// Profile page: edit nickname/avatar/password, watchlist, watch history.

const DEFAULT_AVATAR = "https://placehold.co/96x96?text=%20";

async function loadProfile() {
  try {
    const user = await Api.getMe();
    document.getElementById("nickname-input").value = user.nickname;
    document.getElementById("avatar-preview").src = user.avatar_url || DEFAULT_AVATAR;
    document.getElementById("email-display").textContent = user.email;
  } catch (err) {
    window.location.href = "login.html";
  }
}

function videoRowHtml(v, extraLabel) {
  return `
    <a class="video-row" href="detail.html?id=${v.video_id}">
      <img src="${v.thumbnail_url || "https://placehold.co/80x50?text=%20"}" alt="" />
      <div>
        <strong>${v.title}</strong>
        <div class="muted">${extraLabel || ""}</div>
      </div>
    </a>
  `;
}

async function loadWatchlist() {
  const box = document.getElementById("watchlist-list");
  try {
    const videos = await Api.listFavorites();
    box.innerHTML = videos.length
      ? videos.map((v) => videoRowHtml(v, `⭐ ${v.avg_rating ?? 0}`)).join("")
      : `<p class="muted">Nothing saved yet.</p>`;
  } catch (err) {
    box.innerHTML = `<p class="error">${err.message}</p>`;
  }
}

async function loadHistory() {
  const box = document.getElementById("history-list");
  try {
    const videos = await Api.listHistory();
    box.innerHTML = videos.length
      ? videos.map((v) => videoRowHtml(v, new Date(v.viewed_at).toLocaleString())).join("")
      : `<p class="muted">No watch history yet.</p>`;
  } catch (err) {
    box.innerHTML = `<p class="error">${err.message}</p>`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  if (!getToken()) {
    window.location.href = "login.html";
    return;
  }

  loadProfile();
  loadWatchlist();
  loadHistory();

  document.getElementById("profile-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const nickname = document.getElementById("nickname-input").value;
    const avatarFile = document.getElementById("avatar-input").files[0];
    const messageEl = document.getElementById("profile-message");
    try {
      let updated = await Api.updateMe(nickname);
      if (avatarFile) {
        updated = await Api.uploadAvatar(avatarFile);
      }
      setStoredUser(updated);
      renderAuthNav();
      document.getElementById("avatar-preview").src = updated.avatar_url || DEFAULT_AVATAR;
      messageEl.textContent = "Saved!";
    } catch (err) {
      messageEl.textContent = err.message;
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
