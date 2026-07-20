// Profile page: edit nickname/avatar/password, watchlist, watch history.

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
