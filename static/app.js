const usernameInput = document.getElementById("username");
const checkButton = document.getElementById("check-btn");
const resultsCard = document.getElementById("results-card");
const resultsBody = document.getElementById("results-body");
const loadingEl = document.getElementById("loading");
const errorEl = document.getElementById("error");
const copyBtn = document.getElementById("copy-btn");
const downloadBtn = document.getElementById("download-btn");
const suggestionsBox = document.getElementById("suggestions");
const suggestionsList = document.getElementById("suggestions-list");

let lastPayload = null;
let lastPointer = { x: 0, y: 0 };

const usernamePattern = /^[A-Za-z0-9_.]{2,30}$/;

function setLoading(isLoading) {
  loadingEl.hidden = !isLoading;
  checkButton.disabled = isLoading;
}

function showError(message) {
  errorEl.textContent = message;
  errorEl.hidden = !message;
}

function showCursorToast(message, tone = "info") {
  if (!message) return;
  const toast = document.createElement("div");
  toast.className = `cursor-toast${tone === "error" ? " cursor-toast--error" : ""}`;
  toast.textContent = message;
  toast.style.left = `${lastPointer.x}px`;
  toast.style.top = `${lastPointer.y}px`;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 800);
}

function resetResults() {
  resultsCard.hidden = true;
  suggestionsBox.hidden = true;
  copyBtn.disabled = true;
  downloadBtn.disabled = true;
  lastPayload = null;
}

function statusClass(status) {
  if (status === "available") return "status-available";
  if (status === "taken") return "status-taken";
  return "status-unknown";
}

function renderResults(payload) {
  resultsBody.innerHTML = "";
  payload.results.forEach((item) => {
    const row = document.createElement("tr");

    const platformCell = document.createElement("td");
    platformCell.textContent = item.platform;

    const statusCell = document.createElement("td");
    statusCell.textContent = item.status;
    statusCell.className = statusClass(item.status);

    const linkCell = document.createElement("td");
    if (item.url && item.status === "taken") {
      const link = document.createElement("a");
      link.href = item.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = "View";
      linkCell.appendChild(link);
    } else if (item.url && item.status === "unknown") {
      const link = document.createElement("a");
      link.href = item.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = "Check";
      linkCell.appendChild(link);
    } else {
      linkCell.textContent = "-";
    }

    row.appendChild(platformCell);
    row.appendChild(statusCell);
    row.appendChild(linkCell);
    resultsBody.appendChild(row);
  });

  const suggestions = payload.suggestions || [];
  suggestionsList.innerHTML = "";
  if (suggestions.length) {
    suggestions.forEach((value) => {
      const chip = document.createElement("span");
      chip.className = "suggestion-chip";
      chip.textContent = value;
      suggestionsList.appendChild(chip);
    });
    suggestionsBox.hidden = false;
  } else {
    suggestionsBox.hidden = true;
  }

  resultsCard.hidden = false;
  copyBtn.disabled = false;
  downloadBtn.disabled = false;
}

async function checkUsername() {
  const username = usernameInput.value.trim();

  if (!usernamePattern.test(username)) {
    showError("Use 2-30 characters: letters, numbers, underscore, or dot.");
    resetResults();
    return;
  }

  showError("");
  setLoading(true);

  try {
    const response = await fetch(`/api/check?username=${encodeURIComponent(username)}`);
    const data = await response.json();

    if (!response.ok) {
      const message = data?.detail || "Something went wrong.";
      showError(message);
      resetResults();
      return;
    }

    lastPayload = data;
    renderResults(data);
  } catch (err) {
    showError("Network error. Please try again.");
    resetResults();
  } finally {
    setLoading(false);
  }
}

function copyWithFallback(text) {
  if (!text) return Promise.reject(new Error("empty"));

  if (navigator.clipboard && window.isSecureContext) {
    return navigator.clipboard.writeText(text);
  }

  return new Promise((resolve, reject) => {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.top = "-9999px";
    document.body.appendChild(textarea);
    textarea.select();

    const ok = document.execCommand("copy");
    textarea.remove();
    if (ok) {
      resolve();
    } else {
      reject(new Error("copy failed"));
    }
  });
}

async function copyJson() {
  if (!lastPayload) return;
  const text = JSON.stringify(lastPayload, null, 2);

  try {
    await copyWithFallback(text);
    showCursorToast("Copied JSON to clipboard.");
  } catch (err) {
    showCursorToast("Clipboard unavailable. Try downloading instead.", "error");
  }
}

async function copySuggestion(value) {
  if (!value) return;
  try {
    await copyWithFallback(value);
    showCursorToast("Copied suggestion to clipboard.");
  } catch (err) {
    showCursorToast("Clipboard unavailable. Try copying manually.", "error");
  }
}

function downloadJson() {
  if (!lastPayload) return;
  const text = JSON.stringify(lastPayload, null, 2);
  const blob = new Blob([text], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `handle-scout-${lastPayload.username}.json`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

checkButton.addEventListener("click", checkUsername);
usernameInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    checkUsername();
  }
});
window.addEventListener("mousemove", (event) => {
  lastPointer = { x: event.clientX, y: event.clientY };
});
copyBtn.addEventListener("click", copyJson);
downloadBtn.addEventListener("click", downloadJson);
suggestionsList.addEventListener("click", (event) => {
  const target = event.target;
  if (target && target.classList.contains("suggestion-chip")) {
    copySuggestion(target.textContent);
  }
});
