// Emerald Reserve — site interactions
(function () {
  "use strict";

  var CONTACT_EMAIL = "gcalderin@portillalaw.com";

  var ES = document.documentElement.lang === "es";

  // Slide the header up once the language bar has scrolled away
  var syncBar = function () {
    document.body.classList.toggle("past-bar", window.scrollY > 34);
  };
  window.addEventListener("scroll", syncBar, { passive: true });
  syncBar();

  // Header background on scroll
  var header = document.querySelector(".site-header");
  if (header && !header.classList.contains("solid")) {
    var onScroll = function () {
      header.classList.toggle("scrolled", window.scrollY > 40);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  // Mobile navigation
  var toggle = document.querySelector(".nav-toggle");
  var links = document.querySelector(".nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      var open = links.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    links.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        links.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  // Reveal on scroll
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("visible"); });
  }

  // Gallery lightbox
  var lightbox = document.querySelector(".lightbox");
  if (lightbox) {
    var lbImg = lightbox.querySelector("img");
    var close = function () {
      lightbox.classList.remove("open");
      lbImg.removeAttribute("src");
    };
    document.querySelectorAll("[data-lightbox]").forEach(function (a) {
      a.addEventListener("click", function (e) {
        e.preventDefault();
        lbImg.src = a.getAttribute("href");
        lbImg.alt = (a.querySelector("img") || {}).alt || "";
        lightbox.classList.add("open");
      });
    });
    lightbox.addEventListener("click", function (e) {
      if (e.target !== lbImg) close();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") close();
    });
  }

  // Contact form — opens the visitor's email client with the inquiry pre-filled
  var form = document.getElementById("inquiry-form");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;

      var data = new FormData(form);
      var L = ES
        ? { none: "No especificado", noPhone: "No proporcionado", email: "Correo electrónico", name: "Nombre", phone: "Teléfono",
            pref: "Contacto preferido", interest: "Interesado en", timeline: "Plazo", message: "Mensaje",
            subject: "Consulta de preventa Emerald Reserve — " }
        : { none: "Not specified", noPhone: "Not provided", email: "Email", name: "Name", phone: "Phone",
            pref: "Preferred contact", interest: "Interested in", timeline: "Timeline", message: "Message",
            subject: "Emerald Reserve Pre-Sale Inquiry — " };
      var interests = data.getAll("interest").join(", ") || L.none;
      var name = (data.get("name") || "").trim();
      var lines = [
        L.name + ": " + name,
        L.email + ": " + (data.get("email") || ""),
        L.phone + ": " + (data.get("phone") || L.noPhone),
        L.pref + ": " + (data.get("preferred") || L.email),
        L.interest + ": " + interests,
        L.timeline + ": " + (data.get("timeline") || L.none),
        "",
        L.message + ":",
        data.get("message") || ""
      ];
      var subject = L.subject + name;
      var href = "mailto:" + CONTACT_EMAIL +
        "?subject=" + encodeURIComponent(subject) +
        "&body=" + encodeURIComponent(lines.join("\n"));

      window.location.href = href;

      var status = document.querySelector(".form-status");
      if (status) status.classList.add("show");
    });
  }

  // Current year in footer
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
