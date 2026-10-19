(function () {
  "use strict";

  var KEY = "tempestivo_consent_v1";
  var GA_ID = "G-CVM98Z28DB";
  var AHREFS_KEY = "lyGSHKfclMqAd+NMgva7kg";
  var scriptTag = document.currentScript;
  var wantsAhrefs = !!(scriptTag && scriptTag.getAttribute("data-ahrefs") === "1");
  var stored = null;

  try {
    stored = JSON.parse(localStorage.getItem(KEY) || "null");
  } catch (e) {
    stored = null;
  }

  function hasChoice() {
    return stored && typeof stored.analytics === "boolean";
  }

  function save(analytics) {
    stored = {
      analytics: !!analytics,
      ts: new Date().toISOString(),
      v: 1
    };
    try {
      localStorage.setItem(KEY, JSON.stringify(stored));
    } catch (e) {}
  }

  function loadGa() {
    if (window.__tplGaLoaded) return;
    window.__tplGaLoaded = true;

    window.dataLayer = window.dataLayer || [];
    window.gtag = function () {
      window.dataLayer.push(arguments);
    };
    window.gtag("consent", "default", {
      ad_storage: "denied",
      ad_user_data: "denied",
      ad_personalization: "denied",
      analytics_storage: "granted"
    });
    window.gtag("js", new Date());
    window.gtag("config", GA_ID, { anonymize_ip: true });

    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID;
    document.head.appendChild(s);
  }

  function loadAhrefs() {
    if (!wantsAhrefs || window.__tplAhrefsLoaded || !AHREFS_KEY) return;
    window.__tplAhrefsLoaded = true;
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://analytics.ahrefs.com/analytics.js";
    s.setAttribute("data-key", AHREFS_KEY);
    document.head.appendChild(s);
  }

  function applyConsent() {
    if (!hasChoice()) return;
    if (stored.analytics) {
      loadGa();
      loadAhrefs();
    } else if (window.gtag) {
      window.gtag("consent", "update", {
        analytics_storage: "denied",
        ad_storage: "denied",
        ad_user_data: "denied",
        ad_personalization: "denied"
      });
    }
  }

  function deleteCookie(name) {
    var host = location.hostname;
    var domains = [host, "." + host];
    if (host === "tempestivo.it" || /\.tempestivo\.it$/.test(host)) {
      domains.push("tempestivo.it", ".tempestivo.it");
    }
    domains.forEach(function (d) {
      document.cookie = name + "=; Max-Age=0; path=/; domain=" + d + "; SameSite=Lax";
    });
    document.cookie = name + "=; Max-Age=0; path=/; SameSite=Lax";
  }

  function clearAnalyticsCookies() {
    document.cookie.split(";").forEach(function (c) {
      var name = c.split("=")[0].trim();
      if (/^_ga/i.test(name) || /^_ahrefs/i.test(name)) deleteCookie(name);
    });
  }

  function revokeTracking() {
    clearAnalyticsCookies();
    if (window.gtag) {
      window.gtag("consent", "update", {
        analytics_storage: "denied",
        ad_storage: "denied",
        ad_user_data: "denied",
        ad_personalization: "denied"
      });
    }
    if (window.__tplGaLoaded || window.__tplAhrefsLoaded) {
      window.location.reload();
    }
  }

  var banner = null;
  var panel = null;
  var checkbox = null;

  function buildBanner() {
    if (banner) return;

    banner = document.createElement("div");
    banner.id = "tpl-consent";
    banner.setAttribute("role", "dialog");
    banner.setAttribute("aria-modal", "false");
    banner.setAttribute("aria-labelledby", "tpl-consent-title");
    banner.innerHTML =
      '<div class="tpl-consent-inner">' +
      '<div class="tpl-consent-text">' +
      '<strong id="tpl-consent-title">Cookie e analytics</strong><br>' +
      "Usiamo cookie tecnici necessari e, solo con il tuo consenso, cookie di analisi " +
      "(Google Analytics e Ahrefs) per capire come viene usato il sito. " +
      'Puoi <a href="/cookie.html">leggere la Cookie Policy</a> e modificare la scelta quando vuoi.' +
      "</div>" +
      '<div class="tpl-consent-actions">' +
      '<button type="button" class="tpl-accept">Accetta tutti</button>' +
      '<button type="button" class="tpl-reject">Rifiuta</button>' +
      '<button type="button" class="tpl-prefs" aria-expanded="false">Preferenze</button>' +
      "</div>" +
      '<div class="tpl-panel">' +
      "<label><input type=\"checkbox\" class=\"tpl-analytics\">" +
      "<span><strong>Analytics</strong><br>Google Analytics 4 e Ahrefs: statistiche aggregate su pagine viste e provenienza del traffico. Senza questo consenso non viene caricato alcuno script di analisi.</span></label>" +
      '<button type="button" class="tpl-save">Salva preferenze</button>' +
      '<p class="tpl-note">Puoi revocare il consenso in qualsiasi momento da “Preferenze cookie” nel footer o dalla Cookie Policy.</p>' +
      "</div>" +
      "</div>";
    document.body.appendChild(banner);

    panel = banner.querySelector(".tpl-panel");
    checkbox = banner.querySelector(".tpl-analytics");

    banner.querySelector(".tpl-accept").addEventListener("click", function () {
      save(true);
      applyConsent();
      closeBanner();
    });

    banner.querySelector(".tpl-reject").addEventListener("click", function () {
      var wasGranted = hasChoice() && stored.analytics;
      save(false);
      closeBanner();
      if (wasGranted) revokeTracking();
    });

    banner.querySelector(".tpl-prefs").addEventListener("click", function () {
      var open = panel.classList.toggle("is-open");
      this.setAttribute("aria-expanded", open ? "true" : "false");
    });

    banner.querySelector(".tpl-save").addEventListener("click", function () {
      var wasGranted = hasChoice() && stored.analytics;
      var analytics = !!checkbox.checked;
      save(analytics);
      closeBanner();
      if (analytics) {
        applyConsent();
      } else if (wasGranted) {
        revokeTracking();
      }
    });
  }

  function openBanner(prefs) {
    buildBanner();
    checkbox.checked = hasChoice() ? !!stored.analytics : false;
    panel.classList.toggle("is-open", !!prefs);
    banner.querySelector(".tpl-prefs").setAttribute("aria-expanded", prefs ? "true" : "false");
    banner.hidden = false;
  }

  function closeBanner() {
    if (banner) banner.hidden = true;
  }

  function addFooterLink() {
    if (document.querySelector("[data-consent-open]")) return;
    var footer = document.querySelector("footer");
    if (!footer) return;
    var link = document.createElement("a");
    link.href = "/cookie.html";
    link.setAttribute("data-consent-open", "");
    link.textContent = "Preferenze cookie";
    link.style.cssText = "margin:0 8px;color:inherit;text-decoration:underline;";
    link.addEventListener("click", function (e) {
      e.preventDefault();
      openBanner(true);
    });
    footer.appendChild(document.createTextNode(" · "));
    footer.appendChild(link);
  }

  document.addEventListener("click", function (e) {
    var t = e.target.closest ? e.target.closest("[data-consent-open]") : null;
    if (t) {
      e.preventDefault();
      openBanner(true);
    }
  });

  function init() {
    applyConsent();
    addFooterLink();
    if (!hasChoice()) openBanner(false);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  window.tempestivoConsent = {
    open: function () {
      openBanner(true);
    },
    reset: function () {
      try {
        localStorage.removeItem(KEY);
      } catch (e) {}
      stored = null;
      openBanner(false);
    }
  };
})();
