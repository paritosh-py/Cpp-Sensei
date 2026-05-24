# 🥋 Cpp-Sensei: Project Review Preparation Guide

This guide is designed to help your team (Paritosh, Shlok, Alok, and Atulya) prepare for the upcoming project review. It breaks down the evaluation rubrics and maps them to your specific contributions, ensuring every point is clearly addressed during the presentation.

---

## 1. Team Introduction & Roles
Start your presentation by clearly defining the division of labor. This shows excellent **Presentation & Teamwork**.

*   **Shlok & Alok (Frontend & UI/UX):** Handled the user interface, Electron web app wrapper, and client-side logic. They ensured the IDE is responsive, intuitive, and visually engaging for beginners.
*   **Paritosh (Backend & Core Logic):** Architected the main engine. Built the FastAPI server, the real-time code compilation/execution pipeline (using `g++` and WebSockets)
*   **Atulya (AI Logic & Model Integration):** Managed the Gemini API integration, crafted the system prompts to ensure the AI acts as a strict C++ tutor, handled the model tuning (`ai_logic.py`), and the high-speed Regex-based static analysis engine.

---

## 2. Addressing the Evaluation Criteria

### A. Use of Modern Tools & Techniques
*How to present this: Showcase the specific tech stack and why it was chosen.*

*   **Frontend (Shlok/Alok):** Discuss the use of **Electron** to convert a web-based interface (HTML5/Vanilla JS) into a native desktop application, providing a fast and lightweight user experience. Mention real-time WebSocket connections for live I/O streaming.
*   **Backend (Paritosh):** Highlight the use of **FastAPI** for asynchronous, high-performance HTTP request handling. Explain the use of Python's **`subprocess`** for invoking `g++` and managing stdout/stdin streams in real-time.
*   **AI & Static Analysis (Atulya):** Emphasize the integration of **Google Gemini's Generative AI** alongside your **Offline Regex Engine** (`logic.py`). Discuss the technique of using strict "system prompts" to force the model to behave exclusively as a C++ tutor, and explain how the custom Regex engine provides ultra-low latency, zero-cost static analysis for common C++ code blocks.

### B. Feasibility & Sustainability Considerations
*How to present this: Explain why this project can survive and scale in the real world.*

*   **Feasibility:** The project uses lightweight tools. The static analysis (`logic.py`) operates entirely offline using Regex, which means it doesn't waste API calls or incur costs for basic code explanations. 
*   **Sustainability:** 
    *   **Cost-Effective:** By offloading compilation to the user's local machine (via the Electron app) rather than doing it on a cloud server, server costs are effectively zero.
    *   **Scalable AI:** Generative API calls are only made when the user specifically opens the chat, reducing API usage overhead.

### C. Engineering Ethics & Professional Standards
*How to present this: Show that you thought about security, safety, and responsible AI.*

*   **Security & Sandboxing (Paritosh):** Discuss the risks of Remote Code Execution (RCE). Since it's an Electron app, the code runs locally on the user's machine, which is safe. However, acknowledge that if deployed on a public web server, it would require strict sandboxing (e.g., Docker containers or nsjail) to prevent malicious scripts from destroying the server.
*   **Responsible AI (Atulya):** Discuss how the AI is purposely restricted. It is ethically designed for *learning*, not cheating. The prompt engineering prevents it from answering non-educational prompts, ensuring students actually learn instead of just copy-pasting homework.
*   **Graceful Error Handling:** C++ compiler errors are notoriously difficult to read. The system professionally intercepts these errors and converts them into beginner-friendly tips.

### D. Presentation & Teamwork
*How to present this: Demonstrate seamless collaboration.*

*   **API Contracts:** Discuss how Paritosh (Backend) and Shlok/Alok (Frontend) agreed on a strict WebSocket structure and JSON bodies. This allowed the frontend and backend to be developed in parallel without breaking each other.
*   **Modular Design:** Point out the project structure (`main.py`, `server.py`, `logic.py`, `ai_logic.py`). Everyone had their specific files, avoiding code merge conflicts and demonstrating professional software engineering practices.

---

## 3. Project Activity: Documentation & Publication

### Research Article Preparation
You already have the base outline generated in `research_paper_details.txt`. During the review, mention that your research paper focuses on:
1.  **The Pedagogical Impact:** How real-time AI feedback reduces the frustration rate of novice C++ programmers compared to traditional IDEs.
2.  **Architectural Efficiency:** Fusing offline Regex analysis with online LLM API calls to balance speed, cost, and intelligence.
3.  **Local Execution Model:** The benefits and security implications of using an Electron desktop wrapper for safe offline compilation.

### Ethical & Professional Documentation
*   Showcase your `README.md`. Point out the professional use of Markdown, Badges, Installation Steps, and Warning alerts (especially the security notice regarding `subprocess`).
*   Highlight that your code contains clear, professional comments (e.g., the structured rules in `logic.py`), making it maintainable for future developers.

---

## 💡 Q&A Cheat Sheet (Anticipated Questions)

**Q: Why use Python backend for a C++ platform?**
**A (Paritosh):** Python offers rapid development for APIs (FastAPI) and possesses powerful standard libraries (`subprocess`) to interact with shell commands. It also has natively supported, robust SDKs for LLM integration like Google Gemini.

**Q: How do you prevent users from breaking the app with infinite loops?**
**A (Paritosh):** *Mention that while the current scope is a local IDE, professional handling involves setting execution timeouts on the `subprocess` (as seen in `timeout=5`).*

**Q: How did you ensure the AI doesn't give them the whole answer?**
**A (Atulya):** Through prompt engineering. The system prompt commands the AI to act as a "tutor" that guides the user to the answer using hints and conceptually focused responses, rather than a code generator.

**Q: How do you handle complex C++ inputs like `cin`?**
**A (Shlok/Alok & Paritosh):** Through WebSockets. The frontend console captures keystrokes and streams them directly into the standard input (`stdin`) of the running background C++ process in real-time.
