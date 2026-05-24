import google.generativeai as genai
import os

# Using the key we just saw
api_key = "AIzaSyDdHxvCs5r3af-lcmMu9PzMfWKyN_gYPjM"
genai.configure(api_key=api_key)

try:
    print("Listing models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Name: {m.name}")
except Exception as e:
    print(f"Error: {e}")
