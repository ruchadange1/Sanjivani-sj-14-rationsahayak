# RationSahayak Prompt Comparison

## 1. Objective

To compare two prompt versions and identify which prompt provides better answers to ration-related questions using the available records.

## 2. Prompt Version 1 – Basic Prompt

A simple prompt that asks the AI to answer the user's question using the available records.

**Prompt:**

```text
Answer the user's question using the available information.

Give a simple and understandable answer.
Do not invent information.
```

## 3. Prompt Version 2 – Detailed Prompt

A detailed prompt that defines the AI's role, provides specific instructions, uses relevant records, and specifies the expected JSON response.

**Prompt:**

```text
You are RationSahayak, an AI assistant that helps people
understand ration cards and food distribution services in India.

Answer the user's question using the provided records.

Follow these instructions:
1. Explain ration-related information in simple language.
2. Use the available records as your main source.
3. Do not invent government rules or information.
4. If information is unavailable, clearly mention it.
5. Keep the answer relevant to the user's question.

Return the response in this JSON format:

{
    "answer": "Your answer",
    "confidence": "high, medium, or low",
    "follow_up": "A relevant follow-up question"
}
```

## 4. Test Questions

Both prompt versions will be tested using the same 10 questions.

1. What is a ration card?
2. What is PHH?
3. What is AAY?
4. How much ration does a PHH beneficiary receive?
5. How much ration does an AAY household receive?
6. What is ONORC?
7. Can I collect ration outside my home state?
8. What should I do if I do not receive ration?
9. What is the difference between PHH and AAY?
10. Which authority manages ration distribution?

## 5. Evaluation Criteria

| Criteria | Prompt Version 1 | Prompt Version 2 |
|---|---|---|
| Answer clarity | Pending | Pending |
| Accuracy | Pending | Pending |
| Relevance | Pending | Pending |
| Correct JSON format | Pending | Pending |
| Factual correctness | Pending | Pending |

## 6. Question-wise Comparison

| Question | Version 1 Observation | Version 2 Observation |
|---|---|---|
| Q1. What is a ration card? | Pending | Pending |
| Q2. What is PHH? | Pending | Pending |
| Q3. What is AAY? | Pending | Pending |
| Q4. PHH ration quantity | Pending | Pending |
| Q5. AAY ration quantity | Pending | Pending |
| Q6. What is ONORC? | Pending | Pending |
| Q7. Collecting ration outside home state | Pending | Pending |
| Q8. Not receiving ration | Pending | Pending |
| Q9. Difference between PHH and AAY | Pending | Pending |
| Q10. Authority managing ration distribution | Pending | Pending |

## 7. Conclusion

Both prompt versions will be evaluated using the same 10 questions and the same available records.

Their responses will be compared based on clarity, accuracy, relevance, factual correctness, and JSON formatting.

The final conclusion will be added after completing the evaluation.