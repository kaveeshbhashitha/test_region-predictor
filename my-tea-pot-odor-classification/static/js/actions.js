console.log('🍃 TeaPot ML System Initialized');
console.log('✅ Ready to classify tea samples using ExtraTrees model');
console.log('📊 Required inputs: 7 MOS sensor values (adc10–adc23)');

// ---- Single Sample Prediction ----
document.getElementById('tea-classification-form').addEventListener('submit', async function(e) {
  e.preventDefault();

  const sensorInputs = document.querySelectorAll('.sensor-input'); // must match 7 MOS inputs
  const sensorData = [];

  for (let input of sensorInputs) {
    const value = parseFloat(input.value);
    if (isNaN(value)) {
      alert(`Please enter a valid value for ${input.name}`);
      return;
    }
    sensorData.push(value);
  }

  if (sensorData.length !== 7) {
    alert("Exactly 7 sensor values are required.");
    return;
  }

  const placeholder = document.getElementById('results-placeholder');
  const results = document.getElementById('results-content');
  placeholder.style.display = 'block';
  results.style.display = 'none';

  placeholder.innerHTML = `
    <div class="spinner-border text-primary" role="status"></div>
    <h4 class="mt-3">Analyzing Sample...</h4>
  `;

  try {
    const response = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sensors: sensorData })
    });
    const result = await response.json();
    if (!result.success) throw new Error(result.error || "Prediction failed");
    displayResults(result);
  } catch (err) {
    console.error(err);
    placeholder.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
});

// ---- Display Results Function ----
function displayResults(result) {
  const placeholder = document.getElementById('results-placeholder');
  const results = document.getElementById('results-content');

  placeholder.style.display = 'none';
  results.style.display = 'block';

  const predictedRegion = result.prediction;
  const regionName = "";
  
//   switch(expression) {
//   case predictedRegion === 'SB':
//     regionName = 'Sabaragamuwa'
//     break;
//   case predictedRegion === 'RUN':
//     regionName = 'Ruhuna Region'
//     break;
//   case predictedRegion === 'NWE':
//     regionName = 'Nuwara Eliya'
//     break;
//   case predictedRegion === 'KAN':
//     regionName = 'Kandy Region'
//     break;
//   case predictedRegion === 'UPS':
//     regionName = 'Uda Pussallawa'
//     break;
//   case predictedRegion === 'UVA':
//     regionName = 'Uva Region'
//     break;
//   case predictedRegion === 'DIM':
//     regionName = 'Dimbula Region'
//     break;
//   default:
//     // code block
// }

  const confidence = result.confidence;

  // Show only predicted region
  document.querySelector('.region-probabilities').innerHTML = `
    <li class="mb-2 fw-bold">
      <strong>${predictedRegion}:</strong> ${(confidence * 100).toFixed(1)}% probability
    </li>
  `;

  // Confidence progress bar
  const progressBar = document.querySelector('.progress-bar');
  progressBar.style.width = `${(confidence * 100).toFixed(1)}%`;
  progressBar.textContent = `${(confidence * 100).toFixed(1)}%`;

  // Update quality assessment
  updateQualityAssessment(predictedRegion, confidence);

  // Radar chart for chemical signature based on real sensor mapping
  setTimeout(() => {
    const ctx = document.getElementById('chemicalChart');
    if (ctx) {
      const existingChart = Chart.getChart(ctx);
      if (existingChart) existingChart.destroy();

      new Chart(ctx.getContext('2d'), {
        type: 'radar',
        data: {
          labels: ['Theaflavins', 'Thearubigins', 'Caffeine', 'Linalool', 'Geraniol', 'Polyphenols'],
          datasets: [{
            label: 'Your Sample',
            data: generateChemicalProfile(predictedRegion, result.input_sensors),
            backgroundColor: 'rgba(65, 84, 241, 0.2)',
            borderColor: 'rgba(65, 84, 241, 1)',
            pointBackgroundColor: 'rgba(65, 84, 241, 1)',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: 'rgba(65, 84, 241, 1)'
          }]
        },
        options: {
          scales: {
            r: {
              angleLines: { display: true },
              suggestedMin: 0,
              suggestedMax: 5, // matches 0–5V sensor range
              ticks: { stepSize: 1 }
            }
          },
          plugins: { legend: { display: true, position: 'top' } }
        }
      });
    }
  }, 100);

  document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}

// ---- Quality Assessment ----
function updateQualityAssessment(region, confidence) {
  const qualityMap = {
    'Nuwara Eliya': { grade: 'Premium Grade', stars: 4.8, description: 'High-altitude grown tea with delicate aroma.' },
    'Dimbula': { grade: 'Premium Grade', stars: 4.7, description: 'Full-bodied tea with crisp, strong flavor.' },
    'Uva': { grade: 'Premium Grade', stars: 4.6, description: 'Bold and brisk tea with seasonal character.' },
    'Kandy': { grade: 'High Grade', stars: 4.3, description: 'Mid-country tea with good color and flavor.' },
    'Uda Pussellawa': { grade: 'High Grade', stars: 4.4, description: 'Medium-bodied tea with sweet notes.' },
    'Ruhuna': { grade: 'Standard Grade', stars: 4.0, description: 'Low-grown tea with distinct flavor.' },
    'Sabaragamuwa': { grade: 'Standard Grade', stars: 3.9, description: 'Smooth and mellow tea for blending.' }
  };
  const quality = qualityMap[region] || qualityMap['Kandy'];

  document.querySelector('.quality-rating .badge').textContent = quality.grade;

  const starsContainer = document.querySelector('.stars');
  const fullStars = Math.floor(quality.stars);
  const hasHalfStar = quality.stars % 1 >= 0.5;
  let starsHTML = '';
  for (let i = 0; i < fullStars; i++) starsHTML += '<i class="bi bi-star-fill text-warning"></i>';
  if (hasHalfStar) starsHTML += '<i class="bi bi-star-half text-warning"></i>';
  for (let i = Math.ceil(quality.stars); i < 5; i++) starsHTML += '<i class="bi bi-star text-warning"></i>';
  starsHTML += `<span class="ms-2">${quality.stars}/5</span>`;
  starsContainer.innerHTML = starsHTML;

  document.querySelector('.quality-rating').nextElementSibling.textContent = quality.description;
}

// ---- Chemical Profile Generator (from actual sensor data) ----
function generateChemicalProfile(region, sensors) {
  // Map your 7 MOS sensors to radar chart features
  // sensor array: [adc10, adc11, adc12, adc13, adc21, adc22, adc23]
  return [
    sensors[2], // Theaflavins → adc12
    sensors[3], // Thearubigins → adc13
    sensors[4], // Caffeine → adc21
    sensors[1], // Linalool → adc11
    sensors[5], // Geraniol → adc22
    sensors[0]  // Polyphenols → adc10
  ];
}

// ---- Reset Form ----
document.querySelectorAll('.btn-primary').forEach(btn => {
  if (btn.textContent.includes('Analyze Another')) {
    btn.addEventListener('click', function() {
      document.getElementById('tea-classification-form').reset();
      document.getElementById('results-placeholder').style.display = 'block';
      document.getElementById('results-content').style.display = 'none';
      document.getElementById('results-placeholder').innerHTML = `
        <i class="bi bi-cup-hot results-icon display-1 text-muted"></i>
        <h4 class="mt-3">Submit sample data to view analysis results</h4>
        <p class="text-muted">Your tea classification will appear here</p>
      `;
      document.getElementById('classification-hero').scrollIntoView({ behavior: 'smooth' });
    });
  }
});

// ---- File Upload / Batch CSV Handling ----
/*
document.querySelector('.upload-area').addEventListener('click', () => document.getElementById('batchFile').click());

document.getElementById('batchFile').addEventListener('change', function(e) {
  const file = this.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = async function(event) {
    const text = event.target.result;
    const rows = text.split(/\r?\n/).filter(r => r.trim() !== "");
    if (rows.length < 2) return alert("CSV must have at least one row of data.");

    const uploadArea = document.querySelector('.upload-area');
    uploadArea.innerHTML = `
      <i class="bi bi-file-earmark-spreadsheet display-4 text-success mb-3"></i>
      <p class="mb-3">${file.name}</p>
      <button class="btn btn-success" id="analyzeBatchBtn">Analyze Batch</button>
    `;

    document.getElementById('analyzeBatchBtn').addEventListener('click', async () => {
      const batchData = rows.slice(1).map(r => r.split(',').map(Number));
      try {
        const response = await fetch('/predict-batch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ batch: batchData })
        });
        const result = await response.json();
        if (!result.success) throw new Error(result.error || "Batch prediction failed");
        console.log("Batch Predictions:", result.predictions);
        console.log("Batch Probabilities:", result.probabilities);
        alert("Batch prediction completed! Check console for results.");
      } catch (err) {
        console.error(err);
        alert("Batch prediction failed: " + err.message);
      }
    });

    // Preview first 10 rows
    const tableHead = document.getElementById('csvTableHead');
    const tableBody = document.getElementById('csvTableBody');
    tableHead.innerHTML = "";
    tableBody.innerHTML = "";

    const headers = rows[0].split(",");
    const headerRow = document.createElement("tr");
    headers.forEach(h => { const th = document.createElement("th"); th.textContent = h.trim(); headerRow.appendChild(th); });
    tableHead.appendChild(headerRow);

    const maxRows = Math.min(rows.length, 11);
    for (let i = 1; i < maxRows; i++) {
      const row = rows[i].split(",");
      const tr = document.createElement("tr");
      row.forEach(cell => { const td = document.createElement("td"); td.textContent = cell.trim(); tr.appendChild(td); });
      tableBody.appendChild(tr);
    }
    document.getElementById('csvPreview').style.display = "block";
  };
  reader.readAsText(file);
});
*/

// ---- Export Results as PDF ----
document.getElementById("exportReportBtn").addEventListener("click", function () {
  const resultsSection = document.getElementById("results");
  this.innerText = "Generating PDF...";
  this.disabled = true;

  domtoimage.toPng(resultsSection)
    .then(function (dataUrl) {
      const { jsPDF } = window.jspdf;
      const pdf = new jsPDF('p', 'pt', 'a4');
      const imgProps = pdf.getImageProperties(dataUrl);
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
      pdf.addImage(dataUrl, 'PNG', 0, 0, pdfWidth, pdfHeight);
      pdf.save('Tea_Sample_Report.pdf');

      document.getElementById("exportReportBtn").innerText = "Export Report";
      document.getElementById("exportReportBtn").disabled = false;
    })
    .catch(function (error) {
      console.error('PDF generation failed:', error);
      alert("Failed to generate PDF");
      document.getElementById("exportReportBtn").innerText = "Export Report";
      document.getElementById("exportReportBtn").disabled = false;
    });
});