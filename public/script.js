/* ============================================================================
   SENSEI IDE — Client-Side Application Logic
   ============================================================================
   Organized into modules:
   1. State Management
   2. Initialization
   3. File Explorer
   4. Tab Manager
   5. Editor
   6. Explanation Engine
   7. AI Assistant
   8. Terminal / Console
   9. Keyboard Shortcuts
   10. Panel Management
   11. Menu System
   12. Theme
   13. Notifications
   14. Utilities
   ============================================================================ */

// ============================================================================
// 1. STATE MANAGEMENT
// ============================================================================

const State = {
    // Editor
    activeTabId: 'untitled-1',
    tabs: new Map(), // tabId → { name, content, dirty, fileHandle, filePath }
    untitledCounter: 1,

    // Panels
    sidebarVisible: true,
    sidebarView: 'explorer', // 'explorer' | 'explain'
    rightPanelVisible: false,
    rightPanelView: 'ai', // 'ai' | 'explain'
    bottomPanelVisible: false,
    bottomPanelHeight: 200,
    sidebarWidth: 240,
    rightPanelWidth: 340,

    // Explanation
    explanationMode: 'idle', // 'idle' | 'line'
    lastExplainedLine: -1,
    explainTimeout: null,

    // AI
    chatHistory: [],

    // File Explorer
    folderHandle: null,
    fileTree: [],

    // WebSocket
    socket: null,

    // Theme
    isDarkMode: true,

    // Resize
    isResizing: false,
    resizeTarget: null,
};

// Initialize default tab
State.tabs.set('untitled-1', {
    name: 'Untitled-1.cpp',
    content: null, // will be read from textarea
    dirty: false,
    fileHandle: null,
    filePath: null
});


// ============================================================================
// 2. INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', async function () {
    initLucide();
    initTheme();
    setupEventListeners();
    setupKeyboardShortcuts();
    setupPanelResize();
    setupMenuSystem();
    checkServerConnection();

    // Store initial content
    const textarea = document.getElementById('codeTextarea');
    if (textarea) {
        State.tabs.get('untitled-1').content = textarea.value;
    }

    // Initialize Monaco Editor
    await initMonaco();

    // Render onboarding templates
    renderStarterTemplates();

    // Check initial empty state
    checkEditorEmptyState();

    updateStatusBar();
    TabManager.renderTabs();
});

function initLucide() {
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}


// ============================================================================
// 3. FILE EXPLORER
// ============================================================================

const FileExplorer = {
    async openFolder() {
        try {
            if ('showDirectoryPicker' in window) {
                const handle = await window.showDirectoryPicker();
                State.folderHandle = handle;
                await this.readDirectory(handle);
            } else {
                showToast('Unsupported', 'File System Access API not available in this browser. Use Chrome or Edge.');
            }
        } catch (e) {
            if (e.name !== 'AbortError') {
                showToast('Error', 'Failed to open folder: ' + e.message);
            }
        }
    },

    async readDirectory(dirHandle, depth = 0, parentPath = '') {
        const entries = [];
        for await (const entry of dirHandle.values()) {
            if (entry.name.startsWith('.')) continue; // skip hidden files
            const relativePath = parentPath ? `${parentPath}/${entry.name}` : entry.name;
            if (entry.kind === 'directory') {
                const children = await this.readDirectory(entry, depth + 1, relativePath);
                entries.push({
                    name: entry.name,
                    path: relativePath,
                    kind: 'directory',
                    handle: entry,
                    children: children,
                    expanded: depth === 0,
                    depth: depth
                });
            } else {
                entries.push({
                    name: entry.name,
                    path: relativePath,
                    kind: 'file',
                    handle: entry,
                    depth: depth
                });
            }
        }
        // Sort: folders first, then alphabetical
        entries.sort((a, b) => {
            if (a.kind !== b.kind) return a.kind === 'directory' ? -1 : 1;
            return a.name.localeCompare(b.name);
        });

        if (depth === 0) {
            State.fileTree = entries;
            this.renderTree();
        }
        return entries;
    },

    renderTree() {
        const container = document.getElementById('fileTree');
        const emptyState = document.getElementById('sidebarEmpty');

        if (State.fileTree.length === 0 && !State.folderHandle) {
            emptyState.style.display = 'flex';
            return;
        }
        emptyState.style.display = 'none';

        const renderNode = (node, depth) => {
            const indent = depth * 12; // tighter spacing
            if (node.kind === 'directory') {
                const chevronClass = node.expanded ? 'expanded' : '';
                const childrenClass = node.expanded ? '' : 'collapsed';

                let childrenHtml = '';
                if (node.children) {
                    node.children.forEach(child => {
                        childrenHtml += renderNode(child, depth + 1);
                    });
                }

                return `<div class="tree-folder" data-path="${node.path}">
                    <div class="tree-item" data-path="${node.path}" data-kind="directory" style="padding-left: ${8 + indent}px;" data-depth="${depth}">
                        <span class="chevron ${chevronClass}"><i data-lucide="chevron-right"></i></span>
                        <span class="file-icon folder"><i data-lucide="folder"></i></span>
                        <span class="file-name">${node.name}</span>
                    </div>
                    <div class="tree-children ${childrenClass}">
                        ${childrenHtml}
                    </div>
                </div>`;
            } else {
                const ext = node.name.split('.').pop().toLowerCase();
                let iconClass = 'default';
                if (ext === 'cpp' || ext === 'cc' || ext === 'cxx') iconClass = 'cpp';
                else if (ext === 'h' || ext === 'hpp') iconClass = 'h';

                return `<div class="tree-item" data-path="${node.path}" data-kind="file" style="padding-left: ${8 + indent + 16}px;" data-depth="${depth}">
                    <span class="file-icon ${iconClass}"><i data-lucide="file-code"></i></span>
                    <span class="file-name">${node.name}</span>
                </div>`;
            }
        };

        let html = '';
        State.fileTree.forEach(node => {
            html += renderNode(node, 0);
        });
        container.innerHTML = html;
        initLucide();

        // Highlight active file in the newly rendered tree
        const activeTab = State.tabs.get(State.activeTabId);
        if (activeTab && activeTab.filePath) {
            container.querySelectorAll('.tree-item').forEach(item => {
                item.classList.toggle('selected', item.dataset.path === activeTab.filePath);
            });
        }

        // Attach click handlers
        container.querySelectorAll('.tree-item').forEach(item => {
            item.addEventListener('click', (e) => this.handleTreeClick(e, item));
            item.addEventListener('contextmenu', (e) => this.handleTreeContextMenu(e, item));
        });
    },

    handleTreeClick(e, item) {
        const kind = item.dataset.kind;
        const path = item.dataset.path;

        if (kind === 'directory') {
            this.toggleFolder(item, path);
        } else {
            this.openFileFromTree(item, path);
        }
    },

    toggleFolder(item, path) {
        // Find node in tree and toggle expanded state
        const toggleNode = (nodes) => {
            for (const node of nodes) {
                if (node.path === path && node.kind === 'directory') {
                    node.expanded = !node.expanded;
                    return node.expanded;
                }
                if (node.children) {
                    const result = toggleNode(node.children);
                    if (result !== undefined) return result;
                }
            }
        };
        const expanded = toggleNode(State.fileTree);
        if (expanded === undefined) return;

        // Toggle visual classes in DOM for smooth animation
        const chevron = item.querySelector('.chevron');
        if (chevron) {
            chevron.classList.toggle('expanded', expanded);
        }

        const parentFolder = item.closest('.tree-folder');
        if (parentFolder) {
            const children = parentFolder.querySelector(':scope > .tree-children');
            if (children) {
                children.classList.toggle('collapsed', !expanded);
            }
        }
    },

    async openFileFromTree(item, path) {
        // Find the file handle using relative path
        const findHandle = (nodes) => {
            for (const node of nodes) {
                if (node.path === path && node.kind === 'file') return node.handle;
                if (node.children) {
                    const found = findHandle(node.children);
                    if (found) return found;
                }
            }
            return null;
        };

        const handle = findHandle(State.fileTree);
        if (!handle) return;

        // Check if already open by matching unique filePath
        for (const [tabId, tab] of State.tabs) {
            if (tab.filePath === path) {
                TabManager.switchTab(tabId);
                return;
            }
        }

        try {
            const file = await handle.getFile();
            const content = await file.text();
            const tabId = 'file-' + path.replace(/[^a-zA-Z0-9]/g, '-') + '-' + Date.now();
            const filename = item.querySelector('.file-name').textContent;
            TabManager.openTab(tabId, filename, content, handle, path);
        } catch (e) {
            showToast('Error', 'Cannot read file: ' + e.message);
        }
    },

    handleTreeContextMenu(e, item) {
        e.preventDefault();
        const menu = document.getElementById('contextMenu');
        menu.style.left = e.clientX + 'px';
        menu.style.top = e.clientY + 'px';
        menu.classList.add('active');
        menu._targetItem = item;
    },

    async createFile(name) {
        if (!State.folderHandle) {
            // Create a virtual tab instead
            State.untitledCounter++;
            const fileName = name || `Untitled-${State.untitledCounter}.cpp`;
            const tabId = 'untitled-' + State.untitledCounter;
            TabManager.openTab(tabId, fileName, '', null);
            return;
        }

        try {
            const fileName = name || 'newfile.cpp';
            const fileHandle = await State.folderHandle.getFileHandle(fileName, { create: true });
            const writable = await fileHandle.createWritable();
            await writable.write('');
            await writable.close();
            await this.readDirectory(State.folderHandle);
            const tabId = 'file-' + fileName.replace(/[^a-zA-Z0-9]/g, '-') + '-' + Date.now();
            TabManager.openTab(tabId, fileName, '', fileHandle, fileName);
            showToast('Created', `File "${fileName}" created`);
        } catch (e) {
            showToast('Error', 'Failed to create file: ' + e.message);
        }
    },

    async createFolder(name) {
        if (!State.folderHandle) {
            showToast('Info', 'Open a folder first to create subfolders.');
            return;
        }
        try {
            const folderName = name || 'new-folder';
            await State.folderHandle.getDirectoryHandle(folderName, { create: true });
            await this.readDirectory(State.folderHandle);
            showToast('Created', `Folder "${folderName}" created`);
        } catch (e) {
            showToast('Error', 'Failed to create folder: ' + e.message);
        }
    }
};


// ============================================================================
// 4. TAB MANAGER
// ============================================================================

const TabManager = {
    openTab(tabId, name, content, fileHandle = null, filePath = null) {
        // Add to state
        State.tabs.set(tabId, {
            name: name,
            content: content,
            dirty: false,
            fileHandle: fileHandle,
            filePath: filePath
        });

        // Create tab element
        this.renderTabs();
        this.switchTab(tabId);
    },

    closeTab(tabId) {
        if (State.tabs.size <= 1) {
            // Don't close the last tab, just clear it
            const tab = State.tabs.get(tabId);
            if (tab) {
                tab.content = '';
                tab.dirty = false;
                tab.name = 'Untitled-1.cpp';
                tab.fileHandle = null;
                State.untitledCounter = 1;
                setEditorCode('');
                checkEditorEmptyState();
                this.renderTabs();
                updateTitleBar();
            }
            return;
        }

        State.tabs.delete(tabId);

        // If closing active tab, switch to last tab
        if (State.activeTabId === tabId) {
            const lastKey = Array.from(State.tabs.keys()).pop();
            this.switchTab(lastKey);
        }

        this.renderTabs();
    },

    switchTab(tabId) {
        // Save current tab content
        const currentTab = State.tabs.get(State.activeTabId);
        if (currentTab) {
            currentTab.content = getEditorCode();
        }

        // Switch
        State.activeTabId = tabId;
        const tab = State.tabs.get(tabId);
        if (tab) {
            setEditorCode(tab.content || '');
            checkEditorEmptyState();
            updateTitleBar();
        }

        // Update tab UI
        document.querySelectorAll('.tab').forEach(el => {
            el.classList.toggle('active', el.dataset.tabId === tabId);
        });

        // Update file tree selection
        document.querySelectorAll('.tree-item').forEach(item => {
            item.classList.toggle('selected', item.dataset.path === tab?.filePath);
        });

        // Reset explanation
        if (State.explanationMode === 'line') {
            handleCursorMove();
        }
    },

    markDirty(tabId) {
        const tab = State.tabs.get(tabId);
        if (tab && !tab.dirty) {
            tab.dirty = true;
            this.renderTabs();
            updateTitleBar();
        }
    },

    markClean(tabId) {
        const tab = State.tabs.get(tabId);
        if (tab && tab.dirty) {
            tab.dirty = false;
            this.renderTabs();
            updateTitleBar();
        }
    },

    renderTabs() {
        const tabBar = document.getElementById('tabBar');
        let html = '';

        for (const [tabId, tab] of State.tabs) {
            const activeClass = tabId === State.activeTabId ? 'active' : '';
            const dirtyClass = tab.dirty ? 'dirty' : '';
            const ext = tab.name.split('.').pop().toLowerCase();
            let iconClass = 'default';
            if (ext === 'cpp' || ext === 'cc') iconClass = 'cpp';
            else if (ext === 'h' || ext === 'hpp') iconClass = 'h';

            html += `<div class="tab ${activeClass} ${dirtyClass}" data-tab-id="${tabId}">
                <span class="tab-icon ${iconClass}"><i data-lucide="file-code"></i></span>
                <span class="tab-title">${tab.name}</span>
                <span class="tab-action-container">
                    <span class="tab-dirty"></span>
                    <button class="tab-close" title="Close"><i data-lucide="x"></i></button>
                </span>
            </div>`;
        }

        tabBar.innerHTML = html;
        initLucide();

        // Attach events
        tabBar.querySelectorAll('.tab').forEach(tabEl => {
            tabEl.addEventListener('click', (e) => {
                if (!e.target.closest('.tab-close')) {
                    this.switchTab(tabEl.dataset.tabId);
                }
            });
            tabEl.querySelector('.tab-close')?.addEventListener('click', (e) => {
                e.stopPropagation();
                this.closeTab(tabEl.dataset.tabId);
            });
        });
    }
};


// ============================================================================
// 5. EDITOR
// ============================================================================

function updateLineNumbers() {
    if (window.editor) return;
    const textarea = document.getElementById('codeTextarea');
    const lineNumbers = document.getElementById('lineNumbers');
    if (!textarea || !lineNumbers) return;

    const lines = textarea.value.split('\n');
    const cursorLine = getCursorLineNumber(textarea);

    lineNumbers.innerHTML = lines.map((_, i) => {
        const num = i + 1;
        const activeClass = num === cursorLine ? 'active-line' : '';
        return `<div class="line-num ${activeClass}">${num}</div>`;
    }).join('');
}

function syncLineNumbersScroll() {
    if (window.editor) return;
    const textarea = document.getElementById('codeTextarea');
    const lineNumbers = document.getElementById('lineNumbers');
    if (textarea && lineNumbers) {
        lineNumbers.scrollTop = textarea.scrollTop;
    }
}

function getCursorLineNumber(textarea) {
    if (window.editor) {
        return window.editor.getPosition().lineNumber;
    }
    if (!textarea) return 1;
    const value = textarea.value;
    const selectionStart = textarea.selectionStart;
    return value.substr(0, selectionStart).split('\n').length;
}

function getCursorColumn(textarea) {
    if (window.editor) {
        return window.editor.getPosition().column;
    }
    if (!textarea) return 1;
    const value = textarea.value;
    const selectionStart = textarea.selectionStart;
    const lines = value.substr(0, selectionStart).split('\n');
    return lines[lines.length - 1].length + 1;
}

function handleEditorInput() {
    updateLineNumbers();
    updateStatusBar();
    TabManager.markDirty(State.activeTabId);

    // Trigger explanation if in line mode
    if (State.explanationMode === 'line') {
        handleCursorMove();
    }
}

function handleEditorKeydown(e) {
    const textarea = e.target;

    // Tab key → insert 4 spaces
    if (e.key === 'Tab') {
        e.preventDefault();
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;

        if (e.shiftKey) {
            // Outdent
            const lineStart = textarea.value.lastIndexOf('\n', start - 1) + 1;
            const lineText = textarea.value.substring(lineStart, start);
            const spaces = lineText.match(/^ {1,4}/);
            if (spaces) {
                textarea.value = textarea.value.substring(0, lineStart) + textarea.value.substring(lineStart + spaces[0].length);
                textarea.selectionStart = textarea.selectionEnd = start - spaces[0].length;
            }
        } else {
            textarea.value = textarea.value.substring(0, start) + '    ' + textarea.value.substring(end);
            textarea.selectionStart = textarea.selectionEnd = start + 4;
        }
        handleEditorInput();
    }

    // Enter key → auto-indent
    if (e.key === 'Enter') {
        e.preventDefault();
        const start = textarea.selectionStart;
        const lineStart = textarea.value.lastIndexOf('\n', start - 1) + 1;
        const currentLine = textarea.value.substring(lineStart, start);
        const indent = currentLine.match(/^\s*/)[0];

        // If line ends with {, add extra indent
        const trimmed = currentLine.trimEnd();
        let extra = '';
        if (trimmed.endsWith('{')) {
            extra = '    ';
        }

        const insertion = '\n' + indent + extra;
        textarea.value = textarea.value.substring(0, start) + insertion + textarea.value.substring(textarea.selectionEnd);
        textarea.selectionStart = textarea.selectionEnd = start + insertion.length;
        handleEditorInput();
    }

    // Auto-close brackets
    const bracketPairs = { '{': '}', '(': ')', '[': ']', '"': '"', "'": "'" };
    if (bracketPairs[e.key] && !e.ctrlKey && !e.altKey) {
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        // Only auto-close if nothing selected
        if (start === end) {
            e.preventDefault();
            const closing = bracketPairs[e.key];
            textarea.value = textarea.value.substring(0, start) + e.key + closing + textarea.value.substring(end);
            textarea.selectionStart = textarea.selectionEnd = start + 1;
            handleEditorInput();
        }
    }
}

function handleEditorClick() {
    updateLineNumbers();
    updateStatusBar();
    if (State.explanationMode === 'line') {
        handleCursorMove();
    }
}

function updateStatusBar() {
    const line = getCursorLineNumber();
    const col = getCursorColumn();
    const statusCursor = document.getElementById('statusCursor');
    if (statusCursor) {
        statusCursor.querySelector('span').textContent = `Ln ${line}, Col ${col}`;
    }
}

function updateTitleBar() {
    const tab = State.tabs.get(State.activeTabId);
    if (!tab) return;

    const titleText = document.getElementById('titleFileText');
    const unsavedDot = document.getElementById('titleUnsavedDot');

    if (titleText) titleText.textContent = tab.name;
    if (unsavedDot) unsavedDot.style.display = tab.dirty ? 'inline' : 'none';

    document.title = (tab.dirty ? '● ' : '') + tab.name + ' — Sensei';
}


// ============================================================================
// 6. EXPLANATION ENGINE
// ============================================================================

function toggleExplainMode() {
    if (State.explanationMode === 'line') {
        State.explanationMode = 'idle';
        updateExplanationUI();
        // Remove active state from explain button
        document.getElementById('lineExplain')?.classList.remove('explain-active');
    } else {
        State.explanationMode = 'line';
        updateExplanationUI();
        handleCursorMove();
        document.getElementById('lineExplain')?.classList.add('explain-active');

        // Force open right panel showing explanations
        showRightPanelView('explain');
    }
}

function updateExplanationUI() {
    const idleEl = document.getElementById('explainIdle');
    const lineEl = document.getElementById('lineExplanations');

    if (State.explanationMode === 'idle') {
        if (idleEl) idleEl.style.display = 'flex';
        if (lineEl) lineEl.style.display = 'none';
    } else {
        if (idleEl) idleEl.style.display = 'none';
        if (lineEl) lineEl.style.display = 'block';
    }
}

async function handleCursorMove() {
    if (State.explanationMode !== 'line') return;

    const container = document.getElementById('lineExplanations');
    if (!container) return;

    const currentLineNum = getCursorLineNumber();
    const code = getEditorCode();
    const lines = code.split('\n');
    const lineContent = lines[currentLineNum - 1]?.trim();

    if (State.explainTimeout) clearTimeout(State.explainTimeout);

    if (!lineContent || lineContent.startsWith('//') || lineContent.length < 2) {
        container.innerHTML = `<div class="explain-idle" style="height:auto; padding: 20px;">
            <p>Line ${currentLineNum} — waiting for code...</p>
        </div>`;
        return;
    }

    State.explainTimeout = setTimeout(async () => {
        container.innerHTML = `<div class="explain-card" style="border-left-color: var(--warning);">
            <div class="explain-card-body"><span class="message-loading"><span class="dot"></span><span class="dot"></span><span class="dot"></span></span> Analyzing line ${currentLineNum}...</div>
        </div>`;

        try {
            const response = await fetch('http://localhost:8000/explain', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ line: lineContent })
            });
            const data = await response.json();

            const safeSummary = data.summary
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;")
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

            const safeDetail = data.detail
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;")
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\n/g, '<br>');

            const codePreview = lineContent.length > 50 ? lineContent.substring(0, 50) + '...' : lineContent;

            const bodyHtml = `<p style="font-size: var(--font-size-sm); line-height: 1.5; color: var(--text-active);"><strong>${safeSummary}</strong></p>
                            <p style="margin-top: 8px; color: var(--text-primary); line-height: 1.5; font-size: var(--font-size-sm);">${safeDetail}</p>
                            ${data.url ? `<a href="${data.url}" target="_blank" class="explain-card-link" style="margin-top: 10px; display: inline-flex; align-items: center; gap: 4px; color: var(--text-link); text-decoration: none; font-size: var(--font-size-xs);">
                                <i data-lucide="external-link" style="width: 12px; height: 12px;"></i> Read C++ Documentation
                            </a>` : ''}`;

            container.innerHTML = `<div class="explain-card">
                <div class="explain-card-header">
                    <span class="explain-line-badge">Line ${currentLineNum}</span>
                    <span class="explain-line-code">${escapeHtml(codePreview)}</span>
                </div>
                <div class="explain-card-body">${bodyHtml}</div>
            </div>`;
            initLucide();
        } catch (error) {
            container.innerHTML = `<div class="explain-card" style="border-left-color: var(--danger);">
                <div class="explain-card-body" style="color: var(--danger);">Error: ${error.message}. Is the server running?</div>
            </div>`;
        }
    }, 300);
}


// ============================================================================
// 7. AI ASSISTANT
// ============================================================================

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    addChatMessage(message, 'user');
    input.value = '';

    // Add loading
    const loadingId = 'loading-' + Date.now();
    addChatMessage(null, 'ai', loadingId, true);

    try {
        const response = await fetch('http://localhost:8000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        const data = await response.json();

        // Remove loading
        const loadingEl = document.getElementById(loadingId);
        if (loadingEl) loadingEl.remove();

        addChatMessage(data.response, 'ai');
    } catch (e) {
        const loadingEl = document.getElementById(loadingId);
        if (loadingEl) loadingEl.remove();
        addChatMessage('Error connecting to AI: ' + e.message, 'ai');
    }
}

function addChatMessage(content, sender, id = null, isLoading = false) {
    const container = document.getElementById('chatMessages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${sender}-message`;
    if (id) msgDiv.id = id;

    const avatarIcon = sender === 'ai' ? 'bot' : 'user';

    if (isLoading) {
        msgDiv.innerHTML = `
            <div class="message-avatar"><i data-lucide="${avatarIcon}"></i></div>
            <div class="message-content">
                <div class="message-loading"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>
            </div>`;
    } else {
        const rendered = sender === 'ai' ? renderMarkdown(content) : `<p>${escapeHtml(content)}</p>`;
        msgDiv.innerHTML = `
            <div class="message-avatar"><i data-lucide="${avatarIcon}"></i></div>
            <div class="message-content">${rendered}</div>`;
    }

    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
    initLucide();
}

function renderMarkdown(text) {
    if (!text) return '<p></p>';

    // Escape HTML first
    let html = escapeHtml(text);

    // Code blocks (```...```)
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
        return `<pre><code>${code.trim()}</code><button class="copy-code-btn" onclick="copyCodeBlock(this)">Copy</button></pre>`;
    });

    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Italic
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Lists
    html = html.replace(/^\s*[-*]\s+(.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

    // Numbered lists
    html = html.replace(/^\s*\d+\.\s+(.+)$/gm, '<li>$1</li>');

    // Paragraphs
    html = html.split('\n\n').map(p => {
        p = p.trim();
        if (!p) return '';
        if (p.startsWith('<pre>') || p.startsWith('<ul>') || p.startsWith('<ol>') || p.startsWith('<li>')) return p;
        return `<p>${p.replace(/\n/g, '<br>')}</p>`;
    }).join('');

    return html || '<p></p>';
}

function copyCodeBlock(btn) {
    const pre = btn.closest('pre');
    const code = pre.querySelector('code');
    navigator.clipboard.writeText(code.textContent).then(() => {
        btn.textContent = 'Copied!';
        setTimeout(() => { btn.textContent = 'Copy'; }, 1500);
    });
}

async function loadStarterCode(type) {
    try {
        const response = await fetch(`http://localhost:8000/starter-code/${type}`);
        const data = await response.json();

        setEditorCode(data.code);
        checkEditorEmptyState();
        TabManager.markDirty(State.activeTabId);
        showToast('Loaded', `${type} starter code inserted`);
    } catch (e) {
        showToast('Error', 'Failed to load starter code');
    }
}

function handleQuickAction(action) {
    const codeContext = getEditorCode();

    const actions = {
        'step-by-step': 'Can you explain this C++ code step by step?\n\n```cpp\n' + codeContext + '\n```',
        'optimize': 'How can I optimize this C++ code?\n\n```cpp\n' + codeContext + '\n```',
        'find-errors': 'Are there any errors or issues in this C++ code?\n\n```cpp\n' + codeContext + '\n```',
        'starter-io': null,
        'starter-array': null,
        'starter-string': null,
    };

    if (action.startsWith('starter-')) {
        loadStarterCode(action.replace('starter-', ''));
        return;
    }

    const message = actions[action];
    if (message) {
        document.getElementById('chatInput').value = message;
        sendMessage();
    }
}


// ============================================================================
// 8. TERMINAL / CONSOLE
// ============================================================================

async function handleRunCode() {
    const code = getEditorCode();
    const consoleOutput = document.getElementById('consoleOutput');
    const consoleInput = document.getElementById('consoleInput');

    // Show terminal panel
    showBottomPanel();

    // Clear output
    consoleOutput.innerHTML = '';
    consoleInput.value = '';

    // Close existing socket
    if (State.socket) {
        State.socket.close();
    }

    appendToTerminal('Compiling and running...\n', 'compile-msg');

    try {
        State.socket = new WebSocket('ws://localhost:8000/ws/run');

        State.socket.onopen = function () {
            State.socket.send(JSON.stringify({ code: code }));
            updateConnectionStatus(true);
        };

        State.socket.onmessage = function (event) {
            appendToTerminal(event.data);
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
        };

        State.socket.onclose = function () {
            appendToTerminal('\n[Disconnected]', 'compile-msg');
            updateConnectionStatus(false);
        };

        State.socket.onerror = function () {
            appendToTerminal('\n[Connection Error]', 'error-msg');
            updateConnectionStatus(false);
        };
    } catch (e) {
        appendToTerminal('Error connecting: ' + e.message, 'error-msg');
    }
}

function sendConsoleInput() {
    const inputField = document.getElementById('consoleInput');
    const text = inputField.value;

    if (State.socket && State.socket.readyState === WebSocket.OPEN) {
        State.socket.send(text);
        appendToTerminal(text + '\n', 'success-msg');
        inputField.value = '';
    } else {
        showToast('Error', 'Program is not running');
    }
}

function appendToTerminal(text, className = '') {
    const output = document.getElementById('consoleOutput');
    if (!output) return;

    if (className) {
        const span = document.createElement('span');
        span.className = className;
        span.textContent = text;
        output.appendChild(span);
    } else {
        output.appendChild(document.createTextNode(text));
    }
    output.scrollTop = output.scrollHeight;
}

function clearTerminal() {
    const output = document.getElementById('consoleOutput');
    if (output) {
        output.innerHTML = '<span class="compile-msg">Terminal cleared.</span>\n';
    }
}

function updateConnectionStatus(connected) {
    const statusEl = document.getElementById('statusConnection');
    if (!statusEl) return;
    const icon = statusEl.querySelector('.status-icon');
    const text = statusEl.querySelector('span:last-child');
    if (connected) {
        icon.style.color = '#4ec9b0';
        text.textContent = 'Connected';
    } else {
        icon.style.color = '#858585';
        text.textContent = 'Disconnected';
    }
}


// ============================================================================
// 9. KEYBOARD SHORTCUTS
// ============================================================================

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function (e) {
        const key = e.key.toLowerCase();
        const ctrl = e.ctrlKey || e.metaKey;
        const shift = e.shiftKey;

        // Ctrl+S — Save
        if (ctrl && key === 's' && !shift) {
            e.preventDefault();
            saveCurrentFile();
        }

        // Ctrl+Shift+S — Save As
        if (ctrl && shift && key === 's') {
            e.preventDefault();
            saveFileAs();
        }

        // Ctrl+Enter — Run
        if (ctrl && key === 'enter') {
            e.preventDefault();
            handleRunCode();
        }

        // F5 — Run
        if (key === 'f5') {
            e.preventDefault();
            handleRunCode();
        }

        // Ctrl+B — Toggle Sidebar
        if (ctrl && key === 'b' && !shift) {
            e.preventDefault();
            toggleSidebar();
        }

        // Ctrl+` — Toggle Terminal
        if (ctrl && key === '`') {
            e.preventDefault();
            toggleBottomPanel();
        }

        // Ctrl+J — Toggle Bottom Panel
        if (ctrl && key === 'j' && !shift) {
            e.preventDefault();
            toggleBottomPanel();
        }

        // Ctrl+Shift+A — Toggle AI Panel
        if (ctrl && shift && key === 'a') {
            e.preventDefault();
            toggleRightPanel('ai');
        }

        // Ctrl+Shift+E — Focus Explorer
        if (ctrl && shift && key === 'e') {
            e.preventDefault();
            showSidebarView('explorer');
        }

        // Ctrl+N — New file
        if (ctrl && key === 'n' && !shift) {
            e.preventDefault();
            FileExplorer.createFile();
        }

        // Ctrl+/ — Toggle comment
        if (ctrl && key === '/') {
            e.preventDefault();
            toggleComment();
        }

        // Escape — close menus, context menu
        if (key === 'escape') {
            closeAllMenus();
            document.getElementById('contextMenu')?.classList.remove('active');
        }
    });
}

function toggleComment() {
    if (window.editor) {
        window.editor.trigger('keyboard', 'editor.action.commentLine', null);
        return;
    }
    const textarea = document.getElementById('codeTextarea');
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const value = textarea.value;

    const lineStart = value.lastIndexOf('\n', start - 1) + 1;
    const lineEnd = value.indexOf('\n', end);
    const actualEnd = lineEnd === -1 ? value.length : lineEnd;

    const line = value.substring(lineStart, actualEnd);
    const trimmed = line.trimStart();

    let newLine;
    if (trimmed.startsWith('//')) {
        // Uncomment
        newLine = line.replace(/\/\/\s?/, '');
    } else {
        // Comment
        const leadingSpaces = line.match(/^\s*/)[0];
        newLine = leadingSpaces + '// ' + trimmed;
    }

    textarea.value = value.substring(0, lineStart) + newLine + value.substring(actualEnd);
    textarea.selectionStart = lineStart;
    textarea.selectionEnd = lineStart + newLine.length;
    handleEditorInput();
}


// ============================================================================
// 10. PANEL MANAGEMENT
// ============================================================================

function toggleSidebar() {
    State.sidebarVisible = !State.sidebarVisible;
    const container = document.getElementById('ideContainer');
    container.classList.toggle('sidebar-hidden', !State.sidebarVisible);

    // Update activity bar button
    document.getElementById('actExplorer')?.classList.toggle('active', State.sidebarVisible);
}

function showSidebarView(view) {
    State.sidebarVisible = true;
    const container = document.getElementById('ideContainer');
    container.classList.remove('sidebar-hidden');
    document.getElementById('actExplorer')?.classList.add('active');
}

function toggleRightPanel(view = 'ai') {
    const container = document.getElementById('ideContainer');

    if (State.rightPanelVisible && State.rightPanelView === view) {
        // Collapse
        State.rightPanelVisible = false;
        container.classList.add('right-panel-hidden');

        // Deactivate activity bar buttons
        document.getElementById('actAI')?.classList.remove('active');
        document.getElementById('actExplain')?.classList.remove('active');
    } else {
        // Show or switch
        showRightPanelView(view);
    }
}

function showRightPanelView(view) {
    State.rightPanelView = view;
    State.rightPanelVisible = true;

    const container = document.getElementById('ideContainer');
    container.classList.remove('right-panel-hidden');

    const aiView = document.getElementById('aiAssistantView');
    const explainView = document.getElementById('explainView');

    if (view === 'ai') {
        if (aiView) aiView.style.display = 'flex';
        if (explainView) explainView.style.display = 'none';
    } else if (view === 'explain') {
        if (aiView) aiView.style.display = 'none';
        if (explainView) explainView.style.display = 'flex';
    }

    // Update activity bar active status
    document.getElementById('actAI')?.classList.toggle('active', view === 'ai');
    document.getElementById('actExplain')?.classList.toggle('active', view === 'explain');
}

function toggleBottomPanel() {
    State.bottomPanelVisible = !State.bottomPanelVisible;
    const panel = document.getElementById('panelBottom');
    panel.classList.toggle('collapsed', !State.bottomPanelVisible);
}

function showBottomPanel() {
    State.bottomPanelVisible = true;
    const panel = document.getElementById('panelBottom');
    panel.classList.remove('collapsed');
}


// ============================================================================
// PANEL RESIZE
// ============================================================================

function setupPanelResize() {
    // Sidebar resize
    const sidebarResize = document.getElementById('sidebarResize');
    if (sidebarResize) {
        setupResize(sidebarResize, 'sidebar', 'horizontal');
    }

    // Bottom panel resize
    const bottomResize = document.getElementById('panelBottomResize');
    if (bottomResize) {
        setupResize(bottomResize, 'bottom', 'vertical');
    }

    // Right panel resize
    const rightResize = document.getElementById('panelRightResize');
    if (rightResize) {
        setupResize(rightResize, 'right', 'horizontal');
    }
}

function setupResize(handle, target, direction) {
    let startPos = 0;
    let startSize = 0;

    const onMouseDown = (e) => {
        e.preventDefault();
        State.isResizing = true;
        State.resizeTarget = target;
        handle.classList.add('active');
        document.body.classList.add('is-resizing');
        document.body.style.cursor = direction === 'horizontal' ? 'col-resize' : 'row-resize';
        document.body.style.userSelect = 'none';

        if (direction === 'horizontal') {
            startPos = e.clientX;
            if (target === 'sidebar') {
                startSize = document.getElementById('sidebar').offsetWidth;
            } else if (target === 'right') {
                startSize = document.getElementById('panelRight').offsetWidth;
            }
        } else {
            startPos = e.clientY;
            startSize = document.getElementById('panelBottom').offsetHeight;
        }

        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    };

    const onMouseMove = (e) => {
        if (!State.isResizing) return;

        if (direction === 'horizontal') {
            const diff = e.clientX - startPos;
            let newSize;

            if (target === 'sidebar') {
                newSize = Math.max(170, Math.min(500, startSize + diff));
                document.getElementById('sidebar').style.width = newSize + 'px';
                State.sidebarWidth = newSize;
            } else if (target === 'right') {
                newSize = Math.max(260, Math.min(600, startSize - diff));
                document.getElementById('panelRight').style.width = newSize + 'px';
                State.rightPanelWidth = newSize;
            }
        } else {
            const diff = startPos - e.clientY;
            const newSize = Math.max(120, Math.min(500, startSize + diff));
            document.getElementById('panelBottom').style.height = newSize + 'px';
            State.bottomPanelHeight = newSize;
        }
    };

    const onMouseUp = () => {
        State.isResizing = false;
        State.resizeTarget = null;
        handle.classList.remove('active');
        document.body.classList.remove('is-resizing');
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
    };

    handle.addEventListener('mousedown', onMouseDown);
}


// ============================================================================
// 11. MENU SYSTEM
// ============================================================================

function setupMenuSystem() {
    const menus = {
        'menuFile': 'fileMenuDropdown',
        'menuView': 'viewMenuDropdown',
        'menuRun': 'runMenuDropdown',
        'menuHelp': 'helpMenuDropdown',
    };

    Object.entries(menus).forEach(([btnId, menuId]) => {
        const btn = document.getElementById(btnId);
        const menu = document.getElementById(menuId);
        if (!btn || !menu) return;

        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = menu.classList.contains('active');
            closeAllMenus();
            if (!isOpen) {
                menu.style.left = btn.getBoundingClientRect().left + 'px';
                menu.classList.add('active');
            }
        });
    });

    // Close menus on outside click
    document.addEventListener('click', () => {
        closeAllMenus();
        document.getElementById('contextMenu')?.classList.remove('active');
    });

    // Menu actions
    document.getElementById('menuNewFile')?.addEventListener('click', () => { closeAllMenus(); FileExplorer.createFile(); });
    document.getElementById('menuOpenFile')?.addEventListener('click', () => { closeAllMenus(); openFileDialog(); });
    document.getElementById('menuOpenFolder')?.addEventListener('click', () => { closeAllMenus(); FileExplorer.openFolder(); });
    document.getElementById('menuSave')?.addEventListener('click', () => { closeAllMenus(); saveCurrentFile(); });
    document.getElementById('menuSaveAs')?.addEventListener('click', () => { closeAllMenus(); saveFileAs(); });
    document.getElementById('menuDownload')?.addEventListener('click', () => { closeAllMenus(); handleDownloadCode(); });
    document.getElementById('menuToggleSidebar')?.addEventListener('click', () => { closeAllMenus(); toggleSidebar(); });
    document.getElementById('menuToggleTerminal')?.addEventListener('click', () => { closeAllMenus(); toggleBottomPanel(); });
    document.getElementById('menuToggleAI')?.addEventListener('click', () => { closeAllMenus(); toggleRightPanel(); });
    document.getElementById('menuToggleTheme')?.addEventListener('click', () => { closeAllMenus(); toggleTheme(); });
    document.getElementById('menuRunCode')?.addEventListener('click', () => { closeAllMenus(); handleRunCode(); });

    // Context menu actions
    document.querySelectorAll('#contextMenu .context-menu-item').forEach(item => {
        item.addEventListener('click', () => {
            const action = item.dataset.action;
            const menu = document.getElementById('contextMenu');
            menu.classList.remove('active');

            if (action === 'new-file') FileExplorer.createFile();
            if (action === 'new-folder') FileExplorer.createFolder();
            // rename/delete would need the target item reference
        });
    });
}

function closeAllMenus() {
    document.querySelectorAll('.menu-dropdown').forEach(m => m.classList.remove('active'));
}

async function openFileDialog() {
    try {
        if ('showOpenFilePicker' in window) {
            const [fileHandle] = await window.showOpenFilePicker({
                types: [{
                    description: 'C++ Files',
                    accept: { 'text/x-c++src': ['.cpp', '.cc', '.cxx', '.h', '.hpp'] }
                }, {
                    description: 'All Files',
                    accept: { 'text/plain': ['*'] }
                }]
            });
            const file = await fileHandle.getFile();
            const content = await file.text();
            const tabId = 'file-' + file.name.replace(/[^a-zA-Z0-9]/g, '-') + '-' + Date.now();
            TabManager.openTab(tabId, file.name, content, fileHandle);
        } else {
            // Fallback: use hidden file input
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.cpp,.cc,.cxx,.h,.hpp,.c,.txt';
            input.onchange = async (e) => {
                const file = e.target.files[0];
                if (file) {
                    const content = await file.text();
                    const tabId = 'file-' + file.name.replace(/[^a-zA-Z0-9]/g, '-') + '-' + Date.now();
                    TabManager.openTab(tabId, file.name, content, null);
                }
            };
            input.click();
        }
    } catch (e) {
        if (e.name !== 'AbortError') {
            showToast('Error', 'Failed to open file: ' + e.message);
        }
    }
}

async function saveCurrentFile() {
    const tab = State.tabs.get(State.activeTabId);
    if (!tab) return;

    // Save current textarea content
    tab.content = getEditorCode();

    if (tab.fileHandle) {
        try {
            const writable = await tab.fileHandle.createWritable();
            await writable.write(tab.content);
            await writable.close();
            TabManager.markClean(State.activeTabId);
            showToast('Saved', tab.name);
        } catch (e) {
            showToast('Error', 'Failed to save: ' + e.message);
        }
    } else {
        // No file handle — save as
        await saveFileAs();
    }
}

async function saveFileAs() {
    const tab = State.tabs.get(State.activeTabId);
    if (!tab) return;

    tab.content = getEditorCode();

    try {
        if ('showSaveFilePicker' in window) {
            const fileHandle = await window.showSaveFilePicker({
                suggestedName: tab.name,
                types: [{
                    description: 'C++ Source',
                    accept: { 'text/x-c++src': ['.cpp'] }
                }]
            });
            const writable = await fileHandle.createWritable();
            await writable.write(tab.content);
            await writable.close();

            tab.fileHandle = fileHandle;
            tab.name = fileHandle.name;
            TabManager.markClean(State.activeTabId);
            TabManager.renderTabs();
            updateTitleBar();
            showToast('Saved', tab.name);
        } else {
            // Fallback download
            handleDownloadCode();
        }
    } catch (e) {
        if (e.name !== 'AbortError') {
            showToast('Error', 'Failed to save: ' + e.message);
        }
    }
}


// ============================================================================
// 12. THEME
// ============================================================================

function initTheme() {
    const savedTheme = localStorage.getItem('sensei-theme');
    if (savedTheme === 'light') {
        document.body.classList.remove('dark-mode');
        document.body.classList.add('light-mode');
        State.isDarkMode = false;
    } else {
        document.body.classList.remove('light-mode');
        document.body.classList.add('dark-mode');
        State.isDarkMode = true;
    }
}

function toggleTheme() {
    State.isDarkMode = !State.isDarkMode;
    document.body.classList.toggle('dark-mode', State.isDarkMode);
    document.body.classList.toggle('light-mode', !State.isDarkMode);
    localStorage.setItem('sensei-theme', State.isDarkMode ? 'dark' : 'light');
}


// ============================================================================
// 13. NOTIFICATIONS
// ============================================================================

function showToast(title, description) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `
        <div class="toast-header">${escapeHtml(title)}</div>
        <div class="toast-description">${escapeHtml(description || '')}</div>
    `;
    container.appendChild(toast);

    setTimeout(() => {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 2500);
}


// ============================================================================
// 14. UTILITIES
// ============================================================================

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function handleCopyCode() {
    const code = getEditorCode();
    navigator.clipboard.writeText(code).then(() => {
        showToast('Copied', 'Code copied to clipboard');
    });
}

function handleDownloadCode() {
    const tab = State.tabs.get(State.activeTabId);
    const code = getEditorCode();
    const element = document.createElement('a');
    const file = new Blob([code], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = tab ? tab.name : 'code.cpp';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    showToast('Downloaded', element.download);
}

async function checkServerConnection() {
    try {
        const response = await fetch('http://localhost:8000/explain', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ line: 'int x;' })
        });
        if (response.ok) {
            updateConnectionStatus(true);
        }
    } catch (e) {
        updateConnectionStatus(false);
    }
}


// ============================================================================
// EVENT LISTENERS SETUP
// ============================================================================

function setupEventListeners() {
    // Editor
    const textarea = document.getElementById('codeTextarea');
    if (textarea) {
        textarea.addEventListener('input', handleEditorInput);
        textarea.addEventListener('keydown', handleEditorKeydown);
        textarea.addEventListener('scroll', syncLineNumbersScroll);
        textarea.addEventListener('click', handleEditorClick);
        textarea.addEventListener('keyup', handleEditorClick);
    }

    // Run button
    document.getElementById('runCode')?.addEventListener('click', handleRunCode);

    // Explain button
    document.getElementById('lineExplain')?.addEventListener('click', toggleExplainMode);

    // Copy / Download
    document.getElementById('copyCode')?.addEventListener('click', handleCopyCode);
    document.getElementById('downloadCode')?.addEventListener('click', handleDownloadCode);

    // Theme toggle
    document.getElementById('themeToggle')?.addEventListener('click', toggleTheme);

    // Console input
    document.getElementById('consoleInput')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendConsoleInput();
    });

    // Terminal actions
    document.getElementById('clearTerminal')?.addEventListener('click', clearTerminal);
    document.getElementById('closePanel')?.addEventListener('click', toggleBottomPanel);

    // AI Chat
    document.getElementById('sendButton')?.addEventListener('click', sendMessage);
    document.getElementById('chatInput')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Right panel close buttons
    document.getElementById('closeAIPanel')?.addEventListener('click', () => toggleRightPanel('ai'));
    document.getElementById('closeExplainPanel')?.addEventListener('click', () => toggleRightPanel('explain'));

    // Onboarding starter buttons
    document.getElementById('btnStartBlank')?.addEventListener('click', () => {
        if (State.tabs.size === 0) {
            TabManager.createTab();
        }
        setEditorCode('// Start coding here...\n');
        document.getElementById('emptyStateView').style.display = 'none';
        if (window.editor) window.editor.focus();
    });

    document.getElementById('btnOpenFolderEmpty')?.addEventListener('click', () => {
        FileExplorer.openFolder();
    });

    // Quick action suggestions
    document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            handleQuickAction(chip.dataset.action);
        });
    });

    // Activity bar
    document.getElementById('actExplorer')?.addEventListener('click', () => {
        toggleSidebar();
    });

    document.getElementById('actExplain')?.addEventListener('click', () => {
        toggleRightPanel('explain');
        if (State.rightPanelVisible && State.rightPanelView === 'explain') {
            if (State.explanationMode !== 'line') {
                toggleExplainMode();
            }
        }
    });

    document.getElementById('actAI')?.addEventListener('click', () => toggleRightPanel('ai'));

    document.getElementById('actSettings')?.addEventListener('click', () => {
        showToast('Settings', 'Settings panel coming soon!');
    });

    // File explorer buttons
    document.getElementById('btnOpenFolder')?.addEventListener('click', () => FileExplorer.openFolder());
    document.getElementById('btnNewFile')?.addEventListener('click', () => {
        const name = prompt('File name:', 'new_file.cpp');
        if (name) FileExplorer.createFile(name);
    });
    document.getElementById('btnNewFolder')?.addEventListener('click', () => {
        const name = prompt('Folder name:', 'new_folder');
        if (name) FileExplorer.createFolder(name);
    });
    document.getElementById('btnRefreshTree')?.addEventListener('click', () => {
        if (State.folderHandle) FileExplorer.readDirectory(State.folderHandle);
    });

}

// ============================================================================
// 15. MONACO EDITOR & STARTER SNIPPETS
// ============================================================================

const StarterSnippets = [
    {
        id: 'hello_world',
        title: 'Hello World',
        icon: 'terminal',
        desc: 'Print text to the console. The absolute first step in C++.',
        code: `// C++ Basic Input/Output (Hello World)
#include <iostream>
using namespace std;
int main() {
    // Print message to console
    cout << "Hello, World!" <<endl;
    return 0;
}`
    },
    {
        id: 'arithmetic',
        title: 'Arithmetic Operations',
        icon: 'plus',
        desc: 'Addition, subtraction, multiplication, and division.',
        code: `// C++ Arithmetic Operations
#include <iostream>

int main() {
    int a = 15;
    int b = 4;
    
    std::cout << "Numbers: a = " << a << ", b = " << b << std::endl;
    std::cout << "Addition (a + b): " << (a + b) << std::endl;
    std::cout << "Subtraction (a - b): " << (a - b) << std::endl;
    std::cout << "Multiplication (a * b): " << (a * b) << std::endl;
    std::cout << "Division (a / b): " << (a / b) << " (integer)" << std::endl;
    std::cout << "Modulo (a % b): " << (a % b) << " (remainder)" << std::endl;
    
    return 0;
}`
    },
    {
        id: 'even_odd',
        title: 'Even or Odd Check',
        icon: 'help-circle',
        desc: 'Check if a number is even or odd using if-else and modulo.',
        code: `// C++ If-Else (Even/Odd Check)
#include <iostream>

int main() {
    int number;
    std::cout << "Enter an integer to check: ";
    std::cin >> number;
    
    // Check if number is divisible by 2
    if (number % 2 == 0) {
        std::cout << number << " is EVEN." << std::endl;
    } else {
        std::cout << number << " is ODD." << std::endl;
    }
    
    return 0;
}`
    },
    {
        id: 'loops_for',
        title: 'For Loop (Count 1-10)',
        icon: 'repeat',
        desc: 'Repeat code a specific number of times using a for loop.',
        code: `// C++ For Loop (Counting)
#include <iostream>

int main() {
    std::cout << "Counting from 1 to 10:" << std::endl;
    
    // Loop runs from 1 to 10
    for (int i = 1; i <= 10; i++) {
        std::cout << i << " ";
    }
    std::cout << std::endl;
    
    return 0;
}`
    },
    {
        id: 'loops_while',
        title: 'While Loop (Factorial)',
        icon: 'refresh-cw',
        desc: 'Calculate the factorial of a number using a while loop.',
        code: `// C++ While Loop (Factorial)
#include <iostream>

int main() {
    int n = 5;
    long long factorial = 1;
    int i = 1;
    
    while (i <= n) {
        factorial *= i;
        i++;
    }
    
    std::cout << "Factorial of " << n << " is " << factorial << std::endl;
    return 0;
}`
    },
    {
        id: 'calculator',
        title: 'Simple Calculator',
        icon: 'calculator',
        desc: 'Perform basic math using switch statements and user input.',
        code: `// C++ Simple Calculator
#include <iostream>

int main() {
    char op;
    double num1, num2;
    
    std::cout << "Enter operator (+, -, *, /): ";
    std::cin >> op;
    std::cout << "Enter two numbers: ";
    std::cin >> num1 >> num2;
    
    switch(op) {
        case '+':
            std::cout << num1 << " + " << num2 << " = " << (num1 + num2) << std::endl;
            break;
        case '-':
            std::cout << num1 << " - " << num2 << " = " << (num1 - num2) << std::endl;
            break;
        case '*':
            std::cout << num1 << " * " << num2 << " = " << (num1 * num2) << std::endl;
            break;
        case '/':
            if (num2 != 0)
                std::cout << num1 << " / " << num2 << " = " << (num1 / num2) << std::endl;
            else
                std::cout << "Error: Division by zero!" << std::endl;
            break;
        default:
            std::cout << "Error: Invalid operator!" << std::endl;
    }
    
    return 0;
}`
    },
    {
        id: 'arrays',
        title: 'Arrays & Max Value',
        icon: 'list',
        desc: 'Store a list of numbers and find the maximum value.',
        code: `// C++ Arrays (Find Maximum)
#include <iostream>

int main() {
    int numbers[5] = {12, 45, 8, 23, 31};
    int max = numbers[0];
    
    std::cout << "Array elements: ";
    for (int i = 0; i < 5; i++) {
        std::cout << numbers[i] << " ";
        if (numbers[i] > max) {
            max = numbers[i];
        }
    }
    
    std::cout << "\\nMaximum value in the array: " << max << std::endl;
    return 0;
}`
    },
    {
        id: 'strings',
        title: 'Strings & User Name',
        icon: 'type',
        desc: 'Get string input and manipulate text in C++.',
        code: `// C++ Strings
#include <iostream>
#include <string>
using namespace std;
int main() {
    string name;
    
    cout << "What is your name? ";
    getline(cin, name);
    
    cout << "Hello, " << name << "! Welcome to Sensei IDE." << endl;
    cout << "Your name is " << name.length() << " characters long." << endl;
    
    return 0;
}`
    },
    {
        id: 'fibonacci',
        title: 'Fibonacci Series',
        icon: 'trending-up',
        desc: 'Generate Fibonacci numbers using a loop.',
        code: `// C++ Fibonacci Series
#include <iostream>

int main() {
    int terms = 10;
    int t1 = 0, t2 = 1, nextTerm = 0;
    
    std::cout << "Fibonacci Series (10 terms): " << std::endl;
    for (int i = 1; i <= terms; ++i) {
        std::cout << t1 << " ";
        nextTerm = t1 + t2;
        t1 = t2;
        t2 = nextTerm;
    }
    std::cout << std::endl;
    
    return 0;
}`
    },
    {
        id: 'star_pattern',
        title: 'Star Pattern (Triangle)',
        icon: 'triangle',
        desc: 'Print a right-angled triangle pattern of stars using nested loops.',
        code: `// C++ Star Pattern (Triangle)
#include <iostream>

int main() {
    int rows = 5;
    
    for(int i = 1; i <= rows; ++i) {
        for(int j = 1; j <= i; ++j) {
            std::cout << "* ";
        }
        std::cout << std::endl;
    }
    
    return 0;
}`
    }
];

function getEditorCode() {
    if (window.editor) {
        return window.editor.getValue();
    }
    return document.getElementById('codeTextarea')?.value || '';
}

function setEditorCode(value) {
    if (window.editor) {
        window.editor.setValue(value);
    } else {
        const el = document.getElementById('codeTextarea');
        if (el) el.value = value;
    }
    handleEditorInput();
}

function checkEditorEmptyState() {
    const emptyStateView = document.getElementById('emptyStateView');
    if (!emptyStateView) return;

    const hasTabs = State.tabs.size > 0;
    const currentCode = getEditorCode();

    if (!hasTabs) {
        emptyStateView.style.display = 'flex';
        document.getElementById('templateGrid').style.display = 'none';
        document.getElementById('emptyStateSubtitle').innerText = 'Get started by creating a new file or opening a folder.';
        document.getElementById('btnStartBlank').style.display = 'none';
        return;
    }

    const isCleanEmpty = currentCode.trim() === '' ||
        currentCode.trim() === '// Welcome to Sensei!' ||
        currentCode.trim().startsWith('// Start coding here') ||
        currentCode.trim().startsWith('// C++ Basic Input/Output') ||
        currentCode.trim().startsWith('// C++ Arithmetic') ||
        currentCode.trim().startsWith('// C++ If-Else') ||
        currentCode.trim().startsWith('// C++ For Loop') ||
        currentCode.trim().startsWith('// C++ While Loop') ||
        currentCode.trim().startsWith('// C++ Simple Calculator') ||
        currentCode.trim().startsWith('// C++ Arrays') ||
        currentCode.trim().startsWith('// C++ Strings') ||
        currentCode.trim().startsWith('// C++ Fibonacci') ||
        currentCode.trim().startsWith('// C++ Star Pattern') ||
        (currentCode.includes('int main()') && currentCode.length < 300 && currentCode.includes('Enter a number:'));

    if (isCleanEmpty) {
        emptyStateView.style.display = 'flex';
        document.getElementById('templateGrid').style.display = 'grid';
        document.getElementById('emptyStateSubtitle').innerText = 'Select a beginner C++ template below to load example code instantly.';
        document.getElementById('btnStartBlank').style.display = 'block';
    } else {
        emptyStateView.style.display = 'none';
    }
}

function renderStarterTemplates() {
    const grid = document.getElementById('templateGrid');
    if (!grid) return;

    grid.innerHTML = StarterSnippets.map(snippet => {
        return `
            <div class="template-card" data-snippet-id="${snippet.id}">
                <div class="template-card-title">
                    <i data-lucide="${snippet.icon}"></i>
                    ${snippet.title}
                </div>
                <div class="template-card-desc">${snippet.desc}</div>
            </div>
        `;
    }).join('');

    grid.querySelectorAll('.template-card').forEach(card => {
        card.addEventListener('click', () => {
            const snippetId = card.getAttribute('data-snippet-id');
            const snippet = StarterSnippets.find(s => s.id === snippetId);
            if (snippet) {
                if (State.tabs.size === 0) {
                    TabManager.createTab();
                }
                setEditorCode(snippet.code);
                document.getElementById('emptyStateView').style.display = 'none';
                if (window.editor) window.editor.focus();
            }
        });
    });

    initLucide();
}

function initMonaco() {
    return new Promise((resolve) => {
        if (typeof require === 'undefined') {
            resolve();
            return;
        }
        require.config({ paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.39.0/min/vs' } });
        require(['vs/editor/editor.main'], function () {
            registerCppAutocomplete();

            const container = document.getElementById('editorContent');
            if (!container) {
                resolve();
                return;
            }

            const textarea = document.getElementById('codeTextarea');
            const initialCode = textarea ? textarea.value : '';
            if (textarea) textarea.remove();

            const editorDiv = document.createElement('div');
            editorDiv.id = 'monacoEditor';
            editorDiv.className = 'code-textarea';
            editorDiv.style.width = '100%';
            editorDiv.style.height = '100%';
            container.appendChild(editorDiv);

            monaco.editor.defineTheme('sensei-theme', {
                base: 'vs-dark',
                inherit: true,
                rules: [
                    { token: 'comment', foreground: '71717a', fontStyle: 'italic' },
                    { token: 'keyword', foreground: '6366f1', fontStyle: 'bold' },
                    { token: 'string', foreground: 'a78bfa' },
                    { token: 'number', foreground: '10b981' },
                    { token: 'type', foreground: '3b82f6' },
                    { token: 'preprocessor', foreground: 'f59e0b' }
                ],
                colors: {
                    'editor.background': '#121215',
                    'editor.foreground': '#d4d4d8',
                    'editorLineNumber.foreground': '#4b5563',
                    'editorLineNumber.activeForeground': '#6366f1',
                    'editor.lineHighlightBackground': '#1a1a22',
                    'editor.selectionBackground': 'rgba(99, 102, 241, 0.15)',
                    'editorCursor.foreground': '#ffffff'
                }
            });

            window.editor = monaco.editor.create(editorDiv, {
                value: initialCode,
                language: 'cpp',
                theme: 'sensei-theme',
                automaticLayout: true,
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: 13,
                lineHeight: 20,
                tabSize: 4,
                minimap: { enabled: false },
                scrollbar: {
                    vertical: 'visible',
                    horizontal: 'visible',
                    verticalScrollbarSize: 8,
                    horizontalScrollbarSize: 8
                }
            });

            window.editor.onDidChangeModelContent(() => {
                handleEditorInput();
            });

            window.editor.onDidChangeCursorPosition(() => {
                updateStatusBar();
                if (State.explanationMode === 'line') {
                    handleCursorMove();
                }
            });

            resolve();
        });
    });
}

function registerCppAutocomplete() {
    if (typeof monaco === 'undefined') return;

    monaco.languages.registerCompletionItemProvider('cpp', {
        provideCompletionItems: function (model, position) {
            const suggestions = [];

            const keywords = [
                'int', 'float', 'double', 'char', 'string', 'bool', 'void',
                'if', 'else', 'switch', 'case', 'default', 'for', 'while', 'do',
                'return', 'class', 'struct', 'public', 'private', 'protected',
                'using', 'namespace', 'std', 'new', 'delete', 'const', 'static',
                'template', 'typename', 'virtual', 'override', 'include'
            ];

            keywords.forEach(kw => {
                suggestions.push({
                    label: kw,
                    kind: monaco.languages.CompletionItemKind.Keyword,
                    insertText: kw,
                    range: undefined
                });
            });

            const stdItems = [
                { label: 'cout', insertText: 'cout << ${1:value} << endl;', detail: 'std::cout output stream', isSnippet: true },
                { label: 'cin', insertText: 'cin >> ${1:variable};', detail: 'std::cin input stream', isSnippet: true },
                { label: 'endl', insertText: 'endl', detail: 'std::endl newline', isSnippet: false },
                { label: 'vector', insertText: 'vector<${1:type}> ${2:name};', detail: 'std::vector dynamic array', isSnippet: true },
                { label: 'map', insertText: 'map<${1:key_type}, ${2:value_type}> ${3:name};', detail: 'std::map associative array', isSnippet: true },
                { label: 'set', insertText: 'set<${1:type}> ${2:name};', detail: 'std::set unique ordered elements', isSnippet: true },
                { label: 'string', insertText: 'string', detail: 'std::string class', isSnippet: false },
                { label: 'iostream', insertText: 'iostream', detail: 'Input/Output stream header', isSnippet: false },
                { label: 'vector_header', insertText: 'vector', detail: 'Vector header', isSnippet: false },
                { label: 'algorithm', insertText: 'algorithm', detail: 'Algorithm header', isSnippet: false }
            ];

            stdItems.forEach(item => {
                suggestions.push({
                    label: item.label,
                    kind: item.isSnippet ? monaco.languages.CompletionItemKind.Snippet : monaco.languages.CompletionItemKind.Value,
                    insertText: item.insertText,
                    insertTextRules: item.isSnippet ? monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet : undefined,
                    detail: item.detail,
                    range: undefined
                });
            });

            const lineContent = model.getLineContent(position.lineNumber);
            const includeMatch = lineContent.match(/#include\s*<\s*([\w]*)$/);
            if (includeMatch) {
                const headers = ['iostream', 'vector', 'string', 'algorithm', 'map', 'set', 'cmath', 'iomanip', 'fstream'];
                return {
                    suggestions: headers.map(h => ({
                        label: h,
                        kind: monaco.languages.CompletionItemKind.Module,
                        insertText: h + '>',
                        detail: 'Standard C++ Header',
                        range: undefined
                    }))
                };
            }

            const stdMatch = lineContent.match(/std::([\w]*)$/);
            if (stdMatch) {
                const stdMembers = [
                    { label: 'cout', insertText: 'cout', detail: 'Standard output stream' },
                    { label: 'cin', insertText: 'cin', detail: 'Standard input stream' },
                    { label: 'endl', insertText: 'endl', detail: 'Standard end line' },
                    { label: 'vector', insertText: 'vector', detail: 'Dynamic array' },
                    { label: 'string', insertText: 'string', detail: 'String object' },
                    { label: 'map', insertText: 'map', detail: 'Map container' },
                    { label: 'set', insertText: 'set', detail: 'Set container' }
                ];
                return {
                    suggestions: stdMembers.map(m => ({
                        label: m.label,
                        kind: monaco.languages.CompletionItemKind.Method,
                        insertText: m.insertText,
                        detail: m.detail,
                        range: undefined
                    }))
                };
            }

            return { suggestions: suggestions };
        }
    });
}