import google.generativeai as genai
import os

import config

# Use the API key from config.py
api_key = config.GEMINI_API_KEY
if not api_key:
    print("[check_models] Error: GEMINI_API_KEY is not configured in your environment or .env file.")
    exit(1)

genai.configure(api_key=api_key)

try:
    print("Listing models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Name: {m.name}")
except Exception as e:
    print(f"Error: {e}")
