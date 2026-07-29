// Admin dashboard: create/edit/delete videos, review broken-link reports.
// Client-side gating below is UX only -- the real access control has to be
// enforced by require_admin on the backend for every /videos write and
// /videos/reports endpoint, since anyone can edit localStorage.

const ADMIN_TAGS = ["Action", "Sci-Fi", "Comedy", "Mystery", "Drama", "Horror"];

let allVideos = [];
let allReports = [];
let reportCounts = {}; // video_id -> open report count
let selectedVideoId = null;

function renderTagCheckboxes(selected = []) {
  const box = document.getElementById("tags-checkboxes");
  box.innerHTML = ADMIN_TAGS.map(
    (t) => `
      <label class="tag-checkbox">
        <input type="checkbox" value="${t}" ${selected.includes(t) ? "checked" : ""} /> ${t}
      </label>`
  ).join("");
}

function sourceRowHtml(name = "", url = "") {
  return `
    <div class="source-row">
      <input type="text" class="source-name" placeholder="Source name (e.g. Source A - YouTube)" value="${name}" />
      <input type="text" class="source-url" placeholder="https://..." value="${url}" />
      <button type="button" class="remove-source-btn secondary">✕</button>
    </div>
  `;
}

function addSourceRow(name = "", url = "") {
  const list = document.getElementById("sources-list");
  const wrapper = document.createElement("div");
  wrapper.innerHTML = sourceRowHtml(name, url);
  const row = wrapper.firstElementChild;
  row.querySelector(".remove-source-btn").addEventListener("click", () => row.remove());
  list.appendChild(row);
}

function resetVideoForm() {
  document.getElementById("video-id-input").value = "";
  document.getElementById("title-input").value = "";
  document.getElementById("description-input").value = "";
  document.getElementById("thumbnail-input").value = "";
  document.getElementById("sources-list").innerHTML = "";
  renderTagCheckboxes([]);
  addSourceRow();

  document.getElementById("video-form-title").textContent = "Add New Video";
  document.getElementById("video-form-submit").textContent = "Create Video";
  document.getElementById("video-form-cancel").classList.add("hidden");
  document.getElementById("video-form-message").textContent = "";
}

function loadVideoIntoForm(video) {
  document.getElementById("video-id-input").value = video.video_id;
  document.getElementById("title-input").value = video.title;
  document.getElementById("description-input").value = video.description || "";
  document.getElementById("thumbnail-input").value = video.thumbnail_url || "";
  renderTagCheckboxes(video.tags || []);

  document.getElementById("sources-list").innerHTML = "";
  const sources = video.sources && video.sources.length ? video.sources : [{ name: "", url: "" }];
  sources.forEach((s) => addSourceRow(s.name, s.url));

  document.getElementById("video-form-title").textContent = `Edit: ${video.title}`;
  document.getElementById("video-form-submit").textContent = "Save Changes";
  document.getElementById("video-form-cancel").classList.remove("hidden");
  document.getElementById("video-form-message").textContent = "";
  document.getElementById("video-form").scrollIntoView({ behavior: "smooth" });
}

function collectVideoFormPayload() {
  const title = document.getElementById("title-input").value.trim();
  const description = document.getElementById("description-input").value.trim();
  const thumbnail_url = document.getElementById("thumbnail-input").value.trim();
  const tags = Array.from(document.querySelectorAll("#tags-checkboxes input:checked")).map((i) => i.value);
  const sources = Array.from(document.querySelectorAll(".source-row"))
    .map((row) => ({
      name: row.querySelector(".source-name").value.trim(),
      url: row.querySelector(".source-url").value.trim(),
    }))
    .filter((s) => s.url);

  return { title, description, tags, sources, thumbnail_url };
}

function videoRowHtml(v) {
  const thumb = v.thumbnail_url || "https://placehold.co/80x50?text=%20";
  const reportCount = reportCounts[v.video_id] || 0;
  return `
    <tr data-id="${v.video_id}" class="${v.video_id === selectedVideoId ? "selected" : ""}">
      <td><img src="${thumb}" alt="" class="admin-thumb" /></td>
      <td>${v.title}</td>
      <td>${(v.tags || []).join(", ")}</td>
      <td>${v.avg_rating ?? 0}</td>
      <td>${v.click_count ?? 0}</td>
      <td>${reportCount > 0 ? `<span class="badge-report">🚩 ${reportCount}</span>` : "—"}</td>
      <td class="admin-row-actions">
        <button type="button" class="secondary edit-video-btn">Edit</button>
        <button type="button" class="secondary delete-video-btn">Delete</button>
      </td>
    </tr>
  `;
}

function selectVideo(videoId) {
  selectedVideoId = videoId;
  document.querySelectorAll("#admin-video-rows tr").forEach((row) => {
    row.classList.toggle("selected", row.dataset.id === videoId);
  });
  renderReportsPanel();
}

async function loadVideos() {
  const tbody = document.getElementById("admin-video-rows");
  try {
    allVideos = await Api.listVideos();
    tbody.innerHTML = allVideos.map(videoRowHtml).join("");

    tbody.querySelectorAll("tr").forEach((row) => {
      row.addEventListener("click", () => selectVideo(row.dataset.id));
    });

    tbody.querySelectorAll(".edit-video-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const videoId = btn.closest("tr").dataset.id;
        const video = allVideos.find((v) => v.video_id === videoId);
        if (video) loadVideoIntoForm(video);
      });
    });

    tbody.querySelectorAll(".delete-video-btn").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        e.stopPropagation();
        const videoId = btn.closest("tr").dataset.id;
        const video = allVideos.find((v) => v.video_id === videoId);
        if (!confirm(`Delete "${video?.title}"? This cannot be undone.`)) return;
        try {
          await Api.adminDeleteVideo(videoId);
          if (selectedVideoId === videoId) selectedVideoId = null;
          await loadVideos();
          renderReportsPanel();
        } catch (err) {
          document.getElementById("admin-video-message").textContent = err.message;
        }
      });
    });
  } catch (err) {
    document.getElementById("admin-video-message").textContent = err.message;
  }
}

function reportRowHtml(r) {
  return `
    <tr data-id="${r.report_id}">
      <td>${r.source_name || "—"}</td>
      <td>${r.note || "—"}</td>
      <td>${r.reporter_email || r.user_id}</td>
      <td>${new Date(r.created_at).toLocaleString()}</td>
      <td>${r.status}</td>
      <td class="admin-row-actions">
        ${r.status !== "resolved" ? `<button type="button" class="secondary resolve-report-btn">Resolve</button>` : ""}
        <button type="button" class="secondary dismiss-report-btn">Dismiss</button>
      </td>
    </tr>
  `;
}

function attachReportRowHandlers(tbody) {
  tbody.querySelectorAll(".resolve-report-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const reportId = btn.closest("tr").dataset.id;
      try {
        await Api.adminUpdateReportStatus(reportId, "resolved");
        await loadReports();
      } catch (err) {
        document.getElementById("reports-message").textContent = err.message;
      }
    });
  });

  tbody.querySelectorAll(".dismiss-report-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const reportId = btn.closest("tr").dataset.id;
      if (!confirm("Delete this report?")) return;
      try {
        await Api.adminDeleteReport(reportId);
        await loadReports();
      } catch (err) {
        document.getElementById("reports-message").textContent = err.message;
      }
    });
  });
}

function renderReportsPanel() {
  const heading = document.getElementById("reports-heading");
  const hint = document.getElementById("reports-hint");
  const table = document.getElementById("reports-table");
  const tbody = document.getElementById("reports-rows");
  const messageEl = document.getElementById("reports-message");

  if (!selectedVideoId) {
    heading.textContent = "Broken Link Reports";
    hint.textContent = "Select a video above to see its reports.";
    hint.classList.remove("hidden");
    table.classList.add("hidden");
    messageEl.textContent = "";
    return;
  }

  const video = allVideos.find((v) => v.video_id === selectedVideoId);
  heading.textContent = `Broken Link Reports — ${video ? video.title : selectedVideoId}`;

  const reports = allReports.filter((r) => r.video_id === selectedVideoId);
  if (!reports.length) {
    hint.textContent = "No reports for this video.";
    hint.classList.remove("hidden");
    table.classList.add("hidden");
    messageEl.textContent = "";
    return;
  }

  hint.classList.add("hidden");
  table.classList.remove("hidden");
  tbody.innerHTML = reports.map(reportRowHtml).join("");
  attachReportRowHandlers(tbody);
}

async function loadReports() {
  try {
    allReports = await Api.adminListReports();

    // Group counts by video for the badge shown in the Manage Videos table.
    reportCounts = {};
    allReports
      .filter((r) => r.status !== "resolved")
      .forEach((r) => {
        reportCounts[r.video_id] = (reportCounts[r.video_id] || 0) + 1;
      });

    // Refresh the badges already on screen.
    document.querySelectorAll("#admin-video-rows tr").forEach((row) => {
      const count = reportCounts[row.dataset.id] || 0;
      row.querySelector("td:nth-child(6)").innerHTML = count > 0 ? `<span class="badge-report">🚩 ${count}</span>` : "—";
    });

    renderReportsPanel();
  } catch (err) {
    document.getElementById("reports-message").textContent = err.message;
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  if (!getToken()) {
    window.location.href = "login.html";
    return;
  }

  let me;
  try {
    me = await Api.getMe();
  } catch (err) {
    window.location.href = "login.html";
    return;
  }

  if (me.role !== "admin") {
    document.getElementById("admin-denied").classList.remove("hidden");
    return;
  }

  document.getElementById("admin-content").classList.remove("hidden");
  resetVideoForm();
  await loadVideos();
  await loadReports();

  document.getElementById("add-source-btn").addEventListener("click", () => addSourceRow());
  document.getElementById("video-form-cancel").addEventListener("click", resetVideoForm);

  document.getElementById("video-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const videoId = document.getElementById("video-id-input").value;
    const payload = collectVideoFormPayload();
    const messageEl = document.getElementById("video-form-message");

    if (!payload.title) {
      messageEl.textContent = "Title is required.";
      return;
    }

    try {
      if (videoId) {
        await Api.adminUpdateVideo(videoId, payload);
      } else {
        await Api.adminCreateVideo(payload);
      }
      resetVideoForm();
      await loadVideos();
      await loadReports();
    } catch (err) {
      messageEl.textContent = err.message;
    }
  });
});
