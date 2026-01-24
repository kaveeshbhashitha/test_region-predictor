console.log("Batch CSV handler loaded");

const batchFileInput = document.getElementById("batchFile");
const uploadArea = document.querySelector(".upload-area");
const selectFileBtn = document.getElementById("selectFileBtn");

const csvPreview = document.getElementById("csvPreview");
const csvTableHead = document.getElementById("csvTableHead");
const csvTableBody = document.getElementById("csvTableBody");

let selectedFile = null;

// ==============================
// FILE SELECTION
// ==============================
selectFileBtn.addEventListener("click", () => batchFileInput.click());

uploadArea.addEventListener("click", () => batchFileInput.click());

batchFileInput.addEventListener("change", handleFileSelect);

// ==============================
// HANDLE FILE
// ==============================
function handleFileSelect(event) {
  const file = event.target.files[0];
  console.log("Selected file:", file); // Debugging line
  if (!file) {
    console.log("No file selected."); // Debugging line
    return;
  }

  if (!file.name.toLowerCase().endsWith(".csv")) {
    alert("Only CSV files are allowed");
    return;
  }

  selectedFile = file;
  console.log("File set for analysis:", selectedFile); // Debugging line
  previewCSV(file);
}

// ==============================
// CSV PREVIEW
// ==============================
function previewCSV(file) {
  const reader = new FileReader();

  reader.onload = function (e) {
    const lines = e.target.result.split(/\r?\n/).filter(l => l.trim() !== "");

    if (lines.length < 2) {
      alert("CSV must contain at least one data row");
      return;
    }

    const headers = lines[0].split(",");
    if (headers.length !== 7) {
      alert("CSV must have exactly 7 sensor columns");
      return;
    }

    // Clear table
    csvTableHead.innerHTML = "";
    csvTableBody.innerHTML = "";

    // Header
    const headerRow = document.createElement("tr");
    headers.forEach(h => {
      const th = document.createElement("th");
      th.textContent = h.trim();
      headerRow.appendChild(th);
    });
    csvTableHead.appendChild(headerRow);

    // Preview rows (max 10)
    lines.slice(1, 11).forEach(row => {
      const tr = document.createElement("tr");
      row.split(",").forEach(cell => {
        const td = document.createElement("td");
        td.textContent = cell.trim();
        tr.appendChild(td);
      });
      csvTableBody.appendChild(tr);
    });

    csvPreview.style.display = "block";
    injectAnalyzeButton();
  };

  reader.readAsText(file);
}

// ANALYZE BUTTON
function injectAnalyzeButton() {
  if (document.getElementById("analyzeBatchBtn")) return;

  const btn = document.createElement("button");
  btn.id = "analyzeBatchBtn";
  btn.className = "btn btn-success mt-4";
  btn.textContent = "Analyze Batch CSV";

  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    submitBatch();
  });

  csvPreview.appendChild(btn);
}

async function submitBatch() {
  if (!selectedFile) {
    alert("Please select a CSV file first");
    return;
  }

  const formData = new FormData();
  formData.append("file", selectedFile);

  console.log("📤 Sending file:", selectedFile.name);

  try {
    const response = await fetch("/predict-batch", {
      method: "POST",
      body: formData   // ❗ DO NOT set headers
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || "Batch prediction failed");
    }

    console.log("✅ Batch result:", result);
    displayBatchSummary(result);

  } catch (err) {
    console.error("❌ Batch error:", err);
    alert(err.message);
  }
}

// ==============================
// DISPLAY SUMMARY
// ==============================
function displayBatchSummary(result) {
  alert(
    `Batch completed\n\n` +
    `Total samples: ${result.total_samples}\n` +
    `Accepted: ${result.accepted}\n` +
    `Rejected: ${result.rejected}`
  );

  // Optional: log rejected reasons
  const rejected = result.results.filter(r => r.status === "REJECTED");
  if (rejected.length > 0) {
    console.warn("Rejected samples:", rejected);
  }
}
