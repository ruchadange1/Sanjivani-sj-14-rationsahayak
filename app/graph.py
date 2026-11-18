from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

from app.rag import ask_question
from app.tools import ration_entitlement


# Define agent state
class AgentState(TypedDict):
    question: str
    card_type: Optional[str]
    family_size: Optional[int]
    annual_income: Optional[float]
    area: Optional[str]
    tool_used: str
    answer: str
    approved: bool


# Route the question
def route_node(state: AgentState):
    question = state["question"].lower()

    keywords = [
        "entitlement",
        "how much ration",
        "how many kg",
        "monthly ration",
        "ration quantity",
        "income eligibility"
    ]

    if any(word in question for word in keywords):
        return {"tool_used": "ration_entitlement"}

    return {"tool_used": "rag_search"}


# Approval node
def approval_node(state: AgentState):

    approval = interrupt({
        "message": "Do you approve the ration entitlement calculation?",
        "action": "ration_entitlement"
    })

    return {"approved": approval}


# Entitlement calculation node
def entitlement_node(state: AgentState):

    result = ration_entitlement(
        state["card_type"],
        state["family_size"],
        state["annual_income"],
        state["area"]
    )

    return {"answer": str(result)}


# RAG node
def rag_node(state: AgentState):

    result = ask_question(state["question"])

    return {"answer": result["answer"]}


# Decide next step
def choose_tool(state: AgentState):

    if state["tool_used"] == "ration_entitlement":
        return "approval"

    return "rag"


# Check approval
def check_approval(state: AgentState):

    if state["approved"]:
        return "entitlement"

    return END


# Build graph
builder = StateGraph(AgentState)

builder.add_node("route", route_node)
builder.add_node("approval", approval_node)
builder.add_node("entitlement", entitlement_node)
builder.add_node("rag", rag_node)

builder.add_edge(START, "route")

builder.add_conditional_edges(
    "route",
    choose_tool,
    {
        "approval": "approval",
        "rag": "rag"
    }
)

builder.add_conditional_edges(
    "approval",
    check_approval,
    {
        "entitlement": "entitlement",
        END: END
    }
)

builder.add_edge("entitlement", END)
builder.add_edge("rag", END)

# Add memory
memory = MemorySaver()

graph = builder.compile(checkpointer=memory)