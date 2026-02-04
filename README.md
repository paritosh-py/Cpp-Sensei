# 🥋 Cpp-Sensei (Cpp 先生)

![Cpp Sensei Banner](assets/banner.png)

> **"Master C++ one line at a time."**

**Cpp-Sensei** is a modern, interactive IDE customized for learning C++ programming. Unlike standard text editors, Sensei watches your keystrokes and provides real-time, context-aware explanations using AI and static analysis. It's designed to help beginners bridge the gap between "Hello World" and actual software engineering.

---

##  Features

- ** Instant Explanations**: Hover or click any line of code to see what it *actually* does.
- ** Gemini AI Integration**: A built-in coding assistant that strictly answers C++ queries (and politely declines to talk about the weather).
- ** Real-Time Execution**: Run your code instantly with live stdout/stderr streaming via WebSockets.
- ** Modern UI**: A beautiful, dark-themed coding environment built with the latest web technologies.
- ** Beginner Mode**: Toggles simplified explanations for those just starting out.

##  Tech Stack

| Component | Tech | Description |
| :--- | :--- | :--- |
| **Backend** | ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi) | High-performance async Python server |
| **Frontend** | ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black) | Vanilla JS + HTML5 for a lightweight, reactive UI |
| **AI Engine** | ![Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=flat&logo=googlebard&logoColor=white) | Generative AI for code assistance |
| **Compiler** | ![GCC](https://img.shields.io/badge/GCC-000000?style=flat&logo=gnu&logoColor=white) | Real `g++` compilation under the hood |

---

## ⚠️ Requirements & Warnings

> [!IMPORTANT]
> **Prerequisites**: You must have `g++` (MinGW for Windows or GCC for Linux) installed and added to your System PATH.

> [!WARNING]
> **Security Notice**: This IDE executes code directly on your host machine using Python's `subprocess`.
> *   Do **NOT** run this on a public server without sandboxing (Docker/nsjail).
> *   Malicious code (e.g., `system("rm -rf /")`) *will* be executed if you type it!

> [!CAUTION]
> **AI Usage**: The AI assistant uses your API Key. Be mindful of usage limits and do not commit your `ai_logic.py` with the hardcoded API key to a public repository!

---

##  Getting Started

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/Cpp-Sensei.git
    cd Cpp-Sensei
    ```

2.  **Install Python Dependencies**
    ```bash
    pip install fastapi uvicorn google-generativeai websockets pydantic
    ```

3.  **Run the Server**
    ```bash
    python server.py
    ```

4.  **Code!**
    Open `http://localhost:8000` (or open `index.html` directly if configured) and start coding!

---

## 📂 Project Structure

```bash
Cpp-Sensei/
├── 📄 server.py        # Main FastAPI application & WebSocket handler
├── 📄 logic.py         # Static analysis engine (Regex-based explanations)
├── 📄 ai_logic.py      # Google Gemini integration layer
├── 📂 public/          # Frontend assets
│   ├── index.html      # Main IDE Interface
│   └── script.js       # Client-side logic
└── 📂 assets/          # Project images and resources
```

---

_Built with ❤️ for C++ Learners everywhere._
