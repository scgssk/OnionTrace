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
  }
});
