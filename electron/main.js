const { app, BrowserWindow } = require("electron");
const path = require("path");
const { spawn } = require("child_process");

let backendProcess = null;

function startBackend() {
  const venvPath = path.join(__dirname, "..", "venv");
  const pythonPath = path.join(venvPath, "Scripts", "python.exe");
  const backendPath = path.join(__dirname, "..", "backend");

  backendProcess = spawn(
    pythonPath,
    ["-m", "uvicorn", "app.api.server:app", "--host", "127.0.0.1", "--port", "8000"],
    {
      cwd: backendPath,
      shell: true
    }
  );

  backendProcess.stdout.on("data", data => {
    console.log(`[backend] ${data}`);
  });

  backendProcess.stderr.on("data", data => {
    console.error(`[backend error] ${data}`);
  });
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      sandbox: false
    }
  });

  win.loadFile("index.html");
  win.webContents.openDevTools();
}

app.whenReady().then(() => {
  startBackend();          // 🔥 AUTO START BACKEND
  createWindow();
});

app.on("before-quit", () => {
  if (backendProcess) {
    backendProcess.kill();
  }
});
