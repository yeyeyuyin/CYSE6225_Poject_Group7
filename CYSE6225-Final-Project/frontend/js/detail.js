// Video detail page: player, multi-source switching, rating, click tracking,
// comments, favorite toggle, broken-link reporting.

function getVideoIdFromUrl() {
  return new URLSearchParams(window.location.search).get("id");
}

function embedUrlFor(rawUrl) {
  // Very small helper to turn a plain YouTube/Vimeo watch URL into an
  // embeddable iframe URL. Extend this as needed for other sources.
  try {
    const url = new URL(rawUrl);
    if (url.hostname.includes("youtube.com") && url.searchParams.get("v")) {
      return `https://www.youtube.com/embed/${url.searchParams.get("v")}`;
    }
    if (url.hostname === "youtu.be") {
      return `https://www.youtube.com/embed/${url.pathname.slice(1)}`;
    }
    if (url.hostname.includes("vimeo.com")) {
      const id = url.pathname.split("/").filter(Boolean).pop();
      return `https://player.vimeo.com/video/${id}`;
    }
  } catch (_) {
    /* not a valid URL, fall through */
  }
  return rawUrl; // fall back to raw URL in the iframe
}

let currentVideo = null;

async function loadVideo() {
  const videoId = getVideoIdFromUrl();
  if (!videoId) {
    document.getElementById("detail-root").innerHTML = `<p class="error">No video specified.</p>`;
    return;
  }

  try {
    currentVideo = await Api.getVideo(videoId);
  } catch (err) {
    document.getElementById("detail-root").innerHTML = `<p class="error">${err.message}</p>`;
    return;
  }

  renderVideo();
  loadComments();
}

function renderVideo() {
  const v = currentVideo;
  document.getElementById("video-title").textContent = v.title;
  document.getElementById("video-description").textContent = v.description || "";
  document.getElementById("video-rating").textContent = `⭐ ${v.avg_rating ?? 0} (${v.rating_count ?? 0} ratings)`;
  document.getElementById("video-clicks").textContent = `▶ ${v.click_count ?? 0} plays`;

  renderSourceButtons();
  renderTags(v.tags || []);

  const favBtn = document.getElementById("favorite-btn");
  favBtn.textContent = v.is_favorite ? "★ In Watchlist" : "☆ Add to Watchlist";
  favBtn.classList.toggle("active", !!v.is_favorite);
}

function renderTags(tags) {
  document.getElementById("video-tags").innerHTML = tags
    .map((t) => `<span class="tag-pill">${t}</span>`)
    .join("");
}

function renderSourceButtons() {
  const sources = currentVideo.sources && currentVideo.sources.length
    ? currentVideo.sources
    : [{ name: "Default Source", url: "" }];

  const bar = document.getElementById("source-bar");
  bar.innerHTML = sources
    .map((s, i) => `<button class="source-btn ${i === 0 ? "active" : ""}" data-index="${i}">${s.name}</button>`)
    .join("");

  bar.querySelectorAll(".source-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      bar.querySelectorAll(".source-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      playSource(sources[Number(btn.dataset.index)]);
    });
  });

  playSource(sources[0]);
}

async function playSource(source) {
  const player = document.getElementById("player-frame");
  player.src = source.url ? embedUrlFor(source.url) : "";

  try {
    const { click_count } = await Api.registerClick(currentVideo.video_id);
    document.getElementById("video-clicks").textContent = `▶ ${click_count} plays`;
  } catch (_) {
    // click tracking is best-effort; don't block playback on failure
  }
}

async function loadComments() {
  const list = document.getElementById("comments-list");
  try {
    const comments = await Api.listComments(currentVideo.video_id);
    if (!comments.length) {
      list.innerHTML = `<p class="muted">No comments yet — be the first!</p>`;
      return;
    }
    list.innerHTML = comments
      .map(
        (c) => `
        <div class="comment" data-id="${c.comment_id}">
          <div class="comment-header">
            <strong>${c.nickname}</strong>
            <span class="muted">${new Date(c.created_at).toLocaleString()}</span>
          </div>
          <p>${c.text}</p>
          <button class="like-btn" data-id="${c.comment_id}">👍 ${c.likes}</button>
        </div>`
      )
      .join("");

    list.querySelectorAll(".like-btn").forEach((btn) => {
      btn.addEventListener("click", async () => {
        try {
          const { likes } = await Api.likeComment(currentVideo.video_id, btn.dataset.id);
          btn.textContent = `👍 ${likes}`;
        } catch (err) {
          alert(err.message);
        }
      });
    });
  } catch (err) {
    list.innerHTML = `<p class="error">${err.message}</p>`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadVideo();

  document.getElementById("rating-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!getToken()) return (window.location.href = "login.html");
    const score = document.getElementById("rating-select").value;
    try {
      const result = await Api.submitRating(currentVideo.video_id, score);
      document.getElementById("video-rating").textContent = `⭐ ${result.avg_rating} (${result.rating_count} ratings)`;
    } catch (err) {
      alert(err.message);
    }
  });

  document.getElementById("comment-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!getToken()) return (window.location.href = "login.html");
    const input = document.getElementById("comment-input");
    if (!input.value.trim()) return;
    try {
      await Api.addComment(currentVideo.video_id, input.value.trim());
      input.value = "";
      loadComments();
    } catch (err) {
      alert(err.message);
    }
  });

  document.getElementById("favorite-btn").addEventListener("click", async () => {
    if (!getToken()) return (window.location.href = "login.html");
    try {
      if (currentVideo.is_favorite) {
        await Api.removeFavorite(currentVideo.video_id);
        currentVideo.is_favorite = false;
      } else {
        await Api.addFavorite(currentVideo.video_id);
        currentVideo.is_favorite = true;
      }
      renderVideo();
    } catch (err) {
      alert(err.message);
    }
  });

  document.getElementById("report-btn").addEventListener("click", async () => {
    if (!getToken()) return (window.location.href = "login.html");
    try {
      const activeSourceBtn = document.querySelector(".source-btn.active");
      const sourceName = activeSourceBtn ? activeSourceBtn.textContent : "";
      const result = await Api.reportBrokenLink(currentVideo.video_id, sourceName, "");
      alert(result.message);
    } catch (err) {
      alert(err.message);
    }
  });
});
