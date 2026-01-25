console.log("✅ Batch CSV handler loaded");

// ==============================
// DOM ELEMENTS
// ==============================
const batchFileInput = document.getElementById("batchFile");
const uploadArea = document.querySelector(".upload-area");
const selectFileBtn = document.getElementById("selectFileBtn");

const batchResults = document.getElementById("batchResults");
const batchSummary = document.getElementById("batchSummary");
const batchResultsBody = document.getElementById("batchResultsBody");

let selectedFile = null;
let analyzeBtn = null;

// ==============================
// FILE SELECTION
// ==============================
selectFileBtn.addEventListener("click", () => batchFileInput.click());
uploadArea.addEventListener("click", () => batchFileInput.click());
batchFileInput.addEventListener("change", handleFileSelect);

// ==============================
// HANDLE FILE SELECT
// ==============================
function handleFileSelect(event) {
  const file = event.target.files[0];

  if (!file) return;

  if (!file.name.toLowerCase().endsWith(".csv")) {
    alert("Only CSV files are allowed");
    batchFileInput.value = "";
    return;
  }

  selectedFile = file;
  console.log("Selected CSV:", file.name);
  alert("File selected successfully");

  showAnalyzeButton();
}

// ==============================
// ANALYZE BUTTON (UI-INDEPENDENT)
// ==============================
function showAnalyzeButton() {
  if (analyzeBtn) return;

  analyzeBtn = document.createElement("button");
  analyzeBtn.id = "analyzeBatchBtn";
  analyzeBtn.className = "btn btn-success mt-4";
  analyzeBtn.textContent = "Analyze Batch CSV";

  analyzeBtn.addEventListener("click", submitBatch);

  // Append button under upload area
  uploadArea.parentElement.appendChild(analyzeBtn);
}

// ==============================
// SUBMIT BATCH
// ==============================
async function submitBatch() {
  if (!selectedFile) {
    alert("Please select a CSV file first");
    return;
  }

  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Analyzing...";

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const response = await fetch("/predict-batch", {
      method: "POST",
      body: formData // ❗ no headers
    });

    const result = await response.json();

    if (!response.ok || !result.success) {
      throw new Error(result.error || "Batch prediction failed");
    }

    console.log("Batch response:", result);
    renderBatchResults(result);

  } catch (err) {
    console.error("Batch error:", err);
    alert(err.message);

  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "Analyze Batch CSV";
  }
}

// ==============================
// RENDER RESULTS
// ==============================
function renderBatchResults(response) {
  batchResults.style.display = "block";
  batchResultsBody.innerHTML = "";

  // ---- Summary alert ----
  batchSummary.className =
    response.rejected === 0
      ? "alert alert-success mt-3"
      : "alert alert-warning mt-3";

  batchSummary.innerHTML = `
    <strong>Batch Analysis Complete</strong><br>
    Total Samples: ${response.total_samples} |
    Accepted: ${response.accepted} |
    Rejected: ${response.rejected} |
    Model: ${response.model}
  `;
  batchSummary.style.display = "block";

  // ---- Table rows ----
  response.results.forEach(r => {
    const tr = document.createElement("tr");

    const statusBadge =
      r.status === "ACCEPTED"
        ? `<span class="badge bg-success">Accepted</span>`
        : `<span class="badge bg-danger">Rejected</span>`;

    tr.innerHTML = `
      <td>${r.sample_index}</td>
      <td>${r.prediction ?? "-"}</td>
      <td>${(r.confidence * 100).toFixed(2)}%</td>
      <td>${statusBadge}</td>
    `;

    batchResultsBody.appendChild(tr);
  });
}