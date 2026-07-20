// Homepage: video grid + search + tag filter + sort toggle.

const TAGS = ["Action", "Sci-Fi", "Comedy", "Mystery", "Drama", "Horror"];

let currentTag = "";
let currentSort = "";
let currentQuery = "";

function videoCardHtml(v) {
  const thumb = v.thumbnail_url || "https://placehold.co/300x170?text=No+Thumbnail";
  return `
    <a class="video-card" href="detail.html?id=${v.video_id}">
      <img src="${thumb}" alt="${v.title}" />
      <div class="video-card-body">
        <h3>${v.title}</h3>
        <div class="video-card-meta">
          <span>⭐ ${v.avg_rating ?? 0}</span>
          <span>▶ ${v.click_count ?? 0}</span>
        </div>
      </div>
    </a>
  `;
}

async function loadVideos() {
  const grid = document.getElementById("video-grid");
  grid.innerHTML = `<p class="muted">Loading...</p>`;
  try {
    let videos;
    if (currentQuery) {
      videos = await Api.searchVideos(currentQuery);
    } else {
      const params = {};
      if (currentTag) params.tag = currentTag;
      if (currentSort) params.sort = currentSort;
      videos = await Api.listVideos(params);
    }

    if (!videos.length) {
      grid.innerHTML = `<p class="muted">No videos found.</p>`;
      return;
    }
    grid.innerHTML = videos.map(videoCardHtml).join("");
  } catch (err) {
    grid.innerHTML = `<p class="error">Failed to load videos: ${err.message}</p>`;
  }
}

function renderTags() {
  const tagBar = document.getElementById("tag-bar");
  tagBar.innerHTML =
    `<button class="tag-btn ${currentTag === "" ? "active" : ""}" data-tag="">All</button>` +
    TAGS.map((t) => `<button class="tag-btn ${currentTag === t ? "active" : ""}" data-tag="${t}">${t}</button>`).join("");

  tagBar.querySelectorAll(".tag-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      currentTag = btn.dataset.tag;
      currentQuery = "";
      document.getElementById("search-input").value = "";
      renderTags();
      loadVideos();
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  renderTags();
  loadVideos();

  const searchInput = document.getElementById("search-input");
  let debounceTimer;
  searchInput.addEventListener("input", () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      currentQuery = searchInput.value.trim();
      loadVideos();
    }, 300);
  });

  const sortSelect = document.getElementById("sort-select");
  sortSelect.addEventListener("change", () => {
    currentSort = sortSelect.value;
    loadVideos();
  });
});
