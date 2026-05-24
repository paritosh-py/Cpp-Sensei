const { contextBridge, ipcRenderer } = require('electron');

contextBridge.revealInMainWorld('electronAPI', {
    openFolder: () => ipcRenderer.invoke('open-folder'),
    readDirectory: (dirPath) => ipcRenderer.invoke('read-directory', dirPath),
    readFile: (filePath) => ipcRenderer.invoke('read-file', filePath),
    writeFile: (filePath, content) => ipcRenderer.invoke('write-file', filePath, content),
    createFile: (filePath) => ipcRenderer.invoke('create-file', filePath),
    createFolder: (dirPath) => ipcRenderer.invoke('create-folder', dirPath),
    deletePath: (filePath) => ipcRenderer.invoke('delete-path', filePath),
    renamePath: (oldPath, newPath) => ipcRenderer.invoke('rename-path', oldPath, newPath),
    joinPath: (...args) => ipcRenderer.invoke('join-path', ...args)
});
