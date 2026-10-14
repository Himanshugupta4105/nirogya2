/**
 * Nirogya AI — Application Controller
 * Manages multi-patient state, real-time manual record entry,
 * file upload ingestion, live Google Gemini settings, and dynamic tab rendering
 */

class App {
  static currentPatientId = "pat-101";
  static patients = [];
  static currentDocId = "sample_lab_report";
  static currentDocumentData = null;
  static currentSummaryData = null;
  static patientProfile = null;
  static timelineData = null;
  static vitalsData = null;
  static medicationsData = null;

  static async init() {
    this.setupNavigation();
    this.setupLanguageSelector();
    this.setupDropzone();
    this.setupSampleButtons();
    this.setupPatientSwitcher();
    this.setupManualEntryModal();
    this.setupAiSettingsModal();

    CopilotManager.init();
    AbdmManager.init();

    await this.loadPatients();
    await this.loadPatientData(this.currentPatientId);
    this.checkAiStatus();
  }

  static getBaseUrl() {
    return (typeof API_BASE !== 'undefined') ? API_BASE : '';
  }

  // ─── MULTI-PATIENT PROFILE MANAGEMENT ───────────────────────────────────────

  static async loadPatients() {
    try {
      const base = this.getBaseUrl();
      const res = await fetch(`${base}/api/patients`);
      if (res.ok) {
        this.patients = await res.json();
        this.renderPatientDropdown(this.patients);
      }
    } catch (e) {
      console.warn("Could not load patient list:", e);
    }
  }

  static renderPatientDropdown(patients) {
    const select = document.getElementById("patient-select-dropdown");
    if (!select) return;

    if (!patients || patients.length === 0) {
      select.innerHTML = `<option value="">No patients found</option>`;
      return;
    }

    select.innerHTML = patients.map(p => {
      const isSelected = p.id === this.currentPatientId ? 'selected' : '';
      return `<option value="${p.id}" ${isSelected}>${p.name} (${p.age}Y • ${p.gender === 'Female' ? 'F' : 'M'})</option>`;
    }).join("");

    select.value = this.currentPatientId;
  }

  static setupPatientSwitcher() {
    const select = document.getElementById("patient-select-dropdown");
    const addBtn = document.getElementById("btn-open-add-patient");

    if (select) {
      select.addEventListener("change", (e) => {
        const patientId = e.target.value;
        if (patientId && patientId !== this.currentPatientId) {
          this.switchPatient(patientId);
        }
      });
    }

    if (addBtn) {
      addBtn.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        document.getElementById("add-patient-modal")?.classList.add("active");
      });
    }
  }

  static async switchPatient(patientId) {
    this.currentPatientId = patientId;
    const select = document.getElementById("patient-select-dropdown");
    if (select && select.value !== patientId) {
      select.value = patientId;
    }

    App.showToast("Loading patient medical records…", "info");
    await this.loadPatientData(patientId);
    this.renderPatientDropdown(this.patients);
  }

  static async handleCreatePatient() {
    const name = document.getElementById("pat-form-name")?.value.trim();
    const age = parseInt(document.getElementById("pat-form-age")?.value);
    const gender = document.getElementById("pat-form-gender")?.value;
    const blood_group = document.getElementById("pat-form-blood")?.value;
    const phone = document.getElementById("pat-form-phone")?.value.trim();
    const condition_summary = document.getElementById("pat-form-conditions")?.value.trim();

    if (!name || isNaN(age)) {
      App.showToast("Please fill in valid name and age", "error");
      return;
    }

    try {
      const base = this.getBaseUrl();
      const res = await fetch(`${base}/api/patients`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, age, gender, blood_group, phone, condition_summary })
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.detail || "Registration failed");

      document.getElementById("add-patient-modal")?.classList.remove("active");
      document.getElementById("form-add-patient")?.reset();

      App.showToast(`Patient ${name} registered with ABHA: ${data.patient.abha_number}`, "success");

      await this.loadPatients();
      await this.switchPatient(data.patient.id);

    } catch (err) {
      App.showToast("Error creating patient: " + err.message, "error");
    }
  }

  // ─── PATIENT DATA LOADING ───────────────────────────────────────────────────

  static async loadPatientData(patientId) {
    try {
      const base = this.getBaseUrl();
      const [profRes, timeRes, vitalsRes, medsRes, docsRes] = await Promise.all([
        fetch(`${base}/api/profile?patient_id=${patientId}`),
        fetch(`${base}/api/timeline?patient_id=${patientId}`),
        fetch(`${base}/api/vitals?patient_id=${patientId}`),
        fetch(`${base}/api/medications?patient_id=${patientId}`),
        fetch(`${base}/api/documents?patient_id=${patientId}`)
      ]);

      if (profRes.ok) {
        this.patientProfile = await profRes.json();
        this.updatePatientHeader(this.patientProfile);
      }

      if (timeRes.ok) {
        this.timelineData = await timeRes.json();
        TimelineManager.init(this.timelineData);
      }

      if (vitalsRes.ok) {
        this.vitalsData = await vitalsRes.json();
        VitalsChartManager.renderCharts(this.vitalsData);
      }

      if (medsRes.ok) {
        this.medicationsData = await medsRes.json();
        this.renderMedicationsTab(this.medicationsData);
      }

      // Load first available document for this patient
      let targetDocId = "sample_lab_report";
      if (docsRes.ok) {
        const docs = await docsRes.json();
        if (docs && docs.length > 0) {
          targetDocId = docs[0].id;
        }
      }

      await this.loadDocument(targetDocId);

    } catch (e) {
      console.error("Error loading patient data:", e);
      App.showToast("Failed to connect to health database", "error");
    }
  }

  static updatePatientHeader(profile) {
    if (!profile) return;
    const subEl  = document.getElementById("header-patient-sub");
    const abhaPill = document.getElementById("header-abha-pill");
    const initials = document.getElementById("patient-avatar-initials");
    const select = document.getElementById("patient-select-dropdown");

    if (select && profile.id) select.value = profile.id;
    if (subEl) subEl.textContent = `${profile.age || 40} Y • ${profile.gender || 'Patient'} • ${profile.blood_group || 'B+'}`;
    if (abhaPill) abhaPill.innerHTML = `<span class="abha-dot"></span><span>ABHA Linked</span>`;

    if (initials && profile.name) {
      const parts = profile.name.trim().split(" ");
      initials.textContent = (parts[0][0] + (parts[1]?.[0] || "")).toUpperCase();
    }

    const modalName = document.getElementById("modal-patient-name");
    if (modalName && profile.name) modalName.textContent = profile.name;

    const abhaNumEl = document.getElementById("card-abha-number");
    if (abhaNumEl && profile.abha_number) abhaNumEl.textContent = profile.abha_number;

    const abhaAddrEl = document.getElementById("card-abha-address");
    if (abhaAddrEl && profile.abha_address) abhaAddrEl.textContent = profile.abha_address;

    const modalAbhaNum = document.getElementById("modal-abha-number");
    if (modalAbhaNum && profile.abha_number) modalAbhaNum.textContent = profile.abha_number;

    const modalAbhaAddr = document.getElementById("modal-abha-address");
    if (modalAbhaAddr && profile.abha_address) modalAbhaAddr.textContent = profile.abha_address;
  }

  // ─── NAVIGATION (TABS SWITCHING) ───────────────────────────────────────────

  static setupNavigation() {
    const navItems = document.querySelectorAll(".nav-item");
    navItems.forEach(btn => {
      btn.addEventListener("click", () => {
        const targetId = btn.getAttribute("data-view");
        App.switchView(targetId);
      });
    });
  }

  static switchView(viewId) {
    document.querySelectorAll(".nav-item").forEach(b => {
      if (b.getAttribute("data-view") === viewId) b.classList.add("active");
      else b.classList.remove("active");
    });

    document.querySelectorAll(".view-panel").forEach(p => p.classList.remove("active"));

    const targetPanel = document.getElementById(viewId);
    if (targetPanel) {
      targetPanel.classList.add("active");

      if (viewId === "view-vitals" && this.vitalsData) {
        VitalsChartManager.renderCharts(this.vitalsData);
      } else if (viewId === "view-timeline" && this.timelineData) {
        TimelineManager.renderTimeline();
      } else if (viewId === "view-medications" && this.medicationsData) {
        this.renderMedicationsTab(this.medicationsData);
      } else if (viewId === "view-fhir" && this.currentDocumentData?.fhir_bundle) {
        AbdmManager.renderFhirViewer(this.currentDocumentData.fhir_bundle);
      }
    }
  }

  // ─── LANGUAGE SELECTOR ──────────────────────────────────────────────────────

  static setupLanguageSelector() {
    const sel = document.getElementById("language-selector");
    if (!sel) return;
    sel.addEventListener("change", async (e) => {
      const lang = e.target.value;
      I18nManager.setLanguage(lang);
      App.showToast(`Switched language to ${e.target.options[e.target.selectedIndex].text}`, "info");
      await this.loadDocument(this.currentDocId);
    });
  }

  // ─── FILE UPLOAD & DROPZONE ─────────────────────────────────────────────────

  static setupDropzone() {
    const dropzone  = document.getElementById("file-dropzone");
    const fileInput = document.getElementById("hidden-file-input");
    if (!dropzone || !fileInput) return;

    dropzone.addEventListener("click", () => fileInput.click());

    dropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropzone.classList.add("dragover");
    });
    dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragover"));
    dropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropzone.classList.remove("dragover");
      if (e.dataTransfer.files.length > 0) this.uploadFile(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener("change", (e) => {
      if (e.target.files.length > 0) this.uploadFile(e.target.files[0]);
    });
  }

  static async uploadFile(file) {
    const promptEl = document.getElementById("dropzone-prompt");
    const hintEl   = document.getElementById("dropzone-sub");

    if (promptEl) promptEl.textContent = `Analyzing ${file.name} for ${this.patientProfile?.name || 'Patient'}…`;
    if (hintEl) hintEl.textContent = "Extracting clinical entities, medicines, and biomarker values…";

    const formData = new FormData();
    formData.append("file", file);
    formData.append("patient_id", this.currentPatientId);
    formData.append("lang", I18nManager.currentLanguage || "en");

    try {
      const base = this.getBaseUrl();
      const res = await fetch(`${base}/api/documents/upload`, { method: "POST", body: formData });
      const data = await res.json();
      if (!data.success) throw new Error(data.detail || "Processing failed");

      if (promptEl) promptEl.textContent = "Analysis complete!";
      if (hintEl) hintEl.textContent = "Record indexed in patient timeline.";

      await this.loadDocument(data.doc_id);

      // Refresh timeline & vitals
      const timeRes = await fetch(`${base}/api/timeline?patient_id=${this.currentPatientId}`);
      if (timeRes.ok) {
        this.timelineData = await timeRes.json();
        TimelineManager.init(this.timelineData);
      }

      const vitalsRes = await fetch(`${base}/api/vitals?patient_id=${this.currentPatientId}`);
      if (vitalsRes.ok) {
        this.vitalsData = await vitalsRes.json();
        VitalsChartManager.renderCharts(this.vitalsData);
      }

      const medsRes = await fetch(`${base}/api/medications?patient_id=${this.currentPatientId}`);
      if (medsRes.ok) {
        this.medicationsData = await medsRes.json();
        this.renderMedicationsTab(this.medicationsData);
      }

      this.switchView("view-overview");
      App.showToast("Medical record analyzed and saved to patient file!", "success");

      setTimeout(() => {
        if (promptEl) promptEl.textContent = "Upload a medical record to analyze";
        if (hintEl) hintEl.textContent = "PDF, PNG, JPG, or TXT — prescriptions, lab reports, discharge summaries";
      }, 4000);

    } catch (err) {
      App.showToast("Could not process file: " + err.message, "error");
      if (promptEl) promptEl.textContent = "Upload a medical record to analyze";
      if (hintEl) hintEl.textContent = "PDF, PNG, JPG, or TXT — prescriptions, lab reports, discharge summaries";
    }
  }

  // ─── MANUAL HEALTH RECORD ENTRY MODAL ───────────────────────────────────────

  static setupManualEntryModal() {
    const openBtn = document.getElementById("btn-open-manual-entry");
    const modal   = document.getElementById("manual-record-modal");
    if (openBtn && modal) {
      openBtn.addEventListener("click", () => {
        const dateInput = document.getElementById("man-rec-date");
        if (dateInput && !dateInput.value) {
          dateInput.value = new Date().toISOString().split("T")[0];
        }
        modal.classList.add("active");
      });
    }
  }

  static switchManualTab(tab) {
    const btnValues = document.getElementById("tab-btn-values");
    const btnText   = document.getElementById("tab-btn-text");
    const paneValues = document.getElementById("tab-pane-values");
    const paneText   = document.getElementById("tab-pane-text");

    if (tab === "values") {
      btnValues?.classList.add("active");
      btnText?.classList.remove("active");
      paneValues?.classList.add("active");
      paneText?.classList.remove("active");
    } else {
      btnText?.classList.add("active");
      btnValues?.classList.remove("active");
      paneText?.classList.add("active");
      paneValues?.classList.remove("active");
    }
  }

  static async handleManualRecordSubmit() {
    const title = document.getElementById("man-rec-title")?.value.trim();
    const doc_type = document.getElementById("man-rec-type")?.value || "lab_report";
    const provider = document.getElementById("man-rec-provider")?.value.trim() || "Local Diagnostic Clinic";
    const doc_date = document.getElementById("man-rec-date")?.value || new Date().toISOString().split("T")[0];

    const raw_text = document.getElementById("man-rec-raw-text")?.value.trim();

    // Collect numeric lab values if entered
    const lab_values = {};
    const getVal = (id) => {
      const el = document.getElementById(id);
      return el && el.value !== "" ? parseFloat(el.value) : null;
    };

    const fbs = getVal("val-fbs"); if (fbs !== null) lab_values.fbs = fbs;
    const ppbs = getVal("val-ppbs"); if (ppbs !== null) lab_values.ppbs = ppbs;
    const hba1c = getVal("val-hba1c"); if (hba1c !== null) lab_values.hba1c = hba1c;
    const sys = getVal("val-systolic"); if (sys !== null) lab_values.systolic = sys;
    const dia = getVal("val-diastolic"); if (dia !== null) lab_values.diastolic = dia;
    const creat = getVal("val-creatinine"); if (creat !== null) lab_values.creatinine = creat;
    const chol = getVal("val-cholesterol"); if (chol !== null) lab_values.cholesterol = chol;
    const ldl = getVal("val-ldl"); if (ldl !== null) lab_values.ldl = ldl;
    const tsh = getVal("val-tsh"); if (tsh !== null) lab_values.tsh = tsh;

    if (!title) {
      App.showToast("Please enter a record title", "error");
      return;
    }

    try {
      const base = this.getBaseUrl();
      const res = await fetch(`${base}/api/records/manual-entry`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          patient_id: this.currentPatientId,
          title,
          doc_type,
          provider,
          doc_date,
          raw_text,
          lab_values: Object.keys(lab_values).length ? lab_values : null
        })
      });

      const data = await res.json();
      if (!data.success) throw new Error(data.detail || "Failed to save record");

      document.getElementById("manual-record-modal")?.classList.remove("active");
      document.getElementById("form-manual-record")?.reset();

      App.showToast("Record analyzed and saved to timeline!", "success");

      // Reload patient data and view the newly analyzed record
      await this.loadPatientData(this.currentPatientId);
      await this.loadDocument(data.doc_id);
      this.switchView("view-overview");

    } catch (err) {
      App.showToast("Error recording entry: " + err.message, "error");
    }
  }

  // ─── AI ENGINE & GOOGLE GEMINI SETTINGS ──────────────────────────────────────

  static setupAiSettingsModal() {
    const btn = document.getElementById("btn-open-ai-settings");
    const modal = document.getElementById("ai-settings-modal");
    if (btn && modal) {
      btn.addEventListener("click", () => {
        this.checkAiStatus();
        modal.classList.add("active");
      });
    }
  }

  static async checkAiStatus() {
    try {
      const base = this.getBaseUrl();
      const res = await fetch(`${base}/api/settings/gemini`);
      if (!res.ok) return;
      const data = await res.json();

      const badge = document.getElementById("ai-engine-status-badge");
      const label = document.getElementById("ai-engine-model-label");
      const headerLabel = document.getElementById("header-ai-label");
      const headerPill  = document.getElementById("btn-open-ai-settings");

      if (data.has_key) {
        if (badge) { badge.className = "badge badge-success"; badge.textContent = "Gemini Live Active"; }
        if (label) label.textContent = "Google Gemini 2.5 Flash (Generative AI Active)";
        if (headerLabel) headerLabel.textContent = "Gemini Live";
        if (headerPill) headerPill.classList.add("live");
      } else {
        if (badge) { badge.className = "badge badge-info"; badge.textContent = "Built-in Clinical NLP"; }
        if (label) label.textContent = "Nirogya Rule-Based Clinical Engine";
        if (headerLabel) headerLabel.textContent = "AI Engine";
        if (headerPill) headerPill.classList.remove("live");
      }
    } catch (e) {
      console.warn("Could not check AI engine status:", e);
    }
  }

  static async saveGeminiKey() {
    const key = document.getElementById("gemini-key-input")?.value.trim();
    const resBox = document.getElementById("gemini-test-result");

    if (!key) {
      App.showToast("Please enter a Google Gemini API key", "error");
      return;
    }

    if (resBox) {
      resBox.style.display = "block";
      resBox.style.background = "var(--cyan-dim)";
      resBox.style.color = "var(--cyan)";
      resBox.textContent = "Testing connection with Google Gemini API…";
    }

    try {
      const base = this.getBaseUrl();
      const res = await fetch(`${base}/api/settings/gemini`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: key })
      });
      const data = await res.json();

      if (data.is_valid) {
        if (resBox) {
          resBox.style.background = "var(--emerald-dim)";
          resBox.style.color = "var(--emerald)";
          resBox.textContent = `✓ ${data.message}`;
        }
        App.showToast("Google Gemini API key connected successfully!", "success");
        this.checkAiStatus();
        setTimeout(() => document.getElementById("ai-settings-modal")?.classList.remove("active"), 1200);
      } else {
        if (resBox) {
          resBox.style.background = "var(--rose-dim)";
          resBox.style.color = "var(--rose)";
          resBox.textContent = `⚠️ ${data.message}`;
        }
      }
    } catch (e) {
      if (resBox) {
        resBox.style.background = "var(--rose-dim)";
        resBox.style.color = "var(--rose)";
        resBox.textContent = "Failed to connect to server: " + e.message;
      }
    }
  }

  static async clearGeminiKey() {
    try {
      const base = this.getBaseUrl();
      await fetch(`${base}/api/settings/gemini`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: "" })
      });
      const input = document.getElementById("gemini-key-input");
      if (input) input.value = "";
      const resBox = document.getElementById("gemini-test-result");
      if (resBox) resBox.style.display = "none";

      App.showToast("Gemini key cleared. Operating in built-in mode.", "info");
      this.checkAiStatus();
    } catch (e) {
      App.showToast("Could not clear key: " + e.message, "error");
    }
  }

  // ─── SAMPLE RECORD PRESET BUTTONS ───────────────────────────────────────────

  static setupSampleButtons() {
    document.querySelectorAll(".sample-btn").forEach(btn => {
      btn.addEventListener("click", async () => {
        document.querySelectorAll(".sample-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        const sampleId = btn.getAttribute("data-sample");
        await this.loadDocument(sampleId);
        this.switchView("view-overview");
      });
    });
  }

  // ─── DOCUMENT LOADING & DETAIL RENDERING ───────────────────────────────────

  static async loadDocument(docId) {
    this.currentDocId = docId;
    CopilotManager.currentDocId = docId;

    const narrativeEl = document.getElementById("executive-narrative-text");
    if (narrativeEl) narrativeEl.textContent = "Analyzing clinical report and generating health insights…";

    try {
      const lang = I18nManager.currentLanguage || "en";
      const base = this.getBaseUrl();
      const res  = await fetch(`${base}/api/documents/${docId}?lang=${lang}&patient_id=${this.currentPatientId}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      this.currentDocumentData = data.document;
      this.currentSummaryData  = data.summary;

      this.renderMetrics(data.document, data.summary);
      this.renderExecutiveSummary(data.document, data.summary);
      this.renderAbnormalCards(data.summary?.abnormal_explanations || []);
      this.renderActionChecklist(data.summary?.lifestyle_recommendations || []);
      this.renderBiomarkerDeltas(data.biomarker_deltas || []);
      this.renderDrugInteractions(data.drug_interactions || []);
      this.renderNutritionPlanner(data.nutrition_plan || {});

      if (data.document?.fhir_bundle) {
        AbdmManager.renderFhirViewer(data.document.fhir_bundle);
      }

    } catch (e) {
      console.error("Error loading document:", e);
      if (narrativeEl) narrativeEl.textContent = "Ready to record health data. Upload a file or enter values above.";
    }
  }

  // ─── RENDERING: METRICS STRIP ───────────────────────────────────────────────

  static renderMetrics(doc, summary) {
    const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    set("metric-abnormal-count", (summary && summary.abnormal_count !== undefined) ? summary.abnormal_count : 0);
    set("metric-normal-count",   (summary && summary.normal_count !== undefined) ? summary.normal_count : 0);
    set("metric-doc-date",       (doc && doc.doc_date) ? doc.doc_date : "—");
    set("metric-doc-provider",   (doc && doc.provider) ? doc.provider.split(",")[0] : "—");
  }

  // ─── RENDERING: EXECUTIVE SUMMARY ───────────────────────────────────────────

  static renderExecutiveSummary(doc, summary) {
    const docTypeLabel = (doc?.doc_type || "").replace(/_/g, " ").toUpperCase();
    const tagEl = document.getElementById("banner-doc-tag");
    if (tagEl) tagEl.textContent = docTypeLabel || "HEALTH REPORT";

    const narrativeEl = document.getElementById("executive-narrative-text");
    if (narrativeEl && summary) {
      narrativeEl.textContent = summary.overall_narrative || "Clinical record processed. Review the biomarker breakdown below.";
    }

    const regionalEl = document.getElementById("executive-narrative-regional");
    if (regionalEl) {
      if (summary?.overall_narrative_regional) {
        regionalEl.style.display = "block";
        regionalEl.textContent = summary.overall_narrative_regional;
      } else {
        regionalEl.style.display = "none";
      }
    }
  }

  // ─── RENDERING: ABNORMAL BIOMARKER CARDS ────────────────────────────────────

  static renderAbnormalCards(cards) {
    const container = document.getElementById("abnormal-cards-container");
    if (!container) return;

    if (!cards || cards.length === 0) {
      container.innerHTML = `
        <div style="background:var(--bg-card);border:1px solid var(--border-accent);border-radius:var(--r-md);padding:22px;text-align:center;">
          <div style="font-size:1.4rem;margin-bottom:8px;">✅</div>
          <h4 style="color:var(--emerald);margin-bottom:4px;">All values within normal biological range</h4>
          <p style="font-size:0.82rem;color:var(--text-2);">No critical flags or abnormal results detected in this record.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = cards.map(c => {
      const pct = Math.min(Math.max((parseFloat(c.pct_of_range) || 75), 0), 100);
      const barClass = (c.status === "HIGH" || c.status === "CRITICAL") ? "danger" : (c.status === "LOW" ? "warning" : "");

      const regionalBox = c.plain_meaning_regional ? `
        <div class="regional-card-box">
          <strong>अनुवाद / क्षेत्रीय:</strong> ${c.plain_meaning_regional}
          ${c.why_it_matters_regional ? `<br><span style="font-size:0.75rem;opacity:0.85;">${c.why_it_matters_regional}</span>` : ''}
        </div>
      ` : '';

      return `
        <div class="abnormal-card">
          <div class="abnormal-card-header">
            <div class="card-test-info">
              <h4>${c.test_name}</h4>
              <div class="card-values">
                <span class="card-value-now">${c.current_value}</span>
                <span class="card-value-unit">${c.unit || ''}</span>
                <span class="card-value-ref"> · Ref: ${c.reference_range}</span>
              </div>
            </div>
            <span class="badge ${c.badge_class || (c.status === 'CRITICAL' ? 'badge-danger' : 'badge-warning')}">${c.status}</span>
          </div>

          <div class="range-bar-wrap">
            <div class="range-bar-track">
              <div class="range-bar-fill ${barClass}" style="width:${pct}%;"></div>
              <div class="range-bar-marker" style="left:${pct}%;"></div>
            </div>
            <div class="range-labels">
              <span>Low</span><span>Normal</span><span>High</span>
            </div>
          </div>

          <p class="card-explanation"><strong>What this means:</strong> ${c.plain_meaning}</p>
          ${c.analogy ? `<p class="card-analogy">💡 ${c.analogy}</p>` : ''}
          ${c.why_it_matters ? `<p class="card-why">${c.why_it_matters}</p>` : ''}
          ${c.lifestyle_tip ? `<p class="card-why" style="color:var(--emerald);margin-top:6px;">🥗 ${c.lifestyle_tip}</p>` : ''}

          ${c.doctor_questions && c.doctor_questions.length ? `
            <div style="margin-top:10px;padding:10px;background:var(--indigo-dim);border:1px solid rgba(99,102,241,0.2);border-radius:var(--r-sm);">
              <strong style="font-size:0.78rem;color:var(--text-1);">🩺 Ask your doctor:</strong>
              <ul style="margin-top:5px;padding-left:14px;font-size:0.76rem;color:var(--text-2);">
                ${c.doctor_questions.map(q => `<li style="margin-bottom:3px;">${q}</li>`).join('')}
              </ul>
            </div>
          ` : ''}

          ${regionalBox}
        </div>
      `;
    }).join("");
  }

  // ─── RENDERING: ACTION CHECKLIST ────────────────────────────────────────────

  static renderActionChecklist(checklist) {
    const container = document.getElementById("checklist-container");
    if (!container) return;

    if (!checklist || !checklist.length) {
      container.innerHTML = `<p style="font-size:0.8rem;color:var(--text-3);text-align:center;padding:16px 0;">No specific recommendations for this record.</p>`;
      return;
    }

    container.innerHTML = checklist.map((item, i) => `
      <div class="checklist-item">
        <input type="checkbox" id="chk-${i}" onchange="this.nextElementSibling.classList.toggle('done', this.checked)">
        <label class="checklist-text" for="chk-${i}">
          <strong>${item.title}</strong>${item.action ? ' — ' + item.action : ''}
        </label>
      </div>
    `).join("");
  }

  // ─── RENDERING: BIOMARKER DELTAS ────────────────────────────────────────────

  static renderBiomarkerDeltas(deltas) {
    const grid = document.getElementById("deltas-grid");
    const header = document.getElementById("deltas-section-header");
    if (!grid) return;

    if (!deltas || deltas.length === 0) {
      if (header) header.style.display = "none";
      grid.innerHTML = "";
      return;
    }

    if (header) header.style.display = "block";

    grid.innerHTML = deltas.map(d => {
      const isUp   = d.trajectory === "WORSENING" || d.trajectory === "INCREASING";
      const isDown = d.trajectory === "IMPROVING" || d.trajectory === "DECREASING";
      const arrow  = isUp ? "▲" : isDown ? "▼" : "→";
      const cls    = isUp ? "delta-up" : isDown ? "delta-down" : "delta-flat";

      return `
        <div class="delta-card">
          <div class="delta-label">${d.test_name}</div>
          <div class="delta-value">${d.current_value}</div>
          <div class="delta-change ${cls}">${arrow} ${d.percent_change || ''} <span style="font-weight:400;color:var(--text-3);">${d.trajectory || ''}</span></div>
          <div style="font-size:0.7rem;color:var(--text-3);margin-top:4px;">Baseline: ${d.baseline_value} (${d.baseline_date})</div>
        </div>
      `;
    }).join("");
  }

  // ─── RENDERING: DRUG INTERACTIONS ───────────────────────────────────────────

  static renderDrugInteractions(interactions) {
    const list = document.getElementById("interactions-list");
    if (!list) return;

    if (!interactions || interactions.length === 0) {
      list.innerHTML = `
        <div class="interaction-item severity-low">
          <div class="interaction-icon low">✓</div>
          <div class="interaction-content">
            <h5>No significant drug interactions detected</h5>
            <p>Your current prescribed medications appear compatible. Always consult your physician before altering regimens.</p>
          </div>
        </div>
      `;
      return;
    }

    list.innerHTML = interactions.map(item => {
      const sev = (item.severity || "").toLowerCase();
      const iconMap = { high: "⚠️", medium: "⚡", low: "ℹ️" };
      return `
        <div class="interaction-item severity-${sev}">
          <div class="interaction-icon ${sev}">${iconMap[sev] || "ℹ️"}</div>
          <div class="interaction-content">
            <h5>${item.pair}</h5>
            <p>${item.clinical_detail}</p>
            ${item.action ? `<p style="color:var(--emerald);margin-top:5px;font-size:0.76rem;">🛡 ${item.action}</p>` : ''}
          </div>
        </div>
      `;
    }).join("");
  }

  // ─── RENDERING: NUTRITION PLAN ───────────────────────────────────────────────

  static renderNutritionPlanner(plan) {
    const titleEl  = document.getElementById("nutrition-plan-title");
    const bannerEl = document.getElementById("nutrition-target-banner");
    const mealsEl  = document.getElementById("meals-timeline");
    const superEl  = document.getElementById("superfoods-list");
    const avoidEl  = document.getElementById("avoid-list");

    if (!plan || !mealsEl) return;

    if (titleEl) titleEl.textContent = plan.title || "Diet Recommendations";

    if (bannerEl) {
      bannerEl.innerHTML = `
        <div class="nutrition-target-label">
          <span class="nutrition-tag">🎯 Goal</span>
          <span>${plan.daily_target || ''}</span>
          ${plan.clinical_rationale ? `<span style="color:var(--text-3);">· ${plan.clinical_rationale}</span>` : ''}
        </div>
      `;
    }

    if (mealsEl) {
      mealsEl.innerHTML = (plan.meals || []).map(m => `
        <div class="meal-card">
          <div class="meal-time">${m.slot}</div>
          <div class="meal-title">${m.recommendation}</div>
          <div class="meal-desc">${m.benefits}</div>
        </div>
      `).join("");
    }

    if (superEl && plan.superfoods) {
      superEl.innerHTML = plan.superfoods.map(s => `<li><strong>${s.name}:</strong> ${s.role}</li>`).join("");
    }

    if (avoidEl && plan.strict_avoid) {
      avoidEl.innerHTML = plan.strict_avoid.map(a => `<li>${a}</li>`).join("");
    }
  }

  // ─── RENDERING: MEDICATIONS TAB ─────────────────────────────────────────────

  static renderMedicationsTab(meds) {
    const morningList   = document.getElementById("slot-morning-list");
    const afternoonList = document.getElementById("slot-afternoon-list");
    const nightList     = document.getElementById("slot-night-list");

    if (!morningList || !nightList) return;

    if (!Array.isArray(meds) || meds.length === 0) {
      morningList.innerHTML = `<p class="no-meds-note">No active medications recorded for this patient.</p>`;
      if (afternoonList) afternoonList.innerHTML = `<p class="no-meds-note">No active medications recorded.</p>`;
      nightList.innerHTML = `<p class="no-meds-note">No active medications recorded.</p>`;
      return;
    }

    const seen = new Set();
    const uniqueMeds = [];
    meds.forEach(m => {
      const cleanKey = (m.name || "").split("(")[0].trim().toLowerCase();
      if (!seen.has(cleanKey)) {
        seen.add(cleanKey);
        uniqueMeds.push(m);
      }
    });

    const renderMedItem = (m) => `
      <div class="med-item">
        <div>
          <div class="med-name">${m.name}</div>
          ${m.generic ? `<div class="med-class">${m.generic}</div>` : ''}
          <div class="med-dosage">${m.frequency || m.dosage || ''}</div>
          ${m.purpose ? `<div style="font-size:0.73rem;color:var(--text-3);margin-top:3px;">🎯 ${m.purpose}</div>` : ''}
        </div>
        <div class="med-timing">${m.timing || 'With meals'}</div>
      </div>
    `;

    const morningMeds = [];
    const afternoonMeds = [];
    const nightMeds = [];

    uniqueMeds.forEach(m => {
      const freq = (m.frequency || "").toLowerCase();
      const timing = (m.timing || "").toLowerCase();

      const hasMorning = freq.includes("1 - ") || freq.includes("1-") || timing.includes("morning") || timing.includes("breakfast") || freq.includes("od") || freq.includes("twice") || timing.includes("empty stomach");
      const hasNight   = freq.includes("- 1") || freq.includes("-1") || timing.includes("night") || timing.includes("bedtime") || freq.includes("twice");
      const hasAfternoon = freq.includes("- 1 -") || timing.includes("lunch") || timing.includes("afternoon") || freq.includes("tid");

      if (hasMorning) morningMeds.push(m);
      if (hasAfternoon) afternoonMeds.push(m);
      if (hasNight) nightMeds.push(m);

      if (!hasMorning && !hasAfternoon && !hasNight) {
        morningMeds.push(m);
      }
    });

    morningList.innerHTML = morningMeds.length
      ? morningMeds.map(renderMedItem).join("")
      : `<p class="no-meds-note">No morning medications scheduled.</p>`;

    if (afternoonList) {
      afternoonList.innerHTML = afternoonMeds.length
        ? afternoonMeds.map(renderMedItem).join("")
        : `<p class="no-meds-note">No afternoon medications scheduled.</p>`;
    }

    nightList.innerHTML = nightMeds.length
      ? nightMeds.map(renderMedItem).join("")
      : `<p class="no-meds-note">No night medications scheduled.</p>`;
  }

  // ─── TOAST HELPER ───────────────────────────────────────────────────────────

  static showToast(message, type = "info") {
    let toast = document.getElementById("app-toast");
    if (!toast) {
      toast = document.createElement("div");
      toast.id = "app-toast";
      toast.className = "toast";
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.className = `toast ${type}`;
    requestAnimationFrame(() => {
      toast.classList.add("show");
      setTimeout(() => toast.classList.remove("show"), 3200);
    });
  }
}

// ─── INIT APPLICATION ─────────────────────────────────────────────────────────

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => App.init());
} else {
  App.init();
}
