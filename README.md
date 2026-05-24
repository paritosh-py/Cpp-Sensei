# 🥋 Cpp-Sensei (Cpp 先生)

![Cpp Sensei Banner](assets/banner.png)

> **"Master C++ one line at a time."**

**Cpp-Sensei** is a modern, interactive desktop IDE customized for learning C++ programming. Built with Electron compatibility in mind, Sensei integrates the professional Microsoft Monaco Editor with customized C++ autocomplete engines, instant line-by-line static explanations, and a Gemini AI coding assistant. It is designed to help beginners bridge the gap between "Hello World" and actual software engineering.

---

## 🌟 Features

- **💻 Monaco Editor Integration**: Features a customized, premium electric indigo theme (`sensei-theme`) with professional-grade syntax highlighting, line numbers, automatic brace closing, and scroll behaviors.
- **💡 Context-Aware Autocomplete**: Custom autocomplete suggestions for C++ keywords, STL classes (`cout`, `cin`, `vector`, `endl`), `#include` standard headers, and `std::` namespaces.
- **🎯 Compact Onboarding Empty-State**: A distraction-free welcome overlay displaying a responsive template grid of 10 beginner C++ code snippets (loops, arrays, star patterns, calculators) designed to fit on a single screen without vertical scrolling.
- **📟 Smooth Terminal Management**: The bottom terminal remains collapsed/hidden by default to maximize editor focus. It slides open smoothly on code execution and includes lag-free drag-resize animation logic.
- **🔍 Instant Explanations**: Click any line of code to see what it *actually* does under the hood using regex-based static analysis.
- **🤖 Gemini AI Integration**: A built-in coding chatbot that helps debug compiler errors, optimize loops, and answer C++ technical questions.
- **📂 Workspace File Explorer**: Left sidebar featuring an interactive folder picker, collapsible tree nodes, and file management controls.

## 🛠️ Tech Stack

| Component | Tech | Description |
| :--- | :--- | :--- |
| **Backend** | ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi) | High-performance async Python server |
| **Frontend** | ![Monaco](https://img.shields.io/badge/Monaco%20Editor-007acc?style=flat&logo=visualstudiocode) | Microsoft Monaco Editor (loaded via CDN) |
| **Styling** | ![CSS](https://img.shields.io/badge/Vanilla%20CSS-1572B6?style=flat&logo=css3) | Tailored HSL color palette and smooth layout transitions |
| **AI Engine** | ![Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=flat&logo=googlebard&logoColor=white) | Generative AI for code assistance |
| **Compiler** | ![GCC](https://img.shields.io/badge/GCC-000000?style=flat&logo=gnu&logoColor=white) | Local `g++` compilation under the hood |

---

## ⚠️ Requirements & Warnings

> [!IMPORTANT]
> **Prerequisites**: You must have `g++` (MinGW for Windows or GCC for Linux) installed and added to your System PATH.

> [!WARNING]
> **Security Notice**: This IDE executes code directly on your host machine using Python's `subprocess`.
> *   Do **NOT** run this on a public server without sandboxing (Docker/nsjail).
> *   Malicious code (e.g., `system("rm -rf /")`) *will* be executed if you type it!

> [!CAUTION]
> **AI Usage**: The AI assistant uses your Gemini API Key. Be mindful of usage limits and do not commit your `ai_logic.py` with a hardcoded API key to a public repository!

---

## 🚀 Getting Started

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/paritosh-py/Cpp-Sensei.git
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

4.  **Open the IDE**
    Open `index.html` directly in a browser (or via local file system) and connect to the local server.

---

## 📂 Project Structure

```bash
Cpp-Sensei/
├── 📄 index.html       # Main IDE UI Layout
├── 📄 server.py        # Main FastAPI application & WebSocket run handler
├── 📄 logic.py         # Static analysis engine (Regex-based explanations)
├── 📄 ai_logic.py      # Google Gemini integration layer
├── 📂 public/          # Frontend assets
│   ├── script.js       # Client-side logic & Monaco autocomplete providers
│   └── styles.css      # Custom stylesheet (indigo dark theme & layout)
└── 📂 assets/          # Project images and resources
```

---

_Built with ❤️ for C++ Learners everywhere._
