const { contextBridge } = require("electron");
const fs = require("fs");
const path = require("path");

contextBridge.exposeInMainWorld("api", {
  loadResults: () => {
    try {
      const filePath = path.resolve(
        __dirname,
        "..",
        "backend",
        "output_simulation.json"
      );

      console.log("Loading results from:", filePath);

      return JSON.parse(fs.readFileSync(filePath, "utf-8"));
    } catch (err) {
      console.error("Failed to load results:", err);
      return [];
    }
  },
    saveResults: (data) => {
    const out = path.resolve(__dirname, "..", "export_guard_report.json");
    fs.writeFileSync(out, JSON.stringify(data, null, 2));
    return out;
  }
});
