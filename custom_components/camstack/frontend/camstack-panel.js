/**
 * CamStack iframe panel for Home Assistant.
 * Displays CamStack in a fullscreen iframe.
 * Debug: add ?debug=1 to HA URL to show iframe URL and load status.
 */
const LOG = "[CamStackPanel]";

class CamstackPanel extends HTMLElement {
  constructor() {
    super();
    console.log(LOG, "constructor");
    this.attachShadow({ mode: "open" });
    this._config = null;
    this._loadTimeout = null;
  }

  connectedCallback() {
    console.log(LOG, "connectedCallback");
  }

  set config(c) {
    this._config = c;
    console.log(LOG, "config set", { hasUrl: !!c?.url, url: c?.url, fullConfig: c });
    if (!c?.url) {
      console.warn(LOG, "config missing url, skipping. Config keys:", c ? Object.keys(c) : "null");
      return;
    }
    const url = c.url;
    const showDebug = window.location.search.includes("debug=1");
    console.log(LOG, "creating iframe", url, "showDebug:", showDebug);

    const iframe = document.createElement("iframe");
    iframe.src = url;
    iframe.style.cssText =
      "position:absolute;top:0;left:0;width:100%;height:100%;border:none;";

    const container = document.createElement("div");
    container.style.cssText = "position:relative;width:100%;height:100%;background:#0a0a0a;";
    container.appendChild(iframe);

    if (showDebug) {
      const debug = document.createElement("div");
      debug.style.cssText =
        "position:absolute;top:8px;left:8px;right:8px;padding:8px;background:rgba(0,0,0,0.85);color:#0f0;font-family:monospace;font-size:11px;z-index:9999;border-radius:4px;word-break:break-all;";
      debug.textContent = "CamStack URL: " + url;
      container.appendChild(debug);
    }

    const errorEl = document.createElement("div");
    errorEl.style.cssText =
      "position:absolute;bottom:16px;left:16px;right:16px;padding:12px;background:rgba(180,0,0,0.9);color:#fff;font-size:14px;z-index:9999;border-radius:8px;display:none;";
    errorEl.innerHTML =
      "<strong>CamStack non caricato</strong><br>Verifica l'URL e la connettività. " +
      '<a href="#" style="color:#fff;text-decoration:underline;">Apri in nuova scheda</a>';
    const link = errorEl.querySelector("a");
    link.href = url;
    link.target = "_blank";
    link.rel = "noopener";
    container.appendChild(errorEl);

    let loaded = false;
    iframe.onload = () => {
      loaded = true;
      console.log(LOG, "iframe onload");
      if (this._loadTimeout) clearTimeout(this._loadTimeout);
      this._loadTimeout = null;
    };

    iframe.onerror = (e) => {
      console.error(LOG, "iframe onerror", e);
    };

    this._loadTimeout = setTimeout(() => {
      console.log(LOG, "load timeout fired, loaded:", loaded);
      if (!loaded) {
        console.warn(LOG, "iframe did not load within 12s, showing error");
        errorEl.style.display = "block";
      }
      this._loadTimeout = null;
    }, 12000);

    this.shadowRoot.innerHTML = "";
    this.shadowRoot.appendChild(container);
    console.log(LOG, "iframe appended to shadowRoot");

    setTimeout(() => {
      if (!loaded) {
        console.log(LOG, "2s check: iframe not yet loaded");
      }
    }, 2000);
  }

  get config() {
    return this._config;
  }
}

try {
  customElements.define("camstack-panel", CamstackPanel);
  console.log(LOG, "custom element registered");
} catch (e) {
  console.error(LOG, "failed to register custom element:", e);
}
