// Global State
let isBeginnerMode = true;
let explanationMode = 'idle'; // 'idle', 'line', 'full'
let isChatboxExpanded = false;

// Initialize the application
document.addEventListener('DOMContentLoaded', function () {
    initializeLucideIcons();
    setupEventListeners();
    updateLineNumbers();
    initializeTheme();
    setupSmoothScroll();
});

// Initialize Lucide icons
function initializeLucideIcons() {
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

// Setup all event listeners
function setupEventListeners() {
    // Theme toggle
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);

    // Code editor actions
    document.getElementById('runCode').addEventListener('click', handleRunCode);
    document.getElementById('lineExplain').addEventListener('click', handleLineExplain);
    document.getElementById('fullExplain').addEventListener('click', handleFullExplain);
    document.getElementById('copyCode').addEventListener('click', handleCopyCode);
    document.getElementById('downloadCode').addEventListener('click', handleDownloadCode);

    // Explanation panel
    document.getElementById('toggleBeginnerMode').addEventListener('click', toggleBeginnerMode);

    // Code textarea
    const codeTextarea = document.getElementById('codeTextarea');
    codeTextarea.addEventListener('input', () => {
        updateLineNumbers();
        handleCursorMove(); // Explain on type
    });
    codeTextarea.addEventListener('scroll', syncLineNumbersScroll);
    codeTextarea.addEventListener('click', handleCursorMove); // Explain on click
    codeTextarea.addEventListener('keyup', handleCursorMove); // Explain on arrow keys

    // AI Chatbox
    document.getElementById('chatboxHeader').addEventListener('click', toggleChatbox);
    document.getElementById('chatboxToggle').addEventListener('click', toggleChatbox);
    document.getElementById('sendButton').addEventListener('click', sendMessage);
    document.getElementById('chatInput').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Quick action buttons
    document.querySelectorAll('.quick-action-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const action = this.getAttribute('data-action');
            handleQuickAction(action);
        });
    });

    // Console Input
    const consoleInput = document.getElementById('consoleInput');
    if (consoleInput) {
        consoleInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                sendConsoleInput();
            }
        });
    }

    // Close Console
    document.getElementById('closeConsole').addEventListener('click', () => {
        document.getElementById('consolePanel').style.display = 'none';
        if (socket) socket.close();
    });
}

// Theme Management
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        document.body.classList.remove('light-mode');
    }
}

function toggleTheme() {
    const isDark = document.body.classList.contains('dark-mode');

    if (isDark) {
        document.body.classList.remove('dark-mode');
        document.body.classList.add('light-mode');
        localStorage.setItem('theme', 'light');
        showToast('Switched to light mode', 'Theme updated successfully!');
    } else {
        document.body.classList.remove('light-mode');
        document.body.classList.add('dark-mode');
        localStorage.setItem('theme', 'dark');
        showToast('Switched to dark mode', 'Theme updated successfully!');
    }
}

// Code Editor Functions
// ... Theme ... (unchanged)

let socket = null;

async function handleRunCode() {
    const code = document.getElementById('codeTextarea').value;
    const consolePanel = document.getElementById('consolePanel');
    const consoleOutput = document.getElementById('consoleOutput');
    const consoleInput = document.getElementById('consoleInput');

    // Reset and Show console
    consolePanel.style.display = 'flex'; // Changed to flex for layout
    consoleOutput.textContent = '';
    consoleInput.value = '';
    consoleInput.focus();

    // Close existing socket
    if (socket) {
        socket.close();
    }

    showToast('Connecting...', 'Establishing connection to server...');

    try {
        socket = new WebSocket('ws://localhost:8000/ws/run');

        socket.onopen = function () {
            socket.send(JSON.stringify({ code: code }));
            showToast('Running', 'Connected! Program starting...');
        };

        socket.onmessage = function (event) {
            consoleOutput.textContent += event.data;
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
        };

        socket.onclose = function () {
            consoleOutput.textContent += '\n\n[Disconnected]';
        };

        socket.onerror = function () {
            consoleOutput.textContent += '\n[Connection Error]';
        };

    } catch (e) {
        consoleOutput.textContent = 'Error connecting: ' + e.message;
    }
}

function sendConsoleInput() {
    const inputField = document.getElementById('consoleInput');
    const text = inputField.value;

    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(text);
        // Echo input to console for better UX
        const consoleOutput = document.getElementById('consoleOutput');
        consoleOutput.textContent += text + '\n';
        inputField.value = '';
    } else {
        showToast('Error', 'Program is not running');
    }
}

// Explanation functions...

// Helper to get current line number
function getCursorLineNumber(textarea) {
    const value = textarea.value;
    const selectionStart = textarea.selectionStart;
    const lines = value.substr(0, selectionStart).split("\n");
    return lines.length; // 1-indexed
}

let activeLineTimeout = null;
let lastExplainedLine = -1;

async function handleLineExplain() {
    // Just toggle the mode
    explanationMode = 'line';
    updateExplanationPanel();

    // Add listeners if not already added (check with flag or just add)
    // For simplicity, we'll ensure they are bound. 
    // Ideally we bind them once in setup, but we only want them active in this mode.
    // Let's add them to setupEventListeners but check the mode inside the handler.

    // Trigger initial explanation for current cursor position
    handleCursorMove();

    showToast('Interactive Mode', 'Click or type on any line to explain it!');
}

async function handleCursorMove() {
    if (explanationMode !== 'line') return;

    const textarea = document.getElementById('codeTextarea');
    const container = document.getElementById('lineExplanations');
    const currentLineNum = getCursorLineNumber(textarea);

    // Clear debounce timer
    if (activeLineTimeout) clearTimeout(activeLineTimeout);

    // Get content of current line
    const lines = textarea.value.split('\n');
    const lineContent = lines[currentLineNum - 1]?.trim();

    // Don't re-explain if we're on the same line and content hasn't changed meaningfully
    // Actually, we WANT to re-explain if they type more (e.g. "int" -> "Variable", "int a" -> "Variable named a")
    // So we just rely on debounce.

    lastExplainedLine = currentLineNum; // Keep track but don't block


    if (!lineContent || lineContent.startsWith('//') || lineContent.length < 2) {
        container.innerHTML = `<div style="padding: 20px; color: #888; text-align: center;">Waiting for code on line ${currentLineNum}...</div>`;
        return;
    }

    // Debounce: Wait 300ms after last move/type
    activeLineTimeout = setTimeout(async () => {
        container.innerHTML = `<div style="padding: 20px; text-align: center;"><span class="loading-spinner">Analyzing Line ${currentLineNum}...</span></div>`;

        try {
            const response = await fetch('http://localhost:8000/explain', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ line: lineContent })
            });
            const data = await response.json();

            // Escape HTML in the explanation so <iostream> doesn't vanish
            const safeExplanation = data.explanation
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;")
                .replace(/\n/g, "<br>");

            container.innerHTML = `
                <div class="line-explanation" style="border-left: 4px solid var(--accent-color); animation: fadeIn 0.3s ease;">
                    <div class="line-explanation-header">
                        <span class="line-badge">Line ${currentLineNum}</span>
                        <code class="line-code">${lineContent.substring(0, 40)}${lineContent.length > 40 ? '...' : ''}</code>
                    </div>
                    <div class="line-explanation-content" style="font-size: 1.1rem; line-height: 1.6;">
                        ${safeExplanation}
                    </div>
                </div>`;

        } catch (error) {
            container.innerHTML = `<div style="color: red; padding: 20px;">Error: ${error.message}</div>`;
        }
    }, 300);
}

function handleFullExplain() {
    explanationMode = 'full';
    updateExplanationPanel();
    showToast('Full explanation activated', 'Generating comprehensive code analysis... (Note: Full explain static for demo)');
    // Keep static full explanation for this specific demo or upgrade to AI if needed later
}

function handleCopyCode() {
    const code = document.getElementById('codeTextarea').value;
    navigator.clipboard.writeText(code).then(() => {
        showToast('Code copied!', 'Code has been copied to your clipboard.');
    });
}

function handleDownloadCode() {
    const code = document.getElementById('codeTextarea').value;
    const element = document.createElement('a');
    const file = new Blob([code], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = 'code.cpp';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

function updateLineNumbers() {
    const textarea = document.getElementById('codeTextarea');
    const lineNumbers = document.getElementById('lineNumbers');
    const lines = textarea.value.split('\n');

    lineNumbers.innerHTML = lines.map((_, index) =>
        `<div style="text-align: right; padding-right: 0.5rem; line-height: 1.5;">${index + 1}</div>`
    ).join('');
}

function syncLineNumbersScroll() {
    const textarea = document.getElementById('codeTextarea');
    const lineNumbers = document.getElementById('lineNumbers');
    lineNumbers.scrollTop = textarea.scrollTop;
}

// Explanation Panel Functions
function toggleBeginnerMode() {
    isBeginnerMode = !isBeginnerMode;
    updateBeginnerModeButton();
    // Re-fetch explanations if needed, or just toggle style
    updateExplanationPanel();

    const mode = isBeginnerMode ? 'beginner' : 'advanced';
    showToast(`Switched to ${mode} mode`, 'Explanations will adjust on next analysis!');
}

function updateBeginnerModeButton() {
    const button = document.getElementById('toggleBeginnerMode');
    const beginnerIcon = button.querySelector('.beginner-icon');
    const advancedIcon = button.querySelector('.advanced-icon');
    const modeText = button.querySelector('.mode-text');

    if (isBeginnerMode) {
        button.className = 'btn btn-accent btn-sm';
        beginnerIcon.style.display = 'block';
        advancedIcon.style.display = 'none';
        modeText.textContent = 'Beginner Mode';
    } else {
        button.className = 'btn btn-secondary btn-sm';
        beginnerIcon.style.display = 'none';
        advancedIcon.style.display = 'block';
        modeText.textContent = 'Advanced Mode';
    }
}

function updateExplanationPanel() {
    const title = document.getElementById('explanationTitle');
    const badge = document.getElementById('explanationBadge');
    const idleState = document.getElementById('explanationIdle');
    const lineExplanations = document.getElementById('lineExplanations');
    const fullExplanations = document.getElementById('fullExplanations');

    // Hide all content areas
    idleState.style.display = 'none';
    lineExplanations.style.display = 'none';
    fullExplanations.style.display = 'none';

    if (explanationMode === 'idle') {
        title.textContent = 'AI Explanations';
        badge.style.display = 'none';
        idleState.style.display = 'flex';
    } else if (explanationMode === 'line') {
        title.textContent = 'Line-by-Line Explanation';
        badge.textContent = 'Interactive';
        badge.style.display = 'inline-block';
        badge.className = 'explanation-badge';
        lineExplanations.style.display = 'block';
        // renderLineExplanations(); // No longer calling static render
    } else if (explanationMode === 'full') {
        title.textContent = 'Full Code Explanation';
        badge.textContent = 'Comprehensive';
        badge.style.display = 'inline-block';
        badge.className = 'explanation-badge';
        fullExplanations.style.display = 'block';
        renderFullExplanations();
    }
}

// renderLineExplanations REMOVED/REPLACED by logic inside handleLineExplain


function renderFullExplanations() {
    const container = document.getElementById('fullExplanations');

    const explanations = [
        {
            id: "overview",
            title: "What This Program Does",
            icon: "sparkles",
            content: isBeginnerMode
                ? "This C++ program calculates and prints the first 10 Fibonacci numbers. The Fibonacci sequence is famous in math and nature - each number is the sum of the two before it: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34... You can see this pattern in sunflower seeds, pinecones, and even galaxies!"
                : "Implementation of the Fibonacci sequence using recursive algorithm with exponential time complexity O(2^n). Demonstrates basic C++ syntax, recursion, and I/O operations."
        },
        {
            id: "structure",
            title: "Program Structure",
            icon: "code",
            content: isBeginnerMode
                ? "Every C++ program has the same basic parts: 1) Include statements (like importing tools), 2) The 'main' function (where the program starts), and 3) Other functions we create. This program also has a 'fibonacci' function that we created to do the math calculations."
                : "Standard C++ program structure with preprocessor directives, namespace usage, function declarations, and the main entry point. Follows typical C++ organizational patterns."
        },
        {
            id: "algorithm",
            title: "How the Fibonacci Function Works",
            icon: "brain",
            content: isBeginnerMode
                ? "The fibonacci function is 'recursive' - it calls itself! Think of it like Russian nesting dolls. To find F(5), it needs F(4) and F(3). To find F(4), it needs F(3) and F(2), and so on, until it reaches F(0)=0 and F(1)=1. Then it builds the answer back up: F(2)=1, F(3)=2, F(4)=3, F(5)=5."
                : "Classic recursive approach with base cases (n ≤ 1) and recursive cases (fibonacci(n-1) + fibonacci(n-2)). Demonstrates divide-and-conquer paradigm with exponential time complexity."
        },
        {
            id: "improvements",
            title: "Making It Better",
            icon: "lightbulb",
            content: isBeginnerMode
                ? "This code is great for learning, but it's slow for big numbers because it recalculates the same values many times. Imagine asking 'What's 2+2?' a thousand times instead of remembering the answer! We could make it faster by storing previous answers or using a different approach."
                : "Consider memoization or dynamic programming to reduce time complexity from O(2^n) to O(n). Iterative approach would be more memory efficient. Could also add input validation and error handling for production code."
        }
    ];

    container.innerHTML = explanations.map(item => `
        <div class="full-explanation">
            <button class="full-explanation-trigger" onclick="toggleFullExplanation('${item.id}')">
                <div class="full-explanation-header">
                    <div class="full-explanation-title">
                        <i data-lucide="${item.icon}"></i>
                        ${item.title}
                    </div>
                    <i data-lucide="chevron-right" id="chevron-${item.id}"></i>
                </div>
            </button>
            <div class="full-explanation-content" id="content-${item.id}" style="display: none;">
                ${item.content}
            </div>
        </div>
    `).join('');

    // Re-initialize Lucide icons for the new content
    setTimeout(initializeLucideIcons, 0);
}

function toggleFullExplanation(id) {
    const content = document.getElementById(`content-${id}`);
    const chevron = document.getElementById(`chevron-${id}`);

    if (content.style.display === 'none') {
        content.style.display = 'block';
        chevron.setAttribute('data-lucide', 'chevron-down');
    } else {
        content.style.display = 'none';
        chevron.setAttribute('data-lucide', 'chevron-right');
    }

    // Re-initialize Lucide icons for the updated chevron
    setTimeout(initializeLucideIcons, 0);
}

// AI Chatbox Functions
function toggleChatbox() {
    const chatbox = document.getElementById('aiChatbox');
    const expandIcon = document.querySelector('.expand-icon');
    const collapseIcon = document.querySelector('.collapse-icon');

    isChatboxExpanded = !isChatboxExpanded;

    if (isChatboxExpanded) {
        chatbox.classList.remove('collapsed');
        expandIcon.style.display = 'none';
        collapseIcon.style.display = 'block';
    } else {
        chatbox.classList.add('collapsed');
        expandIcon.style.display = 'block';
        collapseIcon.style.display = 'none';
    }
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (!message) return;

    // Add user message
    addChatMessage(message, 'user');
    input.value = '';

    // Send to Backend AI
    addChatMessage('<span class="loading-spinner">Thinking...</span>', 'ai', 'loading-msg');

    try {
        const response = await fetch('http://localhost:8000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        // Remove loading message
        const loadingMsg = document.getElementById('loading-msg');
        if (loadingMsg) loadingMsg.remove();

        addChatMessage(data.response, 'ai');

    } catch (e) {
        const loadingMsg = document.getElementById('loading-msg');
        if (loadingMsg) loadingMsg.remove();
        addChatMessage("Error connecting to AI: " + e.message, 'ai');
    }
}

async function loadStarterCode(type) {
    showToast('Loading', 'Fetching starter code...');
    try {
        const response = await fetch(`http://localhost:8000/starter-code/${type}`);
        const data = await response.json();

        const textarea = document.getElementById('codeTextarea');
        textarea.value = data.code;
        updateLineNumbers();

        // Trigger explanation update if in line mode
        if (explanationMode === 'line') {
            handleCursorMove();
        }

        showToast('Loaded', 'Starter code inserted!');

        // Close chat if it's open covering the code? Optional.
        // if(isChatboxExpanded && window.innerWidth < 800) toggleChatbox();

    } catch (e) {
        showToast('Error', 'Failed to load starter code');
    }
}

function addChatMessage(message, sender, id = null) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message`;
    if (id) messageDiv.id = id;

    const avatarIcon = sender === 'ai' ? 'bot' : 'user';

    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i data-lucide="${avatarIcon}"></i>
        </div>
        <div class="message-content">
            <p>${message}</p>
        </div>
    `;

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Re-initialize Lucide icons for the new message
    setTimeout(initializeLucideIcons, 0);
}

function handleQuickAction(action) {
    const actions = {
        'step-by-step': 'Can you explain my C++ code step by step?',
        'optimize': 'How can I optimize my Fibonacci code?',
        'find-errors': 'Are there any errors in my C++ code?'
    };

    const message = actions[action];
    if (message) {
        document.getElementById('chatInput').value = message;
        sendMessage();
    }
}

// Toast Notification System
function showToast(title, description) {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = 'toast';

    toast.innerHTML = `
        <div class="toast-header">${title}</div>
        <div class="toast-description">${description}</div>
    `;

    container.appendChild(toast);

    // Auto remove after 3 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 3000);
}

// Smooth scroll navigation
function setupSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });

                // Update active nav link
                document.querySelectorAll('.nav-link').forEach(link => {
                    link.classList.remove('active');
                });
                this.classList.add('active');
            }
        });
    });

    // Update active nav on scroll
    window.addEventListener('scroll', () => {
        const sections = document.querySelectorAll('section[id]');
        const scrollPosition = window.scrollY + 100;

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');

            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                document.querySelectorAll('.nav-link').forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    });
}

// Initialize collapsed chatbox state
document.addEventListener('DOMContentLoaded', function () {
    const chatbox = document.getElementById('aiChatbox');
    chatbox.classList.add('collapsed');
});