from answer import answer_question
import sys

# Simple color codes for terminal output to make it readable
GREEN = "\033[92m"
BLUE = "\033[94m"
RESET = "\033[0m"

def main():
    print(f"{GREEN}--- RAG Backend Test (Gemini 2.0) ---{RESET}")
    print("Type 'exit' or 'quit' to stop.\n")

    history = []

    while True:
        try:
            # 1. Get User Input
            user_input = input(f"{BLUE}You:{RESET} ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            # 2. Call your backend logic directly
            print("Thinking...", end="\r")
            answer, sources = answer_question(user_input, history)
            
            # 3. Print the Answer
            print(f"\n{GREEN}Gemini:{RESET} {answer}\n")
            
            # 4. (Optional) Show which chunks it used
            print(f"{BLUE}[Used {len(sources)} sources from Knowledge Base]{RESET}")
            # Uncomment the next line if you want to see the exact text chunks it found:
            # for s in sources: print(f" - {s.metadata['source']}")
            
            print("-" * 40)

            # 5. Update history for follow-up questions
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": answer})

        except Exception as e:
            print(f"\n{GREEN}Error:{RESET} {e}")

if __name__ == "__main__":
    main()