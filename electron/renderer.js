console.log("Renderer loaded");

let currentResults = [];
let confidenceTimeline = {};
let selectedGuard = null;

const meta = document.getElementById("meta");
const tbody = document.getElementById("table-body");

document.getElementById("analyze").onclick = async () => {
  const fileInput = document.getElementById("pcap");
  const mode = document.getElementById("mode").value;

  if (!fileInput.files.length) {
    alert("Please select a PCAP file");
    return;
  }

  meta.innerText = "Running analysis...";
  tbody.innerHTML = "";

  const filePath = fileInput.files[0].path;

  try {
    const response = await window.api.investigate(filePath, mode);

    if (response.status !== "success") {
      meta.innerText = "Analysis failed";
      alert(response.reason);
      return;
    }

    currentResults = response.results;
    confidenceTimeline = response.timeline;

    meta.innerHTML =
      `Analysis based on <strong>${response.sessions}</strong> sessions ` +
      `<span style="opacity:0.6">(${mode} mode)</span>`;

    renderResults(currentResults);
    drawConfidenceChart(confidenceTimeline);
  } catch (err) {
    console.error(err);
    meta.innerText = "Backend error";
    alert("Failed to communicate with backend");
  }
};


document.getElementById("export").onclick = () => {
  if (!currentResults.length) {
    alert("No results to export");
    return;
  }

  const path = window.api.saveResults(currentResults);
  alert("Exported to " + path);
};


function updateGraphTitle(row) {
  document.getElementById("graph-title").innerText =
    `Confidence Over Time — ${row.guard_id.substring(0,12)}…`;

  document.getElementById("graph-hint").innerText =
    `Confidence stabilizes as the guard reappears across sessions. Final confidence: ${row.confidence}`;
}


function renderResults(data) {
  tbody.innerHTML = "";

  data.forEach(row => {
    const tr = document.createElement("tr");
    tr.style.cursor = "pointer";

    tr.onclick = () => {
      selectedGuard = row.guard_id;
      drawConfidenceChart(confidenceTimeline, selectedGuard);
      updateGraphTitle(row);
    };

    const level = row.confidence_level;
    const pct = Math.round(row.confidence * 100);

    tr.innerHTML = `
      <td class="guard-id">${row.guard_id.substring(0,12)}...</td>
      <td>${row.confidence.toFixed(3)}</td>
      <td>
        <div class="bar-container ${level}">
          <div class="bar-fill" style="width:${pct}%"></div>
        </div>
      </td>
      <td><span class="tag ${level}">${level}</span></td>
      <td class="explanation">${row.explanation}</td>
    `;

    tbody.appendChild(tr);
  });
}


function drawConfidenceChart(timeline, guardId) {
  const canvas = document.getElementById("confidenceChart");
  const ctx = canvas.getContext("2d");

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (!guardId || !timeline[guardId]) return;

  const values = timeline[guardId];
  const padding = 40;
  const width = canvas.width - padding * 2;
  const height = canvas.height - padding * 2;

  // Axes
  ctx.strokeStyle = "#64748b";
  ctx.beginPath();
  ctx.moveTo(padding, padding);
  ctx.lineTo(padding, padding + height);
  ctx.lineTo(padding + width, padding + height);
  ctx.stroke();

  // Line
  ctx.strokeStyle = "#22c55e";
  ctx.lineWidth = 2;
  ctx.beginPath();

  values.forEach((v, i) => {
    const x = padding + (i / (values.length - 1)) * width;
    const y = padding + height - v * height;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });

  ctx.stroke();
}

document.getElementById("pdf").onclick = () => {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF("p", "pt", "a4");

  doc.text("OnionTrace Investigation Report", 40, 40);
  doc.text(`Generated: ${new Date().toLocaleString()}`, 40, 60);

  let y = 100;
  currentResults.slice(0, 10).forEach(r => {
    doc.text(`Guard: ${r.guard_id}`, 40, y);
    doc.text(`Confidence: ${r.confidence}`, 40, y + 14);
    doc.text(`Level: ${r.confidence_level}`, 40, y + 28);
    y += 60;
  });

  doc.save("oniontrace_report.pdf");
};


