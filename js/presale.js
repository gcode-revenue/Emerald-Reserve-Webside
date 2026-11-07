// Emerald Reserve — pre-sale access gate
// The viewer is stored encrypted (AES-GCM, key derived from the access code with PBKDF2);
// it can only be decrypted in the browser with the correct code.
(function () {
  "use strict";
  var form = document.getElementById("gate-form");
  if (!form) return;
  var input = document.getElementById("code");
  var msg = document.getElementById("gate-msg");
  var gate = document.getElementById("gate");
  var viewer = document.getElementById("viewer");
  var btn = form.querySelector("button");
  var cache = null;

  function b64(s) { return Uint8Array.from(atob(s), function (c) { return c.charCodeAt(0); }); }

  function load() {
    if (cache) return Promise.resolve(cache);
    return fetch("assets/presale.enc.json", { cache: "no-store" }).then(function (r) {
      if (!r.ok) throw new Error("load");
      return r.json();
    }).then(function (j) { cache = j; return j; });
  }

  function decrypt(code, p) {
    var enc = new TextEncoder();
    return crypto.subtle.importKey("raw", enc.encode(code), "PBKDF2", false, ["deriveKey"]).then(function (km) {
      return crypto.subtle.deriveKey({ name: "PBKDF2", salt: b64(p.salt), iterations: p.iter, hash: "SHA-256" }, km, { name: "AES-GCM", length: 256 }, false, ["decrypt"]);
    }).then(function (key) {
      return crypto.subtle.decrypt({ name: "AES-GCM", iv: b64(p.iv) }, key, b64(p.ct));
    }).then(function (buf) { return new TextDecoder().decode(buf); });
  }

  function show(html) {
    gate.hidden = true;
    viewer.hidden = false;
    viewer.innerHTML = '<div class="viewer-head"><span class="eyebrow">La Pen\u00ednsula \u00b7 10 Lots</span><h2>Your Private Preview</h2><p>Select any lot on the plan to see its photos, lot size, dock details and pricing with financing.</p></div>';
    var holder = document.createElement("div");
    holder.innerHTML = html;
    var scripts = Array.prototype.slice.call(holder.querySelectorAll("script"));
    scripts.forEach(function (s) { s.parentNode.removeChild(s); });
    viewer.appendChild(holder);
    scripts.forEach(function (s) {
      var n = document.createElement("script");
      n.text = s.text;
      viewer.appendChild(n);
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function fail(text) {
    msg.textContent = text;
    gate.classList.remove("shake");
    void gate.offsetWidth;
    gate.classList.add("shake");
    btn.disabled = false;
    btn.textContent = "View the Homes";
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var code = input.value.trim().toLowerCase();
    if (!code) { fail("Please enter your access code."); return; }
    msg.textContent = "";
    btn.disabled = true;
    btn.textContent = "Checking\u2026";
    load().then(function (p) { return decrypt(code, p); }).then(show).catch(function (err) {
      fail(err && err.message === "load" ? "We could not load the preview. Please try again." : "That code is not valid. Please check it and try again.");
    });
  });
})();
