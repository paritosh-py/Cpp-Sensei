import google.generativeai as genai
import os

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
        api_key = "AIzaSyCS1NNjG83K7SPVLC-DY5rlpkSjhLQDXzE"
        
        if not api_key:
            print("WARNING: GEMINI_API_KEY not found.")
            self.model = None
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
                    self.model = genai.GenerativeModel(selected_model)
                    self.chat_session = self.model.start_chat(history=[])
                else:
                    print("Error: No suitable Gemini models found.")
                    self.model = None

            except Exception as e:
                print(f"Error initializing Gemini: {e}")
                self.model = None

    def get_starter_code(self, type_key):
        return self.starter_codes.get(type_key, "// Starter code not found.")

    def chat(self, user_message, history=[]):
        if not self.model:
            return "Error: Gemini API Key is missing. Please set GEMINI_API_KEY."

        # System Prompt enforcement
        system_prompt = """You are Cpp Sensei, a helpful and encouraging C++ coding tutor for beginners. 
        Your goal is to help users learn C++ programming.
        
        RULES:
        1. ONLY answer questions related to C++ coding, computer science, or programming logic.
        2. If a user asks about non-coding topics (weather, movies, life advice), politely refuse and steer them back to C++.
        3. Keep answers concise and strictly relevant to the learner's level.
        4. Use emojis occasionally to be friendly (e.g., 🚀, 💻, 💡).
        """

        try:
            # We send history + current message to maintain context
            # Note: simplified for this implementation to just send prompt + message
            full_prompt = f"{system_prompt}\n\nUser: {user_message}\nSensei:"
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"AI Error: {str(e)}"
