import json
import time
from pathlib import Path

from app.smart_search import smart_search
from app.llm import generate_answer


# Project folder
base_path = Path(__file__).resolve().parent.parent


# Load records
with open(base_path / "data" / "records.json", "r", encoding="utf-8") as file:
    records = json.load(file)


# 10 test questions
questions = [
    "What is a ration card?",
    "What is PHH?",
    "What is AAY?",
    "How much ration does a PHH beneficiary receive?",
    "How much ration does an AAY household receive?",
    "What is ONORC?",
    "Can I collect ration outside my home state?",
    "What should I do if I do not receive ration?",
    "What is the difference between PHH and AAY?",
    "Which authority manages ration distribution?"
]


# Prompt Version 1
prompt_v1 = """
Answer the user's question using the available information.

Give a simple and understandable answer.
Do not invent information.
"""


# Prompt Version 2
with open(base_path / "prompts" / "system.txt", "r", encoding="utf-8") as file:
    system_prompt = file.read()

prompt_v2 = """
Answer the user's question using the provided records.

Follow these instructions:
1. Explain ration-related information in simple language.
2. Use the available records as your main source.
3. Do not invent government rules or information.
4. If information is unavailable, clearly mention it.
5. Keep the answer relevant to the user's question.

Return only valid JSON:

{
    "answer": "Your answer",
    "confidence": "high, medium, or low",
    "follow_up": "A relevant follow-up question"
}
"""


# Store comparison results
results = []


# Test both prompts
for question in questions:

    print("\nTesting:", question)

    # Find relevant records
    relevant_records = smart_search(records, question)

    context = ""

    for record in relevant_records[:5]:
        context += record["rule"] + "\n"

    # Prepare user prompt
    user_prompt = (
        "Available Records:\n" + context +
        "\nQuestion: " + question
    )

    try:

        # Generate Version 1 response
        answer_v1 = generate_answer(prompt_v1, user_prompt)

        time.sleep(15)

        # Generate Version 2 response
        answer_v2 = generate_answer(system_prompt + prompt_v2, user_prompt)

        time.sleep(15)

        # Store results
        results.append({
            "question": question,
            "version_1": answer_v1,
            "version_2": answer_v2
        })

    except Exception as error:

        print("Error:", error)
        print("Stopping comparison.")
        break


# Save results
output_file = base_path / "eval" / "comparison_results.json"

with open(output_file, "w", encoding="utf-8") as file:
    json.dump(results, file, indent=4, ensure_ascii=False)

print("\nComparison completed!")
print("Questions completed:", len(results))
print("Results saved to:", output_file)