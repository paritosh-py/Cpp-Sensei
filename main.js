const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs').promises;
const { spawn } = require('child_process');

let mainWindow = null;
let backendProcess = null;

// Helper to recursively read directory contents for the explorer tree
async function readDirectoryRecursive(dirPath, depth = 0, rootPath = dirPath) {
    const entries = await fs.readdir(dirPath, { withFileTypes: true });
    const results = [];

    for (const entry of entries) {
        if (entry.name.startsWith('.')) continue; // skip hidden files
        
        const fullPath = path.join(dirPath, entry.name);
        const relativePath = path.relative(rootPath, fullPath).replace(/\\/g, '/');

        if (entry.isDirectory()) {
            try {
                const children = await readDirectoryRecursive(fullPath, depth + 1, rootPath);
                results.push({
                    name: entry.name,
                    path: fullPath, // Store absolute path
                    relativePath: relativePath,
                    kind: 'directory',
                    children: children,
                    expanded: depth === 0,
                    depth: depth
                });
            } catch (err) {
                // Skip directories we cannot read (permissions, etc.)
                console.error(`Cannot read directory ${fullPath}: ${err.message}`);
            }
        } else {
            results.push({
                name: entry.name,
                path: fullPath, // Store absolute path
                relativePath: relativePath,
                kind: 'file',
                depth: depth
            });
        }
    }

    // Sort: folders first, then files alphabetically
    results.sort((a, b) => {
        if (a.kind !== b.kind) return a.kind === 'directory' ? -1 : 1;
        return a.name.localeCompare(b.name);
    });

    return results;
}

function startBackend() {
    const isPackaged = app.isPackaged;
    let backendCmd;
    let args = [];

    if (isPackaged) {
        // In production, server.exe is placed in the resources folder
        backendCmd = path.join(process.resourcesPath, 'server.exe');
    } else {
        // In development, spawn the python process running server.py
        backendCmd = process.platform === 'win32' ? 'python.exe' : 'python';
        args = [path.join(__dirname, 'server.py')];
    }

    console.log(`[Main] Starting backend process: ${backendCmd} ${args.join(' ')}`);

    backendProcess = spawn(backendCmd, args, {
        cwd: __dirname,
        env: { ...process.env }
    });

    backendProcess.stdout.on('data', (data) => {
        console.log(`[Python Server]: ${data.toString().trim()}`);
    });

    backendProcess.stderr.on('data', (data) => {
        console.error(`[Python Server Error]: ${data.toString().trim()}`);
    });

    backendProcess.on('error', (err) => {
        console.error(`[Main] Failed to start backend: ${err.message}`);
    });

    backendProcess.on('exit', (code, signal) => {
        console.log(`[Main] Backend exited with code ${code} and signal ${signal}`);
    });
}

function killBackend() {
    if (backendProcess) {
        console.log('[Main] Terminating backend process tree...');
        if (process.platform === 'win32') {
            try {
                // Clean up process tree on Windows to prevent orphaned uvicorn servers
                spawn('taskkill', ['/pid', backendProcess.pid, '/f', '/t']);
            } catch (e) {
                backendProcess.kill();
            }
        } else {
            backendProcess.kill();
        }
        backendProcess = null;
    }
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1100,
        height: 750,
        title: "Sensei",
        icon: path.join(__dirname, 'assets', 'icon.ico'), // Custom icon path
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false,
            sandbox: false
        }
    });

    // Load file locally for immediate offline-first UI start
    mainWindow.loadFile(path.join(__dirname, 'index.html'));

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

// IPC Handlers for Native Filesystem Operations
ipcMain.handle('open-folder', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openDirectory']
    });

    if (result.canceled || result.filePaths.length === 0) {
        return null;
    }

    const folderPath = result.filePaths[0];
    const folderName = path.basename(folderPath);
    const fileTree = await readDirectoryRecursive(folderPath);

    return {
        folderPath,
        folderName,
        fileTree
    };
});

ipcMain.handle('read-directory', async (event, dirPath) => {
    return await readDirectoryRecursive(dirPath);
});

ipcMain.handle('read-file', async (event, filePath) => {
    return await fs.readFile(filePath, 'utf-8');
});

ipcMain.handle('write-file', async (event, filePath, content) => {
    await fs.writeFile(filePath, content, 'utf-8');
    return true;
});

ipcMain.handle('create-file', async (event, filePath) => {
    await fs.writeFile(filePath, '', 'utf-8');
    return true;
});

ipcMain.handle('create-folder', async (event, dirPath) => {
    await fs.mkdir(dirPath, { recursive: true });
    return true;
});

ipcMain.handle('delete-path', async (event, filePath) => {
    await fs.rm(filePath, { recursive: true, force: true });
    return true;
});

ipcMain.handle('rename-path', async (event, oldPath, newPath) => {
    await fs.rename(oldPath, newPath);
    return true;
});

ipcMain.handle('join-path', async (event, ...args) => {
    return path.join(...args);
});

// App Lifecycle
app.whenReady().then(() => {
    startBackend();
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    killBackend();
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('will-quit', () => {
    killBackend();
});
