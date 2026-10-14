/**
 * Nirogya AI - Unified Health Timeline & Interactive Vitals Charts
 */

class TimelineManager {
  static events = [];
  static activeFilter = "all";

  static init(eventsData) {
    this.events = eventsData;
    this.renderTimeline();
    this.setupFilters();
  }

  static setupFilters() {
    document.querySelectorAll(".filter-btn, .filter-chip").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".filter-btn, .filter-chip").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        this.activeFilter = btn.getAttribute("data-filter");
        this.renderTimeline();
      });
    });
  }

  static renderTimeline() {
    const container = document.getElementById("timeline-tree");
    if (!container) return;

    const filtered = this.events.filter(e => {
      if (this.activeFilter === "all") return true;
      if (this.activeFilter === "lab_report" && e.event_type === "lab_report") return true;
      if (this.activeFilter === "prescription" && e.event_type === "prescription") return true;
      if (this.activeFilter === "hospital" && (e.event_type === "discharge_summary" || e.event_type === "inpatient_admission")) return true;
      return false;
    });

    if (filtered.length === 0) {
      container.innerHTML = `<p style="color: var(--text-secondary); padding: 20px;">No events match the selected filter.</p>`;
      return;
    }

    container.innerHTML = filtered.map(evt => {
      const markerClass = evt.badge_color || "info";
      return `
        <div class="timeline-node" data-doc-key="${evt.document_id || ''}">
          <div class="node-marker ${markerClass}">
            ${this.getMarkerIcon(evt.event_type)}
          </div>
          <div class="node-content-card" onclick="App.loadDocument('${evt.document_id}'); document.querySelector('[data-view=\\'view-overview\\']')?.click();">
            <div class="node-header">
              <span class="node-date">📅 ${evt.event_date}</span>
              <span class="badge badge-${markerClass}">${evt.badge || 'Event'}</span>
            </div>
            <h4 class="node-title">${evt.title}</h4>
            <p class="node-summary">${evt.summary}</p>
          </div>
        </div>
      `;
    }).join("");
  }

  static getMarkerIcon(type) {
    if (type === "prescription") return "💊";
    if (type === "lab_report") return "🧪";
    if (type === "discharge_summary" || type === "inpatient_admission") return "🏥";
    return "📋";
  }
}


class VitalsChartManager {
  static renderCharts(vitalsData) {
    this.renderGlucoseChart(vitalsData.blood_sugar || []);
    this.renderBloodPressureChart(vitalsData.blood_pressure || []);
    this.renderCholesterolChart(vitalsData.cholesterol || []);
  }

  static renderGlucoseChart(data) {
    const wrap = document.getElementById("glucose-chart-svg");
    if (!wrap || data.length === 0) return;

    const width = 500;
    const height = 200;
    const padding = 40;

    // Dates
    const dates = data.map(d => d.date.slice(5)); // e.g. "05-10"
    const fbs = data.map(d => d.fbs);
    const ppbs = data.map(d => d.ppbs);
    const hba1c = data.map(d => d.hba1c);

    const maxVal = 300;
    const minVal = 60;

    const getX = (idx) => padding + (idx * ((width - (padding * 2)) / (data.length - 1)));
    const getY = (val) => height - padding - (((val - minVal) / (maxVal - minVal)) * (height - (padding * 2)));

    // Polyline points
    const fbsPoints = data.map((d, i) => `${getX(i)},${getY(d.fbs)}`).join(" ");
    const ppbsPoints = data.map((d, i) => `${getX(i)},${getY(d.ppbs)}`).join(" ");

    // Normal fasting boundary line (100 mg/dL)
    const normalFbsY = getY(100);

    let dotsHtml = "";
    data.forEach((d, i) => {
      dotsHtml += `
        <circle cx="${getX(i)}" cy="${getY(d.fbs)}" r="4.5" fill="#10b981" stroke="#080c14" stroke-width="2">
          <title>Fasting Glucose: ${d.fbs} mg/dL (${d.date})</title>
        </circle>
        <circle cx="${getX(i)}" cy="${getY(d.ppbs)}" r="4.5" fill="#f43f5e" stroke="#080c14" stroke-width="2">
          <title>Post-Prandial: ${d.ppbs} mg/dL | HbA1c: ${d.hba1c}% (${d.date})</title>
        </circle>
        <text x="${getX(i)}" y="${height - 12}" fill="#94a3b8" font-size="11" text-anchor="middle">${dates[i]}</text>
      `;
    });

    wrap.innerHTML = `
      <svg viewBox="0 0 ${width} ${height}" width="100%" height="100%" style="overflow: visible;">
        <!-- Safe Normal Band Line -->
        <line x1="${padding}" y1="${normalFbsY}" x2="${width - padding}" y2="${normalFbsY}" stroke="rgba(16, 185, 129, 0.4)" stroke-dasharray="4" stroke-width="1.5" />
        <text x="${width - padding}" y="${normalFbsY - 4}" fill="#34d399" font-size="9" text-anchor="end">Fasting Target < 100 mg/dL</text>

        <!-- Lines -->
        <polyline fill="none" stroke="#10b981" stroke-width="3" points="${fbsPoints}" stroke-linecap="round" stroke-linejoin="round" />
        <polyline fill="none" stroke="#f43f5e" stroke-width="3" points="${ppbsPoints}" stroke-linecap="round" stroke-linejoin="round" />

        ${dotsHtml}
      </svg>
    `;
  }

  static renderBloodPressureChart(data) {
    const wrap = document.getElementById("bp-chart-svg");
    if (!wrap || data.length === 0) return;

    const width = 500;
    const height = 200;
    const padding = 40;

    const dates = data.map(d => d.date.slice(5));
    const maxVal = 180;
    const minVal = 50;

    const getX = (idx) => padding + (idx * ((width - (padding * 2)) / (data.length - 1)));
    const getY = (val) => height - padding - (((val - minVal) / (maxVal - minVal)) * (height - (padding * 2)));

    const sysPoints = data.map((d, i) => `${getX(i)},${getY(d.systolic)}`).join(" ");
    const diaPoints = data.map((d, i) => `${getX(i)},${getY(d.diastolic)}`).join(" ");

    const targetSysY = getY(120);

    let dotsHtml = "";
    data.forEach((d, i) => {
      dotsHtml += `
        <circle cx="${getX(i)}" cy="${getY(d.systolic)}" r="4.5" fill="#06b6d4" stroke="#080c14" stroke-width="2">
          <title>Systolic BP: ${d.systolic} mmHg (${d.date})</title>
        </circle>
        <circle cx="${getX(i)}" cy="${getY(d.diastolic)}" r="4.5" fill="#3b82f6" stroke="#080c14" stroke-width="2">
          <title>Diastolic BP: ${d.diastolic} mmHg (${d.date})</title>
        </circle>
        <text x="${getX(i)}" y="${height - 12}" fill="#94a3b8" font-size="11" text-anchor="middle">${dates[i]}</text>
      `;
    });

    wrap.innerHTML = `
      <svg viewBox="0 0 ${width} ${height}" width="100%" height="100%" style="overflow: visible;">
        <!-- Target Normal Line (120 mmHg) -->
        <line x1="${padding}" y1="${targetSysY}" x2="${width - padding}" y2="${targetSysY}" stroke="rgba(6, 182, 212, 0.4)" stroke-dasharray="4" stroke-width="1.5" />
        <text x="${width - padding}" y="${targetSysY - 4}" fill="#06b6d4" font-size="9" text-anchor="end">Target Systolic < 120 mmHg</text>

        <polyline fill="none" stroke="#06b6d4" stroke-width="3" points="${sysPoints}" stroke-linecap="round" stroke-linejoin="round" />
        <polyline fill="none" stroke="#3b82f6" stroke-width="3" points="${diaPoints}" stroke-linecap="round" stroke-linejoin="round" />

        ${dotsHtml}
      </svg>
    `;
  }

  static renderCholesterolChart(data) {
    const wrap = document.getElementById("lipid-chart-svg");
    if (!wrap || data.length === 0) return;

    const width = 500;
    const height = 200;
    const padding = 40;

    const dates = data.map(d => d.date.slice(5));
    const maxVal = 260;
    const minVal = 80;

    const getX = (idx) => padding + (idx * ((width - (padding * 2)) / (data.length - 1)));
    const getY = (val) => height - padding - (((val - minVal) / (maxVal - minVal)) * (height - (padding * 2)));

    const totPoints = data.map((d, i) => `${getX(i)},${getY(d.total)}`).join(" ");
    const ldlPoints = data.map((d, i) => `${getX(i)},${getY(d.ldl)}`).join(" ");

    const targetTotY = getY(200);

    let dotsHtml = "";
    data.forEach((d, i) => {
      dotsHtml += `
        <circle cx="${getX(i)}" cy="${getY(d.total)}" r="4.5" fill="#f59e0b" stroke="#080c14" stroke-width="2">
          <title>Total Cholesterol: ${d.total} mg/dL</title>
        </circle>
        <circle cx="${getX(i)}" cy="${getY(d.ldl)}" r="4.5" fill="#f43f5e" stroke="#080c14" stroke-width="2">
          <title>LDL Bad Cholesterol: ${d.ldl} mg/dL</title>
        </circle>
        <text x="${getX(i)}" y="${height - 12}" fill="#94a3b8" font-size="11" text-anchor="middle">${dates[i]}</text>
      `;
    });

    wrap.innerHTML = `
      <svg viewBox="0 0 ${width} ${height}" width="100%" height="100%" style="overflow: visible;">
        <line x1="${padding}" y1="${targetTotY}" x2="${width - padding}" y2="${targetTotY}" stroke="rgba(245, 158, 11, 0.4)" stroke-dasharray="4" stroke-width="1.5" />
        <text x="${width - padding}" y="${targetTotY - 4}" fill="#fbbf24" font-size="9" text-anchor="end">Desirable Total < 200 mg/dL</text>

        <polyline fill="none" stroke="#f59e0b" stroke-width="3" points="${totPoints}" stroke-linecap="round" stroke-linejoin="round" />
        <polyline fill="none" stroke="#f43f5e" stroke-width="3" points="${ldlPoints}" stroke-linecap="round" stroke-linejoin="round" />

        ${dotsHtml}
      </svg>
    `;
  }
}
