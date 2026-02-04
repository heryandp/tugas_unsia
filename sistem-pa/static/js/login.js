(function () {
  var toggle = document.getElementById("password-toggle");
  if (!toggle) return;
  toggle.addEventListener("click", function () {
    var input = document.getElementById("login-password");
    var icon = document.getElementById("toggle-icon");
    if (!input || !icon) return;
    if (input.type === "password") {
      input.type = "text";
      icon.className = "fas fa-eye-slash";
      toggle.setAttribute("aria-label", "Sembunyikan password");
    } else {
      input.type = "password";
      icon.className = "fas fa-eye";
      toggle.setAttribute("aria-label", "Tampilkan password");
    }
  });
})();
