from google import genai
import os

class GeminiAssistant:
    def __init__(self):
        self.starter_codes = {
            "io": """#include <iostream>
using namespace std;

int main() {
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
    int numbers[5] = {10, 20, 30, 40, 50};
    cout << "Array elements are:" << endl;
    for(int i = 0; i < 5; i++) {
        cout << "Element at index " << i << ": " << numbers[i] << endl;
    }
    return 0;
}""",
            "string": """#include <iostream>
#include <string>
using namespace std;

int main() {
    string text = "C++ Programming";
    cout << "Original String: " << text << endl;
    cout << "Length: " << text.length() << endl;
    cout << "First character: " << text[0] << endl;
    text += " is fun!";
    cout << "Modified String: " << text << endl;
    return 0;
}"""
        }

        api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyDdHxvCs5r3af-lcmMu9PzMfWKyN_gYPjM")

        if not api_key:
            print("WARNING: GEMINI_API_KEY not found.")
            self.client = None
        else:
            try:
                self.client = genai.Client(api_key=api_key)
                self.model = "gemini-2.0-flash"
                print(f"Selected AI Model: {self.model}")
            except Exception as e:
                print(f"Error initializing Gemini: {e}")
                self.client = None

    def get_starter_code(self, type_key):
        return self.starter_codes.get(type_key, "// Starter code not found.")

    def chat(self, user_message, history=[]):
        if not self.client:
            return "Error: Gemini API Key is missing. Please set GEMINI_API_KEY."

        system_prompt = """You are Cpp Sensei, a helpful and encouraging C++ coding tutor for beginners.
        Your goal is to help users learn C++ programming.
        
        RULES:
        1. ONLY answer questions related to C++ coding, computer science, or programming logic.
        2. If a user asks about non-coding topics, politely refuse and steer them back to C++.
        3. Keep answers concise and strictly relevant to the learner's level.
        4. Use emojis occasionally to be friendly (e.g., 🚀, 💻, 💡).
        """

        try:
            full_prompt = f"{system_prompt}\n\nUser: {user_message}\nSensei:"
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt
            )
            return response.text
        except Exception as e:
            return f"AI Error: {str(e)}"