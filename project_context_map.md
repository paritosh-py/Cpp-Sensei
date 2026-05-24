# 🥋Sensei: Comprehensive Project Context Map

This document serves as a precise, single-source reference detailing the architecture, components, features, and code logic of **Sensei**. It is structured to provide other Agent assistants with an immediate and thorough understanding of the repository.

---

## 📌 Project Overview

**Sensei** is a modern, interactive web-based (or Electron desktop) Integrated Development Environment (IDE) custom-designed for novice C++ programmers. 
- **Core Value Proposition**: Rather than just compilation and running, Sensei explains code in plain English in real-time as the user types/clicks.
- **Hybrid Explanation Engine**: Combines a fast, offline, zero-cost **Regex-based Static Analysis Engine** for quick syntax breakdowns, with an online **Google Gemini AI Assistant** for high-level tutor guidance, debugging help, and starter code templates.
- **Interactive Execution**: Compiles C++ code locally via a compiler pipeline (`g++`) and streams output dynamically through WebSockets, enabling real-time terminal interactions (like `cin` prompts).

---

## 🛠️ Architecture & Tech Stack

```mermaid
flowchart TD
    subgraph Frontend [Presentation Layer (Electron / Web Browser)]
        UI[index.html & styles.css]
        ClientJS[public/script.js]
    end

    subgraph Backend [Execution & Analysis Layer (FastAPI)]
        Server[server.py]
        RegexEngine[logic.py - SenseiLogic]
        AIEngine[ai_logic.py - GeminiAssistant]
    end

    subgraph Compiler [Local Execution Layer]
        SubProcess[subprocess.Popen / subprocess.run]
        GCC[g++ Compiler]
        TempFiles[(temp_uuid.cpp & temp_uuid.exe)]
    end

    subgraph AI [External API Layer]
        Gemini[Google Gemini API]
    end

    UI -->|Events & Keystrokes| ClientJS
    ClientJS -->|POST /explain| Server
    ClientJS -->|POST /chat| Server
    ClientJS -->|WS /ws/run| Server
    
    Server -->|Parse line syntax| RegexEngine
    Server -->|Enforced tutor prompts| AIEngine
    AIEngine -->|Generative queries| Gemini
    
    Server -->|Invoke shell commands| SubProcess
    SubProcess -->|Compile source| GCC
    SubProcess -->|Create/Execute| TempFiles
    TempFiles -->|Stream stdout/stdin| Server
    Server -->|Real-time I/O| ClientJS
```

### Stack Components:
1. **Frontend**: Vanilla JavaScript (ES6+), HTML5, and Custom CSS3 (utilizing HSL color variables for dark/light mode toggle, Nunito/Fira Code typography, and Lucide icons). It is designed to be lightweight, fast, and wrapped in **Electron** to run as a native desktop application.
2. **Backend**: **FastAPI** (Python 3) server with asynchronous routing, WebSocket handlers, and CORS configuration.
3. **AI Layer**: **Google Gemini SDK** (`google-generativeai`) using generative models (auto-selecting the best available model like `gemini-1.5-flash` or `gemini-1.5-pro`).
4. **Compilation**: Local `g++` invocation using Python's standard `subprocess` library.

---

## 📂 File Manifest & Descriptions

The repository contains the following file structure:

- [server.py](file:///c:/Users/parit/Desktop/Minor1/server.py): Main FastAPI backend & WebSocket runner. Exposes HTTP REST and WebSocket communication protocols.
- [main.py](file:///c:/Users/parit/Desktop/Minor1/main.py): Legacy/Alternative desktop UI built in Tkinter (utilizes [SenseiIDE](file:///c:/Users/parit/Desktop/Minor1/main.py#L8)).
- [logic.py](file:///c:/Users/parit/Desktop/Minor1/logic.py): Static Analysis Engine. Defines [SenseiLogic](file:///c:/Users/parit/Desktop/Minor1/logic.py#L4) with regex patterns mapping syntax to educational comments.
- [ai_logic.py](file:///c:/Users/parit/Desktop/Minor1/ai_logic.py): AI Assistant Wrapper. Defines [GeminiAssistant](file:///c:/Users/parit/Desktop/Minor1/ai_logic.py#L4) to query Gemini and handle prompt formatting.
- [check_models.py](file:///c:/Users/parit/Desktop/Minor1/check_models.py): Helper utility to list available Gemini models.
- [models.txt](file:///c:/Users/parit/Desktop/Minor1/models.txt): Saved text file listing all available Gemini and Gemma models.
- [index.html](file:///c:/Users/parit/Desktop/Minor1/index.html): Main IDE HTML user interface layout page.
- [public/script.js](file:///c:/Users/parit/Desktop/Minor1/public/script.js): Client-side JavaScript handling state, events, theme toggling, and WebSockets.
- [public/styles.css](file:///c:/Users/parit/Desktop/Minor1/public/styles.css): Complete styling rules for light/dark theme variables, panels, code layout, and responsive breakpoints.
- [README.md](file:///c:/Users/parit/Desktop/Minor1/README.md): Readme overview, features checklist, tech badges, warnings, and setup scripts.
- [project_review_prep.md](file:///c:/Users/parit/Desktop/Minor1/project_review_prep.md): Guide for project reviews mapping team roles to specific rubrics.
- [research_paper_details.txt](file:///c:/Users/parit/Desktop/Minor1/research_paper_details.txt): Draft article outline and architectural features overview.

---

## ⚙️ Core Components & Code Details

### 1. The Offline Static Analysis Engine ([logic.py](file:///c:/Users/parit/Desktop/Minor1/logic.py))
Encapsulated in the [SenseiLogic](file:///c:/Users/parit/Desktop/Minor1/logic.py#L4) class, this engine matches C++ syntax against an ordered array of Regular Expression rules (`self.rules`). 
- **Efficiency**: Operates locally with zero network overhead and zero cost.
- **Rule Hierarchy**: Specific rules (e.g., `#include <bits/stdc++.h>`) are placed above generic ones (e.g., standard `#include <...>`) to prevent shadowed matches.
- **Categories of Code Explanations**:
  - **Preprocessor & Headers**: Regexes for `#include <...>` and namespace definitions (`using namespace std;`).
  - **Control Flow**: Detects `if`, `else if`, `for` loop parameters, `while` loop conditions, `do-while` loops, and `switch` blocks.
  - **Functions**: Captures syntax returning `void`, pointers, basic types, or STL templates.
  - **Input/Output**: Regexes for `cin >>` and `cout <<`.
  - **OOP (Object-Oriented Programming)**: Captures class inheritance (`class A : public B`), constructors (default, parameterized, copy), destructors (`~A`), virtual functions, access modifiers (`public:`, `private:`), and pure virtual bindings (`= 0`).
  - **STL Containers**: Detects vectors (`vector<T>`), maps (`map<K, V>`), and sets (`set<T>`).
  - **Memory Management**: Captures pointer variables (`int*`), references (`int&`), heap allocation (`new`), and manual deallocations (`delete`).
  - **Methods & Members**: Recognizes dot operators (`a.func()`) and arrow dereferences (`ptr->func()`).
  - **Arrays**: Recognizes C-style strings (`char str[]`), fixed-size declarations (`int arr[5]`), and array initialization patterns (`int arr[] = {...}`).

Main methods:
- [explain_line](file:///c:/Users/parit/Desktop/Minor1/logic.py#L286): Iterates rules to generate line-specific markdown feedback.
- [explain_more](file:///c:/Users/parit/Desktop/Minor1/logic.py#L314): Returns full description details and an external cppreference link for the matched construct.

### 2. The API & Execution Backend ([server.py](file:///c:/Users/parit/Desktop/Minor1/server.py))
Runs on FastAPI / Uvicorn and exposes four main endpoints:
- **`POST /explain`**: Receives a code line in JSON. Processes it using [explain_line](file:///c:/Users/parit/Desktop/Minor1/logic.py#L286) and returns the markdown explanation.
- **`POST /chat`**: Receives a chat input and queries the AI Engine via [chat](file:///c:/Users/parit/Desktop/Minor1/ai_logic.py#L124).
- **`GET /starter-code/{type_key}`**: Fetches boilerplates for topics (`io`, `array`, `string`) using [get_starter_code](file:///c:/Users/parit/Desktop/Minor1/ai_logic.py#L121).
- **`WS /ws/run`** (WebSocket endpoint [L48](file:///c:/Users/parit/Desktop/Minor1/server.py#L48)): Handles code compile-and-run requests using an asynchronous WebSocket:
  1. The client opens the socket and transmits the C++ source code as a JSON object.
  2. The server generates a unique workspace ID via `uuid.uuid4()`.
  3. Writes the code to a temporary file named `temp_<uuid>.cpp` using UTF-8 encoding.
  4. Invokes the local compiler: `g++ temp_<uuid>.cpp -o temp_<uuid>.exe`.
  5. If compilation fails, the raw `stderr` compilation error output is sent back to the client, the socket is closed, and temporary files are cleaned up.
  6. If compilation succeeds, the server spawns the executable asynchronously via `subprocess.Popen`.
  7. Spawns dual background daemon threads (`stream_reader`) to continuously read the process's stdout and stderr. **Crucial detail**: It reads the pipe character-by-character (`pipe.read(1)`) instead of line-by-line. This ensures prompts like `Enter number: ` display immediately without waiting for a newline (`\n`).
  8. An input loop listens for text from the frontend WebSocket. When the user sends input, it is written to the process's `stdin` and flushed instantly.
  9. Clean termination signals program finish (`[Program Finished]`), terminates the socket connection, and deletes the temporary files.

### 3. The AI Logic Engine ([ai_logic.py](file:///c:/Users/parit/Desktop/Minor1/ai_logic.py))
Managed by the [GeminiAssistant](file:///c:/Users/parit/Desktop/Minor1/ai_logic.py#L4) class.
- **API Setup**: Currently initialized using a development API Key. For production, this should be refactored to query environment variables (`os.environ["GEMINI_API_KEY"]`).
- **Model Selection Protocol**: Dynamically lists available Google Generative AI models. It looks for models supporting `'generateContent'` and matches them against a preferred order:
  1. `models/gemini-1.5-flash`
  2. `models/gemini-1.5-pro`
  3. `models/gemini-2.0-flash-exp`
  4. `models/gemini-1.0-pro`
  5. `models/gemini-pro`
- **System Tutor Containment**: Enforces a strict system prompt to ensure Gemini behaves as a tutor:
  - Answers *only* C++ or computer science programming questions.
  - Refuses non-coding topics politely, redirecting the user.
  - Keeps responses concise and suited for beginners.
  - Employs friendly formatting (emojis like 🚀, 💻, 💡).
  - Guides students using hints rather than writing their code solutions directly.

### 4. Client-Side Orchestrator ([public/script.js](file:///c:/Users/parit/Desktop/Minor1/public/script.js))
Controls state management, theme settings, UI render updates, and connection setups:
- **Editor Synchronization**: Monitors key releases and clicks in the textarea to identify the user's cursor position. It translates coordinates to get the current active line number and updates the line number rail dynamically.
- **Line Explanation Debounce**: To avoid flooding the FastAPI server with HTTP requests during continuous typing, it triggers a 300ms debounce. If the user stops typing for 300ms on a line, it fires the POST request to `/explain`.
- **Live Console WebSockets**: Handles the connection status, prints compiler prompts, streams inputs, and handles standard inputs (`stdin`) when the user hits 'Enter' on the input field of the console panel.
- **Beginner / Advanced Toggle**: Changes the detail level of code summaries shown in the explanations container.

---

## 🔄 Data Flows & Processes

### 1. Code Explanation Request
```
[User moves cursor/types code] 
    --> [public/script.js (Cursor Move Event)] 
    --> [300ms Debounce Check] 
    --> [Fetch POST to /explain]
    --> [server.py (explain_endpoint)] 
    --> [logic.py (SenseiLogic.explain_line)] 
    --> [Regex Match Lookup] 
    --> [Return Markdown Explanation] 
    --> [Render in right-side pane]
```

### 2. Code Run & Interactive I/O Pipeline
```
[User clicks Run] 
    --> [WS Connects to /ws/run] 
    --> [Client transmits source code JSON]
    --> [Backend writes temp_<uuid>.cpp]
    --> [Backend compiles via g++] 
    --> [On Fail: Stream stderr to WS -> close]
    --> [On Success: Popen temp_<uuid>.exe]
    --> [Spawn stdio reader threads (char-by-char)]
    --> [Pipe output to WebSocket -> Render in UI Console]
    --> [User types input in UI -> Sends to WS]
    --> [Backend writes input to stdin of executable]
    --> [Executable completes -> cleanup files -> WS Close]
```

---

## 🔒 Security & Deployment Considerations

- **Remote Code Execution (RCE)**: Since the backend executes raw compiled binaries locally using `subprocess`, the app runs with the permissions of the host machine. This is safe inside a desktop Electron environment (since the user is executing their own code).
- **Public Sandbox Requirement**: If this backend is ever hosted on a public server, it **MUST** be sandboxed. You must use tools like **Docker containers** or **nsjail** to restrict network access, file system access, and memory/CPU consumption of compiled C++ binaries.
- **Key Configuration**: The Google Gemini API key must be removed from code and managed using environment variables (`os.environ`) in production environments.
