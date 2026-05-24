const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');

let mainWindow;
let backendProcess;

// Figure out where server.exe is — works both in dev and packaged .exe
function getServerPath() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, 'server.exe');
  } else {
    return path.join(__dirname, 'dist', 'server.exe');
  }
}

// Poll localhost:8000 until the Python server is ready
function waitForServer(url, retries, callback) {
  http.get(url, (res) => {
    callback(); // Server is up!
  }).on('error', () => {
    if (retries === 0) {
      console.error('Server failed to start.');
      return;
    }
    setTimeout(() => waitForServer(url, retries - 1, callback), 500);
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    title: 'Cpp Sensei',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    }
  });

  mainWindow.loadURL('http://localhost:8000');
  mainWindow.setMenuBarVisibility(false); // Hide default menu bar

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  // Launch Python backend
  const serverPath = getServerPath();
  backendProcess = spawn(serverPath, [], {
    detached: false,
    stdio: 'ignore'
  });

  backendProcess.on('error', (err) => {
    console.error('Failed to start backend:', err);
  });

  // Wait for server to be ready, then open window
  waitForServer('http://localhost:8000', 20, createWindow);
});

// Kill backend when Electron closes
app.on('window-all-closed', () => {
  if (backendProcess) {
    backendProcess.kill();
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  if (backendProcess) {
    backendProcess.kill();
  }
});