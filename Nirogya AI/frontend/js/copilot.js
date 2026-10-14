/**
 * Nirogya AI — Conversational Copilot Controller
 */

class CopilotManager {
  static isOpen = false;
  static currentDocId = "sample_lab_report";

  static init() {
    this.setupEventListeners();
    this.setupVoiceInput();
  }

  static toggleDrawer() {
    const drawer = document.getElementById("copilot-drawer");
    if (!drawer) return;
    this.isOpen = !this.isOpen;
    if (this.isOpen) {
      drawer.classList.add("open");
      document.getElementById("copilot-input")?.focus();
    } else {
      drawer.classList.remove("open");
    }
  }

  static setupEventListeners() {
    document.getElementById("copilot-fab-btn")?.addEventListener("click", () => this.toggleDrawer());
    document.getElementById("copilot-close-btn")?.addEventListener("click", () => this.toggleDrawer());
    document.getElementById("copilot-send-btn")?.addEventListener("click", () => this.handleSendMessage());

    document.getElementById("copilot-input")?.addEventListener("keydown", (e) => {
      if (e.key === "Enter") { e.preventDefault(); this.handleSendMessage(); }
    });

    // Quick prompt chips
    document.querySelectorAll(".chip").forEach(chip => {
      chip.addEventListener("click", () => {
        const input = document.getElementById("copilot-input");
        if (input) {
          input.value = chip.getAttribute("data-prompt") || chip.textContent;
          if (!this.isOpen) this.toggleDrawer();
          this.handleSendMessage();
        }
      });
    });
  }

  static setupVoiceInput() {
    const micBtn = document.getElementById("copilot-mic-btn");
    const input  = document.getElementById("copilot-input");
    if (!micBtn || !input) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      micBtn.title = "Voice input not supported in this browser.";
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;

    micBtn.addEventListener("click", () => {
      const lang = I18nManager.currentLanguage || "en";
      recognition.lang = lang === "hi" ? "hi-IN" : "en-IN";

      if (micBtn.classList.contains("recording")) {
        recognition.stop();
        micBtn.classList.remove("recording");
      } else {
        try {
          recognition.start();
          micBtn.classList.add("recording");
          micBtn.title = "Listening… speak now";
        } catch (e) { console.warn("Voice error:", e); }
      }
    });

    recognition.onresult = (e) => {
      input.value = e.results[0][0].transcript;
      micBtn.classList.remove("recording");
      this.handleSendMessage();
    };
    recognition.onerror = recognition.onend = () => micBtn.classList.remove("recording");
  }

  static async handleSendMessage() {
    const input    = document.getElementById("copilot-input");
    const chatArea = document.getElementById("copilot-chat-area");
    if (!input || !chatArea) return;

    const message = input.value.trim();
    if (!message) return;

    this.appendMessage(message, "user");
    input.value = "";

    // Typing indicator
    const loadingId = "typing-" + Date.now();
    const typingEl  = document.createElement("div");
    typingEl.id = loadingId;
    typingEl.className = "chat-bubble bot";
    typingEl.innerHTML = `<em style="color:var(--text-3);">Analyzing your records…</em>`;
    chatArea.appendChild(typingEl);
    chatArea.scrollTop = chatArea.scrollHeight;

    try {
      const base = (typeof API_BASE !== 'undefined') ? API_BASE : '';
      const patientId = (typeof App !== 'undefined' && App.currentPatientId) ? App.currentPatientId : 'pat-101';
      const res = await fetch(`${base}/api/copilot/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message,
          patient_id: patientId,
          doc_id: this.currentDocId,
          language: I18nManager.currentLanguage || "en"
        })
      });
      const data = await res.json();
      document.getElementById(loadingId)?.remove();

      let html = this.formatMarkdown(data.reply || "");
      const metaItems = [];
      if (data.engine) metaItems.push(`⚡ ${data.engine}`);
      if (data.citations?.length) metaItems.push(...data.citations);
      if (metaItems.length) {
        html += `<div style="margin-top:8px;font-size:0.72rem;color:var(--cyan);opacity:0.9;">${metaItems.join(" · ")}</div>`;
      }

      this.appendMessage(html, "bot", true, data.reply);
    } catch {
      document.getElementById(loadingId)?.remove();
      this.appendMessage("Could not connect to the health intelligence server. Please make sure the backend is running.", "bot");
    }
  }

  static appendMessage(content, sender, isHtml = false, rawText = "") {
    const chatArea = document.getElementById("copilot-chat-area");
    if (!chatArea) return;

    const bubble = document.createElement("div");
    bubble.className = `chat-bubble ${sender}`;

    if (isHtml) {
      bubble.innerHTML = content;
      if (sender === "bot" && window.speechSynthesis && rawText) {
        const speakBtn = document.createElement("button");
        speakBtn.style.cssText = "margin-top:8px;background:none;border:1px solid var(--border);border-radius:var(--r-full);padding:3px 10px;font-size:0.72rem;color:var(--text-3);cursor:pointer;";
        speakBtn.textContent = "🔊 Listen";
        speakBtn.onclick = () => this.speakText(rawText);
        bubble.appendChild(speakBtn);
      }
    } else {
      bubble.textContent = content;
    }

    chatArea.appendChild(bubble);
    chatArea.scrollTop = chatArea.scrollHeight;
  }

  static speakText(text) {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(text.replace(/[*#_~]/g, ''));
    const lang = I18nManager.currentLanguage || "en";
    utter.lang = lang === "hi" ? "hi-IN" : "en-IN";
    utter.rate = 0.95;
    window.speechSynthesis.speak(utter);
  }

  static formatMarkdown(text) {
    if (!text) return "";
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n\n/g, '<br><br>')
      .replace(/\n/g, '<br>');
  }
}
