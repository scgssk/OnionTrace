console.log("Renderer loaded");

let currentResults = [];

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

    meta.innerHTML =
      `Analysis based on <strong>${response.sessions}</strong> sessions ` +
      `<span style="opacity:0.6">(${mode} mode)</span>`;

    renderResults(currentResults);
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

function renderResults(data) {
  tbody.innerHTML = "";

  if (!data.length) {
    tbody.innerHTML =
      `<tr><td colspan="5" class="empty-state">
        No correlation results available.
       </td></tr>`;
    return;
  }

  data.forEach(row => {
    const tr = document.createElement("tr");
    const level = row.confidence_level;
    const pct = Math.round(row.confidence * 100);

    tr.innerHTML = `
      <td>
        <span class="guard-id" title="${row.guard_id}">
          ${row.guard_id.substring(0, 12)}...
        </span>
      </td>
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
