import google.generativeai as genai
import os
import config

# ============================================================================
# SYSTEM PROMPTS — Structured behavioral control for Cpp Sensei
# ============================================================================

# Base identity shared across chat and diagnosis models to maintain consistency and token efficiency
BASE_IDENTITY = """You are **Cpp Sensei** (先生), a focused, professional C++ coding mentor integrated into the Sensei IDE.
Tone: Encouraging, concise, technically precise.
Scope: ONLY answer questions about C++, programming concepts, computer science fundamentals, debugging, and IDE usage.
For unrelated topics, reply EXACTLY with: "I'm focused on C++ and programming! 🥋 Let me help you with your code instead. What would you like to learn?"
"""

SENSEI_SYSTEM_PROMPT = BASE_IDENTITY + """
## RESPONSE FORMATTING & GUIDELINES
- Use markdown formatting in all responses.
- Wrap ALL C++ code in fenced code blocks with the `cpp` language tag.
- Keep responses concise: aim for 3-8 sentences for simple questions.
- Use bullet points and numbered lists for multi-step explanations.
- Explain the **why**, not just the **what**, using simple analogies for beginners.
- When showing code, always add brief inline comments explaining key lines.
- Reference specific line numbers or variables from the user's code context when relevant.
"""

DIAGNOSE_SYSTEM_PROMPT = BASE_IDENTITY + """
## ERROR DIAGNOSIS TASK
A student's C++ code failed to compile. You are given their source code and the compiler error output.
Analyze the information and structure your response EXACTLY like this:

### ❌ Error Found
One-sentence plain-English summary of what went wrong.

### 📍 Where
Identify the exact line and what's wrong on that line.

### 🔧 How to Fix
Show the corrected C++ code snippet (use ```cpp fenced blocks).

### 💡 Why This Happens
One or two sentences explaining the underlying concept so the student learns from it.

Rules: Focus on the FIRST compilation error only, keep it under 150 words total, and use markdown.
"""


class GeminiAssistant:
    def __init__(self):
        # STARTER CODE TEMPLATES
        self.starter_codes = {
            "io": """#include <iostream>
using namespace std;

int main() {
    // Basic Input/Output Example
    string name;
    int age;

    cout << "Enter your name: ";
    cin >> name;

    cout << "Enter your age: ";
    cin >> age;

    cout << "Hello, " << name << "! You are " << age << " years old." << endl;

    return 0;
}""",
            "array": """#include <iostream>
using namespace std;

int main() {
    // Basic Array Example
    int numbers[5] = {10, 20, 30, 40, 50};

    cout << "Array elements are:" << endl;
    
    // Loop through the array
    for(int i = 0; i < 5; i++) {
        cout << "Element at index " << i << ": " << numbers[i] << endl;
    }

    return 0;
}""",
            "string": """#include <iostream>
#include <string>
using namespace std;

int main() {
    // Basic String Example
    string text = "C++ Programming";
    
    cout << "Original String: " << text << endl;
    cout << "Length: " << text.length() << endl;
    
    // Accessing characters
    cout << "First character: " << text[0] << endl;
    
    // Modifying string
    text += " is fun!";
    cout << "Modified String: " << text << endl;

    return 0;
}"""
        }

        # Track last code context to prevent redundant token consumption
        self.last_code_context = None

        # Configure API Key securely from centralized config
        api_key = config.GEMINI_API_KEY
        
        if not api_key:
            print("[GeminiAssistant] WARNING: GEMINI_API_KEY not configured. AI features are offline.")
            self.model = None
            self.diagnose_model = None
        else:
            try:
                genai.configure(api_key=api_key)
                
                # Use model configured in config.py
                selected_model = config.GEMINI_MODEL
                # Ensure model name starts with models/ if it doesn't already
                if not selected_model.startswith("models/"):
                    selected_model = f"models/{selected_model}"
                
                print(f"[GeminiAssistant] Initializing model: {selected_model}")
                
                # Main chat model with system instruction & token limits
                self.model = genai.GenerativeModel(
                    selected_model,
                    system_instruction=SENSEI_SYSTEM_PROMPT,
                    generation_config={
                        "temperature": config.AI_TEMPERATURE,
                        "max_output_tokens": config.AI_MAX_OUTPUT_TOKENS
                    }
                )
                self.chat_session = self.model.start_chat(history=[])
                
                # Separate model instance for error diagnosis
                self.diagnose_model = genai.GenerativeModel(
                    selected_model,
                    system_instruction=DIAGNOSE_SYSTEM_PROMPT,
                    generation_config={
                        "temperature": config.AI_TEMPERATURE,
                        "max_output_tokens": config.AI_MAX_OUTPUT_TOKENS
                    }
                )
            except Exception as e:
                print(f"[GeminiAssistant] Error initializing Gemini: {e}")
                self.model = None
                self.diagnose_model = None

    def get_starter_code(self, type_key):
        return self.starter_codes.get(type_key, "// Starter code not found.")

    def chat(self, user_message, code_context=None):
        """Send a message to the AI assistant with optional code context."""
        if not self.model:
            return "Sensei: AI services are currently offline. Please set a valid `GEMINI_API_KEY` in your `.env` configuration file to enable the AI assistant."

        try:
            # Clean and check code context to avoid redundant token usage
            cleaned_context = code_context.strip() if code_context else None
            
            # Only append code context if it is present and has changed
            if cleaned_context and cleaned_context != self.last_code_context:
                # Optionally truncate massive context files to protect token usage limits
                if len(cleaned_context) > 20000:
                    cleaned_context = cleaned_context[:20000] + "\n// [Code truncated for length...]"
                full_message = f"[Current code in editor]:\n```cpp\n{cleaned_context}\n```\n\n{user_message}"
                self.last_code_context = cleaned_context
            else:
                full_message = user_message

            # Use chat session for multi-turn memory
            response = self.chat_session.send_message(full_message)
            return response.text
        except Exception as e:
            # Handle specific API errors gracefully
            err_msg = str(e)
            if "API_KEY" in err_msg or "API key" in err_msg or "403" in err_msg or "APIKey" in err_msg:
                return "Sensei: AI services are temporarily unavailable due to an authentication issue. Please verify that a valid GEMINI_API_KEY is configured in your backend environment settings."
            elif "quota" in err_msg.lower() or "limit" in err_msg.lower() or "429" in err_msg:
                return "Sensei: We have reached the rate limit or quota for AI requests. Please wait a moment or try again later."
            
            # If chat session fails due to history mismatch, reset and retry once
            try:
                self.chat_session = self.model.start_chat(history=[])
                self.last_code_context = None
                response = self.chat_session.send_message(user_message)
                return response.text
            except Exception as retry_e:
                retry_err_msg = str(retry_e)
                if "API_KEY" in retry_err_msg or "API key" in retry_err_msg or "403" in retry_err_msg or "APIKey" in retry_err_msg:
                    return "Sensei: AI services are temporarily unavailable due to an authentication issue. Please verify that a valid GEMINI_API_KEY is configured in your backend environment settings."
                elif "quota" in retry_err_msg.lower() or "limit" in retry_err_msg.lower() or "429" in retry_err_msg:
                    return "Sensei: We have reached the rate limit or quota for AI requests. Please wait a moment or try again later."
                return f"Sensei: I ran into an issue connecting to AI services: {retry_err_msg}"

    def diagnose_error(self, code, error_text):
        """Diagnose a compilation error and provide beginner-friendly explanation."""
        if not self.diagnose_model:
            return "Sensei: AI services are currently offline. Please set a valid `GEMINI_API_KEY` in your `.env` configuration file to enable error diagnosis."

        try:
            # Truncate overly long error inputs or code context
            trimmed_code = code[:15000] if code else ""
            trimmed_err = error_text[:5000] if error_text else ""
            
            prompt = f"""The student wrote this C++ code:

```cpp
{trimmed_code}
```

The compiler returned this error:

```
{trimmed_err}
```

Diagnose the error following your instructions."""

            response = self.diagnose_model.generate_content(prompt)
            return response.text
        except Exception as e:
            err_msg = str(e)
            if "API_KEY" in err_msg or "API key" in err_msg or "403" in err_msg or "APIKey" in err_msg:
                return "Sensei: AI services are temporarily unavailable due to an authentication issue. Please verify that a valid GEMINI_API_KEY is configured in your backend environment settings."
            elif "quota" in err_msg.lower() or "limit" in err_msg.lower() or "429" in err_msg:
                return "Sensei: We have reached the rate limit or quota for AI requests. Please wait a moment or try again later."
            return f"Sensei: Could not diagnose error: {err_msg}"

    def clear_history(self):
        """Reset the chat session to clear conversation memory."""
        self.last_code_context = None
        if self.model:
            try:
                self.chat_session = self.model.start_chat(history=[])
            except Exception:
                pass
