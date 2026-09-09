// Admin shared bootstrap
document.addEventListener("DOMContentLoaded", () => {
  // Auth guard
  if (typeof requireAuth === "function") {
    requireAuth("../login.html");
  } else if (!localStorage.getItem("aurora_token")) {
    location.href = "../login.html";
  }

  // User display
  const user = typeof getUser === "function" ? getUser() : {};
  const name = user.full_name || "Admin User";
  const initials = name.split(" ").map(p => p[0]).join("").slice(0, 2).toUpperCase() || "AD";

  document.querySelectorAll(".avatar").forEach(el => {
    if (!el.querySelector("img")) el.textContent = initials;
  });
  document.querySelectorAll(".admin b, .admin-name").forEach(el => {
    el.textContent = name;
  });
  document.querySelectorAll(".admin .muted, .admin-role").forEach(el => {
    el.textContent = (user.role || "admin").charAt(0).toUpperCase() + (user.role || "admin").slice(1);
  });

  // Mobile menu
  const menuBtn = document.getElementById("menu");
  const sidebar = document.getElementById("sidebar");
  if (menuBtn && sidebar) {
    menuBtn.addEventListener("click", () => sidebar.classList.toggle("open"));
  }

  // Logout links
  document.querySelectorAll('[data-logout], a[href*="login.html"]').forEach(el => {
    if (el.textContent.toLowerCase().includes("logout") || el.dataset.logout !== undefined) {
      el.addEventListener("click", async (e) => {
        e.preventDefault();
        if (typeof logoutUser === "function") await logoutUser();
        else {
          localStorage.removeItem("aurora_token");
          localStorage.removeItem("aurora_user");
          localStorage.removeItem("auroraLogin");
        }
        location.href = "../login.html";
      });
    }
  });
});
