(function () {
  function toggleSpinner(elt, on) {
    if (!elt) return;
    var label = elt.getAttribute("data-loading-label") || "Memproses...";
    if (on) {
      if (!elt.getAttribute("data-original-html")) {
        elt.setAttribute("data-original-html", elt.innerHTML);
      }
      elt.disabled = true;
      elt.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>' + label;
    } else {
      var original = elt.getAttribute("data-original-html");
      if (original) {
        elt.innerHTML = original;
      }
      elt.disabled = false;
    }
  }

  function showToast(level, message) {
    var container = document.getElementById("toast-container");
    if (!container) return;
    var bg = level === "success" ? "success" : level === "error" ? "danger" : level === "warning" ? "warning" : "info";
    var wrap = document.createElement("div");
    wrap.className = "toast align-items-center text-bg-" + bg + " border-0 mb-2";
    wrap.setAttribute("role", "alert");
    wrap.setAttribute("aria-live", "assertive");
    wrap.setAttribute("aria-atomic", "true");
    wrap.setAttribute("data-bs-delay", "4000");
    wrap.innerHTML = '<div class="d-flex"><div class="toast-body"></div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button></div>';
    wrap.querySelector(".toast-body").textContent = message;
    container.appendChild(wrap);
    var t = new bootstrap.Toast(wrap);
    t.show();
  }

  function applyBodyClass(root) {
    // Priority: #htmx-meta, then any element with [data-body-class]
    var el = root.querySelector("#htmx-meta") || root.querySelector("[data-body-class]");
    if (!el) return;

    var val = el.getAttribute("data-body-class");
    if (val !== null) {
      document.body.className = val;
    }
  }

  function applyBodyStyle(root) {
    var body = document.body;
    var el = root.querySelector("#htmx-meta") || root.querySelector("[data-body-style]");
    if (!el) return;

    var val = el.getAttribute("data-body-style");
    if (val !== null) {
      // If we have specific new styles, we should apply them
      // We overwrite existing styles if it's a "body-style" because usually it's used for page-specific backgrounds
      body.style.cssText = val;
    }
  }

  function scrollToHash() {
    if (!location.hash) {
      return;
    }
    var target = document.querySelector(location.hash);
    if (target) {
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("#toast-container .toast").forEach(function (el) {
      var t = new bootstrap.Toast(el);
      t.show();
    });
    applyBodyClass(document);
    applyBodyStyle(document);
    scrollToHash();
  });

  document.addEventListener("htmx:afterSwap", function (evt) {
    // Hanya proses jika ini adalah HTMX swap, bukan full page reload
    if (evt.detail && evt.detail.requestConfig) {
      if (evt.detail.target && evt.detail.target.id === "app") {
        applyBodyClass(evt.detail.target);
        applyBodyStyle(evt.detail.target);
        scrollToHash();
      }
    }
  });

  document.body.addEventListener("htmx:beforeRequest", function (evt) {
    var trigger = evt.detail && evt.detail.elt;
    if (!trigger) return;
    if (trigger.tagName === "FORM") {
      var submitBtn = trigger.querySelector("button[type='submit']");
      toggleSpinner(submitBtn, true);
    } else if (trigger.tagName === "BUTTON") {
      toggleSpinner(trigger, true);
    } else if (trigger.tagName === "A") {
      trigger.setAttribute("data-hx-busy", "1");
      trigger.classList.add("disabled");
      trigger.style.pointerEvents = "none";
      trigger.setAttribute("aria-busy", "true");
    }
  });

  document.body.addEventListener("htmx:afterRequest", function (evt) {
    var trigger = evt.detail && evt.detail.elt;
    if (!trigger) return;
    if (trigger.tagName === "FORM") {
      var submitBtn = trigger.querySelector("button[type='submit']");
      toggleSpinner(submitBtn, false);
    } else if (trigger.tagName === "BUTTON") {
      toggleSpinner(trigger, false);
    } else if (trigger.tagName === "A") {
      trigger.removeAttribute("data-hx-busy");
      trigger.classList.remove("disabled");
      trigger.style.pointerEvents = "";
      trigger.removeAttribute("aria-busy");
    }
  });

  document.body.addEventListener("htmx:wsAfterSend", function (evt) {
    var form = evt.detail && evt.detail.elt;
    if (form && form.matches("#chat-form")) {
      form.reset();
    }
  });

  document.body.addEventListener("toast", function (evt) {
    if (!evt.detail) return;
    showToast(evt.detail.level || "info", evt.detail.message || "");
  });

  document.body.addEventListener('htmx:configRequest', function (evt) {
    var csrfToken = document.querySelector("meta[name='csrf-token']").getAttribute("content");
    evt.detail.headers['X-CSRFToken'] = csrfToken;
  });

  // Handle closeModal event from server
  document.body.addEventListener('closeModal', function (evt) {
    const modalId = evt.detail.value || '#editModal'; // Default or from event
    const modalEl = document.querySelector(modalId);
    if (modalEl) {
      const modal = bootstrap.Modal.getInstance(modalEl);
      if (modal) {
        modal.hide();
      } else {
        // Should not happen if correctly initialized, but fallback:
        const m = new bootstrap.Modal(modalEl);
        m.hide();
      }
    }
  });

  // Chat auto-scroll on new message via WS
  document.body.addEventListener('htmx:wsAfterMessage', function (evt) {
    const chatBox = document.getElementById("chat-box");
    if (chatBox) {
      // Smooth scroll to bottom
      setTimeout(() => {
        chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
      }, 100);
    }
  });
})();
