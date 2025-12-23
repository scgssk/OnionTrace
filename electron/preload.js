const { contextBridge } = require("electron");
const fs = require("fs");
const path = require("path");

contextBridge.exposeInMainWorld("api", {
  investigate: async (filePath, mode) => {
    const fileBuffer = fs.readFileSync(filePath);

    const formData = new FormData();
    formData.append(
      "file",
      new Blob([fileBuffer]),
      path.basename(filePath)
    );
    formData.append("mode", mode);

    const res = await fetch("http://localhost:8000/investigate", {
      method: "POST",
      body: formData
    });

    return res.json();
  },

  saveResults: (data) => {
    const out = path.resolve(
      __dirname,
      "..",
      "export_guard_report.json"
    );
    fs.writeFileSync(out, JSON.stringify(data, null, 2));
    return out;
  }
});
