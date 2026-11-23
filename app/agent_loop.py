
from app.rag import ask_question
from app.tools import ration_entitlement


def agent_loop(question, card_type=None, family_size=None,
               annual_income=None, area=None):

    keywords = [
        "entitlement",
        "how much ration",
        "how many kg",
        "monthly ration",
        "ration quantity",
        "income eligibility"
    ]

    # Check whether the question is about ration entitlement
    if any(word in question.lower() for word in keywords):

        if card_type is None or family_size is None:
            return {
                "tool_used": "ration_entitlement",
                "answer": "Please provide your card type and family size."
            }

        answer = ration_entitlement(
            card_type, family_size, annual_income, area
        )

        return {
            "tool_used": "ration_entitlement",
            "answer": answer
        }

    # Use RAG for other questions
    result = ask_question(question)

    return {
        "tool_used": "rag_search",
        "answer": result["answer"],
        "citations": result["citations"]
    }
