// Sprint 1 subset: edit nickname/avatar/password only.
// Watchlist + Watch History are wired up once the Videos/Favorites/History
// endpoints exist (later sprint) — see the full project's profile.js.

async function loadProfile() {
  try {
    const user = await Api.getMe();
    document.getElementById("nickname-input").value = user.nickname;
    document.getElementById("avatar-input").value = user.avatar_url || "";
    document.getElementById("email-display").textContent = user.email;
  } catch (err) {
    window.location.href = "login.html";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  if (!getToken()) {
    window.location.href = "login.html";
    return;
  }

  loadProfile();

  document.getElementById("profile-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const nickname = document.getElementById("nickname-input").value;
    const avatar_url = document.getElementById("avatar-input").value;
    try {
      const updated = await Api.updateMe(nickname, avatar_url);
      setStoredUser(updated);
      renderAuthNav();
      document.getElementById("profile-message").textContent = "Saved!";
    } catch (err) {
      document.getElementById("profile-message").textContent = err.message;
    }
  });

  document.getElementById("password-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const old_password = document.getElementById("old-password-input").value;
    const new_password = document.getElementById("new-password-input").value;
    try {
      await Api.changePassword(old_password, new_password);
      document.getElementById("password-message").textContent = "Password updated!";
      e.target.reset();
    } catch (err) {
      document.getElementById("password-message").textContent = err.message;
    }
  });
});
