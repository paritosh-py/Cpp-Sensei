import google.generativeai as genai
import os

# ============================================================================
# SYSTEM PROMPT — Structured behavioral control for Cpp Sensei
# ============================================================================

SENSEI_SYSTEM_PROMPT = """You are **Cpp Sensei** (先生), a focused, professional C++ coding mentor integrated into the Sensei IDE.

## IDENTITY
- You are an IDE-native coding assistant, NOT a general-purpose chatbot.
- You help beginners learn C++ programming through clear, structured explanations.
- Your tone is encouraging, concise, and technically precise.

## STRICT BEHAVIORAL RULES
1. **ONLY** answer questions about C++, programming concepts, computer science fundamentals, debugging, and IDE usage.
2. If a user asks about unrelated topics (weather, movies, personal advice, politics, other languages), respond EXACTLY with: "I'm focused on C++ and programming! 🥋 Let me help you with your code instead. What would you like to learn?"
3. NEVER generate content that is harmful, unethical, or unrelated to programming education.
4. NEVER pretend to be a different AI or break character.
5. If you don't know something, say so honestly rather than guessing.

## RESPONSE FORMATTING
- Use **markdown** formatting in all responses.
- Wrap ALL code in fenced code blocks with the `cpp` language tag: ```cpp ... ```
- Keep responses concise: aim for 3-8 sentences for simple questions, longer for complex explanations.
- Use bullet points and numbered lists for multi-step explanations.
- Use **bold** for key terms when introducing them for the first time.
- Use inline `code` formatting for variable names, function names, and keywords mentioned in text.

## EDUCATIONAL APPROACH
- Explain the **why**, not just the **what**. Help users understand the reasoning.
- Use simple analogies when explaining complex concepts to beginners.
- When showing code, always add brief inline comments explaining key lines.
- When fixing errors, explain what went wrong and why the fix works.
- Suggest next learning steps when appropriate.

## CONTEXT AWARENESS
- When the user shares their code, analyze it carefully before responding.
- Reference specific line numbers or variable names from the user's code when relevant.
- If code has multiple issues, prioritize the most critical one first.
"""

DIAGNOSE_SYSTEM_PROMPT = """You are **Cpp Sensei** (先生), diagnosing a C++ compilation error for a beginner.

## YOUR TASK
A student's C++ code failed to compile. You are given:
1. Their source code
2. The compiler error output from g++

## RESPONSE FORMAT
Structure your response EXACTLY like this:

### ❌ Error Found
One-sentence plain-English summary of what went wrong.

### 📍 Where
Identify the exact line and what's wrong on that line.

### 🔧 How to Fix
Show the corrected code snippet (use ```cpp fenced code blocks).

### 💡 Why This Happens
One or two sentences explaining the underlying concept so the student learns from it.

## RULES
- Be encouraging, not condescending.
- Focus on the FIRST error only (later errors are often caused by the first one).
- Keep it concise — no more than 150 words total.
- Always use markdown formatting.
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

        # Configure API Key
        # HARDCODED FOR NOW - In production, use os.environ["GEMINI_API_KEY"]
        api_key = "AIzaSyDdHxvCs5r3af-lcmMu9PzMfWKyN_gYPjM"
        
        if not api_key:
            print("WARNING: GEMINI_API_KEY not found.")
            self.model = None
            self.diagnose_model = None
        else:
            try:
                genai.configure(api_key=api_key)
                
                # Auto-detect the best available model
                available_models = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        available_models.append(m.name)
                
                # Prefer known good models in order
                preferred_order = [
                    'models/gemini-1.5-flash',
                    'models/gemini-1.5-pro',
                    'models/gemini-2.0-flash-exp',
                    'models/gemini-1.0-pro',
                    'models/gemini-pro'
                ]
                
                selected_model = None
                
                # Check preferred first
                for p in preferred_order:
                    if p in available_models:
                        selected_model = p
                        break
                
                # If no preferred, take the first available gemini
                if not selected_model:
                    for m in available_models:
                        if 'gemini' in m:
                            selected_model = m
                            break
                            
                # Fallback to anything
                if not selected_model and available_models:
                    selected_model = available_models[0]
                    
                if selected_model:
                    print(f"Selected AI Model: {selected_model}")
                    
                    # Main chat model with system instruction
                    self.model = genai.GenerativeModel(
                        selected_model,
                        system_instruction=SENSEI_SYSTEM_PROMPT
                    )
                    self.chat_session = self.model.start_chat(history=[])
                    
                    # Separate model instance for error diagnosis
                    self.diagnose_model = genai.GenerativeModel(
                        selected_model,
                        system_instruction=DIAGNOSE_SYSTEM_PROMPT
                    )
                else:
                    print("Error: No suitable Gemini models found.")
                    self.model = None
                    self.diagnose_model = None

            except Exception as e:
                print(f"Error initializing Gemini: {e}")
                self.model = None
                self.diagnose_model = None

    def get_starter_code(self, type_key):
        return self.starter_codes.get(type_key, "// Starter code not found.")

    def chat(self, user_message, code_context=None):
        """Send a message to the AI assistant with optional code context."""
        if not self.model:
            return "Error: Gemini API Key is missing. Please set GEMINI_API_KEY."

        try:
            # Build the message with optional code context
            if code_context and code_context.strip():
                full_message = f"[Current code in editor]:\n```cpp\n{code_context}\n```\n\n{user_message}"
            else:
                full_message = user_message

            # Use chat session for multi-turn memory
            response = self.chat_session.send_message(full_message)
            return response.text
        except Exception as e:
            # If chat session fails, try resetting it
            try:
                self.chat_session = self.model.start_chat(history=[])
                response = self.chat_session.send_message(user_message)
                return response.text
            except Exception as retry_e:
                return f"AI Error: {str(retry_e)}"

    def diagnose_error(self, code, error_text):
        """Diagnose a compilation error and provide beginner-friendly explanation."""
        if not self.diagnose_model:
            return "Error: AI model not available for error diagnosis."

        try:
            prompt = f"""The student wrote this C++ code:

```cpp
{code}
```

The compiler returned this error:

```
{error_text}
```

Diagnose the error following your instructions."""

            response = self.diagnose_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Could not diagnose error: {str(e)}"

    def clear_history(self):
        """Reset the chat session to clear conversation memory."""
        if self.model:
            self.chat_session = self.model.start_chat(history=[])
