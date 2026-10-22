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

  // --------------------------------------------------------------------
  // Contesto pagina + eventi conversione (GA4)
  // Il contesto si ricava dall'URL: nessun attributo da aggiungere a 240
  // pagine e nessun rischio di disallineamento tra HTML e tracciamento.
  // --------------------------------------------------------------------
  // Comuni con pagine ma senza cluster dedicato: servono solo a impedire che
  // una pagina multi-comune venga attribuita a un comune solo.
  var CITTA_EXTRA = ["trapani"];

  var COMUNI = {
    "palermo": "Palermo",
    "carini": "Carini",
    "terrasini": "Terrasini",
    "balestrate": "Balestrate",
    "castellammare-del-golfo": "Castellammare del Golfo",
    "alcamo": "Alcamo",
    "cinisi": "Cinisi",
    "bagheria": "Bagheria",
    "monreale": "Monreale"
  };

  function pageContext() {
    var path = location.pathname.replace(/\/+$/, "") || "/";
    var parts = path.split("/").filter(function (p) { return p; });
    var comune = COMUNI[parts[0]] || "";
    var zona = "";
    var servizio = "non_definito";
    var tipo = "altra";
    var low = path.toLowerCase();

    // Pagine fuori dai cluster comunali (/guasti/, /servizi/, /prezzi/): il
    // comune si ricava dallo slug solo se compare un solo comune, altrimenti
    // resta vuoto (es. /pronto-intervento-palermo-trapani.html e' multi-comune).
    if (!comune) {
      var tokens = low.split(/[^a-z]+/);
      var found = [];
      for (var i = 0; i < tokens.length; i++) {
        if (!tokens[i]) continue;
        if (CITTA_EXTRA.indexOf(tokens[i]) !== -1) {
          found.push(tokens[i]);
          continue;
        }
        for (var slug in COMUNI) {
          if (slug === tokens[i] || slug.indexOf(tokens[i] + "-") === 0) {
            if (found.indexOf(slug) === -1) found.push(slug);
          }
        }
      }
      if (found.length === 1) comune = COMUNI[found[0]] || "";
    }

    if (/\/guasti(\/|$)/.test(low)) tipo = "guasto";
    else if (low.indexOf("caso-studio") !== -1) tipo = "case_study";
    else if (low.indexOf("/prezzi/") !== -1) tipo = "prezzo";
    else if (low.indexOf("/servizi/") !== -1) tipo = "servizio";
    else if (path === "/") tipo = "home";
    else if (comune && parts.length === 1) tipo = "hub_comune";
    else if (comune && parts.length === 2) {
      tipo = /urgent|pronto|h24/.test(parts[1]) ? "pronto_intervento" : "hub_servizio";
    } else if (comune && parts.length >= 3) {
      // Distingue la landing urgenza di zona (pronto_intervento) dalla pagina
      // di servizio della stessa zona, altrimenti in GA4 finiscono insieme.
      tipo = /urgent|pronto|h24/.test(parts[2]) ? "pronto_intervento" : "zona";
      zona = parts[1].replace(/-/g, " ");
    }

    if (comune && parts.length >= 3 && !zona &&
        !/^(elettricista|idraulico|pronto|impianti|ristruttur|guasti|prezzi|servizi)/.test(parts[1])) {
      zona = parts[1].replace(/-/g, " ");
    }

    // Landing fuori dai cluster comunali: senza queste regole finirebbero
    // tutte in page_type "altra" e non sarebbero distinguibili in GA4.
    if (tipo === "altra") {
      if (/\/guasti\//.test(low)) tipo = "guasto";
      else if (/pronto-intervento|pronto_intervento/.test(low)) tipo = "pronto_intervento";
      else if (/landing-ristrutturazioni|soluzioni-business/.test(low)) tipo = "servizio";
      else if (low.indexOf("/prezzi/") !== -1) tipo = "prezzo";
    }

    if (/elettric|salvavita|cortocircuito|manca-la-corrente/.test(low)) servizio = "elettrico";
    else if (/idraul|perdit|autoclave|scarico/.test(low)) servizio = "idrico";
    else if (/ristruttur|bagno|bnb|commerciale|appartament|uffici/.test(low)) servizio = "edilizia";
    else if (/urgent|pronto-intervento|guasti/.test(low)) servizio = "h24";

    return { page_type: tipo, comune: comune, zona: zona, servizio: servizio };
  }

  var CONTEXT = pageContext();

  function ctaPosition(el) {
    if (!el || !el.closest) return "inline";
    if (el.closest("header")) return "header";
    if (el.closest("#tempestivo-sticky-footer") || el.closest(".tempestivo-mobile-cta") ||
        el.closest(".sticky-call-btn") || el.closest("[class*=sticky]")) return "sticky";
    if (el.closest("footer")) return "footer";
    if (el.closest(".hero")) return "hero";
    return "inline";
  }

  function track(name, params) {
    // Nessun invio senza consenso analytics e senza gtag caricato.
    if (!window.__tplGaLoaded || typeof window.gtag !== "function") return;
    var payload = {
      page_type: CONTEXT.page_type,
      comune: CONTEXT.comune || "non_assegnato",
      zona: CONTEXT.zona || "non_assegnata",
      servizio: CONTEXT.servizio
    };
    for (var k in params) {
      if (Object.prototype.hasOwnProperty.call(params, k)) payload[k] = params[k];
    }
    payload.transport_type = "beacon";
    window.gtag("event", name, payload);
  }

  function trackClicks() {
    document.addEventListener("click", function (e) {
      var a = e.target && e.target.closest ? e.target.closest("a[href]") : null;
      if (!a) return;
      var href = a.getAttribute("href") || "";
      var pos = ctaPosition(a);

      if (href.indexOf("tel:") === 0) {
        track("tel_click", { cta_position: pos, link_text: (a.textContent || "").trim().slice(0, 60) });
        return;
      }

      if (href.indexOf("wa.me") !== -1 || href.indexOf("whatsapp") !== -1) {
        var text = "";
        try {
          text = new URL(href, location.href).searchParams.get("text") || "";
        } catch (err) {}
        track("wa_click", {
          cta_position: pos,
          wa_has_text: text ? "si" : "no",
          wa_template: text ? text.toLowerCase().replace(/[^a-z ]+/g, " ").trim().slice(0, 80) : "generico"
        });
      }
    }, true);

    document.addEventListener("submit", function (e) {
      var form = e.target;
      if (!form || form.tagName !== "FORM") return;
      track("form_submit", {
        form_id: form.id || "formspree",
        form_destination: (form.getAttribute("action") || "").indexOf("formspree") !== -1 ? "formspree" : "interno"
      });
    }, true);
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
    trackClicks();
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
