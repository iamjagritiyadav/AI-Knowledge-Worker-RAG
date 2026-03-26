import warnings
warnings.filterwarnings("ignore") # This hides those Pydantic warnings

from dotenv import load_dotenv
from litellm import completion
import os

load_dotenv(dotenv_path=".env")

print("--- Gemini Chat Active (Type 'quit' to stop) ---")

while True:
    user_input = input("\nYou: ")
    
    if user_input.lower() in ["quit", "exit", "stop"]:
        break

    try:
        response = completion(
            model="gemini/gemini-3-flash-preview", 
            messages=[{"role": "user", "content": user_input}],
        )
        print(f"\nGemini: {response.choices[0].message.content}")

    except Exception as e:
        print(f"\nError: {e}")