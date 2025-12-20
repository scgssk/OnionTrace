console.log("Renderer loaded");

if (!window.api) {
    console.error("API not exposed");
} else {
    const data = window.api.loadResults();
    console.log("Loaded data:", data);

    document.getElementById("export").onclick = () => {
        const path = window.api.saveResults(data);
        alert("Exported to " + path);
    };

    const meta = document.getElementById("meta");
    if (data.length > 0) {
        meta.innerHTML = `Analysis based on <strong>${data[0].sessions_seen}</strong> correlated sessions <span style="opacity:0.6">(Simulation Mode)</span>`;
    }

    const tbody = document.getElementById("table-body");

    if (data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="empty-state">No correlation results available. Run the analysis first.</td></tr>`;
    } else {
        data.forEach(row => {
            const tr = document.createElement("tr");

            // Use the level (HIGH/MEDIUM/LOW) to scope color usage
            const levelClass = row.confidence_level;
            const percentage = Math.round(row.confidence * 100);

            tr.innerHTML = `
                <td>
                    <span class="guard-id" title="${row.guard_id}">${row.guard_id.substring(0, 12)}...</span>
                </td>
                <td style="font-weight: 500;">
                    ${row.confidence.toFixed(3)}
                </td>
                <td>
                    <div class="bar-container ${levelClass}">
                        <div class="bar-fill" style="width: ${percentage}%"></div>
                    </div>
                </td>
                <td>
                    <span class="tag ${levelClass}">${row.confidence_level}</span>
                </td>
                <td class="explanation">
                    ${row.explanation}
                </td>
            `;

            tbody.appendChild(tr);
        });
    }
}

