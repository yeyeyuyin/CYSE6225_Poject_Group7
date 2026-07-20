// Shared header/nav auth state logic. Included on every page.

function renderAuthNav() {
  const nav = document.getElementById("auth-nav");
  if (!nav) return;
  const user = getStoredUser();

  if (user) {
    nav.innerHTML = `
      <span class="nav-user">Hi, ${user.nickname}</span>
      <a href="profile.html">Profile</a>
      <a href="#" id="logout-link">Log out</a>
    `;
    document.getElementById("logout-link").addEventListener("click", (e) => {
      e.preventDefault();
      clearToken();
      window.location.href = "index.html";
    });
  } else {
    nav.innerHTML = `<a href="login.html">Log in / Register</a>`;
  }
}

document.addEventListener("DOMContentLoaded", renderAuthNav);
