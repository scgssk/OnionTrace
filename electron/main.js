const { app, BrowserWindow } = require("electron");
const path = require("path");

function createWindow() {
  const win = new BrowserWindow({
    width: 1000,
    height: 700,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      sandbox: false   // 🔥 THIS IS THE FIX
    }
  });

  win.loadFile("index.html");
  win.webContents.openDevTools(); // keep for debugging
}

app.whenReady().then(createWindow);
