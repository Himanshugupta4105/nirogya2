/**
 * Nirogya AI — ABDM & FHIR R4 Interoperability Controller
 */

class AbdmManager {
  static currentFhirBundle = null;

  static init() {
    this.setupModalEvents();
  }

  static setupModalEvents() {
    const abhaPill = document.getElementById("header-abha-pill");
    const modal    = document.getElementById("abha-modal");
    const closeBtn = document.getElementById("close-abha-modal");
    const genBtn   = document.getElementById("btn-generate-new-abha");

    if (abhaPill && modal) {
      abhaPill.addEventListener("click", () => modal.classList.add("active"));
    }
    if (closeBtn && modal) {
      closeBtn.addEventListener("click", () => modal.classList.remove("active"));
    }
    if (modal) {
      modal.addEventListener("click", (e) => {
        if (e.target === modal) modal.classList.remove("active");
      });
    }

    // Close consent modal on backdrop click
    const consentModal = document.getElementById("consent-modal");
    if (consentModal) {
      consentModal.addEventListener("click", (e) => {
        if (e.target === consentModal) consentModal.classList.remove("active");
      });
    }

    if (genBtn) {
      genBtn.addEventListener("click", () => this.generateNewAbha());
    }
    const genBtnModal = document.getElementById("btn-generate-new-abha-modal");
    if (genBtnModal) {
      genBtnModal.addEventListener("click", () => this.generateNewAbha());
    }
  }

  static async generateNewAbha() {
    try {
      const base = (typeof API_BASE !== 'undefined') ? API_BASE : '';
      const res = await fetch(`${base}/api/abha/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: "Rajesh Kumar Sharma", year_of_birth: 1974 })
      });
      const data = await res.json();

      ["modal-abha-number", "card-abha-number"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = data.abha_number;
      });
      ["modal-abha-address", "card-abha-address"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = data.abha_address;
      });

      App.showToast(`New ABHA linked: ${data.abha_number}`, "success");
    } catch {
      App.showToast("Could not generate ABHA ID", "error");
    }
  }

  static renderFhirViewer(bundle) {
    this.currentFhirBundle = bundle;
    const codeBox = document.getElementById("fhir-code-display");
    if (!codeBox) return;
    codeBox.textContent = bundle ? JSON.stringify(bundle, null, 2) : "// No FHIR R4 bundle loaded";
  }

  static downloadFhirBundle() {
    if (!this.currentFhirBundle) {
      App.showToast("No FHIR bundle available to download", "error");
      return;
    }
    const uri = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(this.currentFhirBundle, null, 2));
    const a   = document.createElement("a");
    a.href = uri;
    a.download = `abdm_fhir_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    App.showToast("FHIR R4 bundle downloaded", "success");
  }

  static async openConsentSimulator() {
    const modal = document.getElementById("consent-modal");
    if (!modal) return;
    modal.classList.add("active");

    // Reset stepper states
    document.getElementById("step-node-1")?.setAttribute("class", "step-node done");
    document.getElementById("step-node-2")?.setAttribute("class", "step-node active");
    document.getElementById("step-node-3")?.setAttribute("class", "step-node");

    const resBox = document.getElementById("consent-result-box");
    if (resBox) resBox.style.display = "none";

    const btn = document.getElementById("btn-approve-consent");
    if (btn) { btn.style.display = ""; btn.textContent = "🔐 Grant Consent"; }
  }

  static async approveConsentHandshake() {
    const btn = document.getElementById("btn-approve-consent");
    if (btn) btn.textContent = "Verifying OTP…";

    try {
      const base = (typeof API_BASE !== 'undefined') ? API_BASE : '';
      const res = await fetch(`${base}/api/abdm/consent-flow`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          hip: "Apollo Hospitals / Metropolis Healthcare",
          purpose: "Chronic Care Monitoring & Glycemic Review"
        })
      });
      const data = await res.json();

      document.getElementById("step-node-2")?.setAttribute("class", "step-node done");
      document.getElementById("step-node-3")?.setAttribute("class", "step-node done");

      const resBox = document.getElementById("consent-result-box");
      if (resBox) {
        resBox.style.display = "block";
        resBox.innerHTML = `
          <div style="background:var(--emerald-dim);border:1px solid var(--border-accent);border-radius:var(--r-md);padding:14px;">
            <div style="color:var(--emerald);font-weight:700;margin-bottom:10px;">✓ Consent Granted & Bridge Established</div>
            <div class="consent-row"><span>Consent ID</span><code class="mono">${data.consent_id}</code></div>
            <div class="consent-row"><span>HIP</span><span>${data.hip}</span></div>
            <div class="consent-row"><span>HIU</span><span>${data.hiu}</span></div>
            <div class="consent-row"><span>Valid Until</span><span>${data.expiry}</span></div>
            <div class="consent-row"><span>Security</span><span>${data.security}</span></div>
            <div class="consent-row"><span>Records Unlocked</span><strong style="color:var(--emerald);">${data.unlocked_records_count} documents</strong></div>
          </div>
        `;
      }
      if (btn) btn.style.display = "none";
    } catch {
      App.showToast("Error simulating consent handshake", "error");
      if (btn) btn.textContent = "🔐 Grant Consent";
    }
  }
}
