console.log("Renderer loaded");

if (!window.api) {
  console.error("API not exposed");
} else {
  const data = window.api.loadResults();
  console.log("Loaded data:", data);

  const table = document.getElementById("results");

  if (data.length === 0) {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td colspan="4">No results available</td>`;
    table.appendChild(tr);
  }

  data.forEach(row => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.guard_id}</td>
      <td>${row.confidence}</td>
      <td class="${row.confidence_level}">${row.confidence_level}</td>
      <td>${row.explanation}</td>
    `;
    table.appendChild(tr);
  });
}
