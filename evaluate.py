import warnings
warnings.filterwarnings("ignore")

from answer import answer_question
from litellm import completion
import pandas as pd

# 1. THE GOLDEN DATASET (Add your own "Truths" here)
test_cases = [
    {
        "question": "Who is Avery Lancaster?",
        "ground_truth": "Avery Lancaster is the CEO and Co-Founder of Insurellm, founded in 2015."
    },
    {
        "question": "What is Homellm?",
        "ground_truth": "Homellm is a B2B and B2C home insurance product that uses AI for personalized policies."
    },
    {
        "question": "Does Insurellm cover alien invasions?",
        "ground_truth": "I don't know, but likely not as it is a standard insurance provider. (The model should admit it doesn't know)"
    }
]

# 2. THE JUDGE (Gemini 2.0 Evaluation Prompt)
EVAL_PROMPT = """
You are a strict teacher grading an exam. 
I will give you a QUESTION, the GROUND TRUTH (correct answer), and the STUDENT ANSWER (AI generated).

Grade the STUDENT ANSWER on a scale of 1-5:
1: Completely wrong or hallucinated.
3: Partially correct but missing key details.
5: Perfect. Matches the ground truth meaning (even if words differ).

Output format:
SCORE: [Number]
REASON: [Short explanation]

---
QUESTION: {q}
GROUND TRUTH: {truth}
STUDENT ANSWER: {answer}
"""

def evaluate():
    print(f"👨‍🏫 Starting Evaluation on {len(test_cases)} test cases...\n")
    results = []

    for test in test_cases:
        print(f"Testing: {test['question']}...", end="\r")
        
        # 1. Run RAG
        rag_answer, sources = answer_question(test['question'])
        
        # 2. Run Judge
        judge_input = EVAL_PROMPT.format(
            q=test['question'], 
            truth=test['ground_truth'], 
            answer=rag_answer
        )
        
        evaluation = completion(
            model="gemini/gemini-2.0-flash",
            messages=[{"role": "user", "content": judge_input}]
        ).choices[0].message.content
        
        # 3. Parse Score
        score = "Unknown"
        if "SCORE: 5" in evaluation: score = 5
        elif "SCORE: 4" in evaluation: score = 4
        elif "SCORE: 3" in evaluation: score = 3
        elif "SCORE: 2" in evaluation: score = 2
        elif "SCORE: 1" in evaluation: score = 1
        
        results.append({
            "Question": test['question'],
            "RAG Answer": rag_answer[:100] + "...",
            "Judge Score": score,
            "Judge Reason": evaluation.split("REASON:")[1].strip() if "REASON:" in evaluation else evaluation
        })

    # Print Results Table
    df = pd.DataFrame(results)
    print("\n\n" + "="*60)
    print("📊 ACCURACY REPORT CARD")
    print("="*60)
    print(df[["Question", "Judge Score", "Judge Reason"]].to_string(index=False))

if __name__ == "__main__":
    evaluate()