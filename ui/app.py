import csv
import os
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st

# -------------------------------
# PAGE CONFIGURATION
# -------------------------------

st.set_page_config(
    page_title="RationSahayak",
    page_icon="🌾",
    layout="wide"
)

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
FEEDBACK_FILE = DATA_DIR / "feedback.csv"


# -------------------------------
# SESSION STATE
# -------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "ration_slip" not in st.session_state:
    st.session_state.ration_slip = None


# -------------------------------
# CUSTOM CSS
# -------------------------------

st.markdown("""
<style>

/* Main application */
.stApp {
    background-color: #F6F8F6;
    color: #263A32;
}

[data-testid="stAppViewContainer"] {
    background-color: #F6F8F6;
}

[data-testid="stHeader"] {
    background-color: #F6F8F6;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* General text */
.stApp p,
.stApp label,
.stApp li,
.stApp span,
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4 {
    color: #263A32;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #E8F0E8;
    border-right: 1px solid #DCE7DC;
}

[data-testid="stSidebar"] * {
    color: #263A32;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding: 8px;
    border-radius: 8px;
}

/* Header banner */
.main-header {
    background: linear-gradient(120deg, #E2F2E9, #CBE8D9);
    padding: 30px;
    border-radius: 16px;
    margin-bottom: 28px;
    border: 1px solid #D5E9DB;
}

.main-header h1 {
    color: #205C48 !important;
    font-size: 34px;
    margin-bottom: 8px;
}

.main-header p {
    color: #456657 !important;
    font-size: 15px;
}

/* Section headings */
.section-title {
    color: #263A32;
    font-size: 26px;
    font-weight: 700;
    margin-bottom: 5px;
}

.section-description {
    color: #718078;
    font-size: 14px;
    margin-bottom: 22px;
}

/* Dashboard cards */
.dashboard-card {
    background: #FFFFFF;
    padding: 23px;
    border-radius: 14px;
    border: 1px solid #DFE9E0;
    min-height: 150px;
    margin-bottom: 15px;
}

.dashboard-card h3 {
    color: #27866E !important;
    font-size: 19px;
}

.dashboard-card p {
    color: #64756B !important;
    font-size: 14px;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #DFE9E0;
    border-radius: 12px;
    padding: 18px;
}

[data-testid="stMetricLabel"] {
    color: #52675C !important;
}

[data-testid="stMetricValue"] {
    color: #27866E !important;
    font-weight: 700;
}

[data-testid="stMetricDelta"] {
    color: #27866E !important;
}

/* Input fields */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    background-color: #FFFFFF !important;
    color: #263A32 !important;
    border: 1px solid #CBD9CE !important;
    border-radius: 9px !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #87968C !important;
}

/* Select boxes */
[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #263A32 !important;
    border-color: #CBD9CE !important;
}

[data-baseweb="popover"],
[data-baseweb="menu"] {
    background-color: #FFFFFF !important;
}

[data-baseweb="menu"] * {
    color: #263A32 !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background-color: #FFFFFF !important;
    border: 1px solid #DFE9E0;
    border-radius: 12px;
    padding: 14px;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li {
    color: #263A32 !important;
}

/* Buttons */
/* Buttons */
div.stButton > button,
div.stDownloadButton > button,
div.stFormSubmitButton > button {
    background-color: #27866E !important;
    color: #FFFFFF !important;
    border: 1px solid #27866E !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
}

div.stButton > button *,
div.stDownloadButton > button *,
div.stFormSubmitButton > button * {
    color: #FFFFFF !important;
}

div.stButton > button:hover {
    background-color: #1E705A !important;
    color: #FFFFFF !important;
}

/* Forms */
[data-testid="stForm"] {
    background-color: #FFFFFF;
    border: 1px solid #DFE9E0;
    border-radius: 12px;
    padding: 15px;
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 10px;
}

/* Footer */
.footer {
    text-align: center;
    color: #718078;
    padding: 22px;
    font-size: 13px;
}

hr {
    border-color: #DFE9E0;
    margin-top: 25px;
    margin-bottom: 25px;
}

</style>
""", unsafe_allow_html=True)


# -------------------------------
# SIDEBAR
# -------------------------------

with st.sidebar:

    st.markdown("""
    <div style="text-align:center; padding:15px 5px;">
        <h1 style="font-size:40px;">🌾</h1>
        <h2 style="color:#205C48;">RationSahayak</h2>
        <p>Smart Ration Assistance</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### MENU")

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "💬 AI Assistant",
            "🧾 Ration Calculator",
            "🔍 e-PoS Verification",
            "ℹ️ About Project"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("### SYSTEM STATUS")

    try:
        health = requests.get(API_URL + "/health", timeout=3)

        if health.status_code == 200:
            st.success("Backend Connected")
        else:
            st.error("Backend Unavailable")

    except requests.RequestException:
        st.error("Backend Offline")

    st.divider()

    st.caption("AI + RAG Powered Application")
    st.caption("Maharashtra | India")


# -------------------------------
# HEADER
# -------------------------------

st.markdown("""
<div class="main-header">
    <h1>🌾 RationSahayak</h1>
    <p>Your Smart Ration Assistance System</p>
    <p>
        Access ration information, understand your entitlements
        and verify your monthly foodgrain distribution.
    </p>
</div>
""", unsafe_allow_html=True)


# -------------------------------
# DASHBOARD
# -------------------------------

if page == "🏠 Dashboard":

    st.markdown(
        '<div class="section-title">Welcome to RationSahayak</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Your digital assistant for ration-related information and services.'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="dashboard-card">
            <h3>💬 AI Assistant</h3>
            <p>Ask questions about ration cards, eligibility
            and government schemes.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="dashboard-card">
            <h3>🧾 Ration Calculator</h3>
            <p>Calculate your expected monthly foodgrain
            entitlement based on your ration card.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="dashboard-card">
            <h3>🔍 e-PoS Verification</h3>
            <p>Compare your expected ration quantity
            with the quantity received from the shop.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📌 Monthly Entitlement Rules")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("AAY Household", "35 kg", "Per household / month")

    with col2:
        st.metric("PHH Household", "5 kg", "Per person / month")

    st.info(
        "Choose a section from the left navigation menu "
        "to explore RationSahayak services."
    )


# -------------------------------
# AI ASSISTANT
# -------------------------------

elif page == "💬 AI Assistant":

    st.markdown(
        '<div class="section-title">💬 AI Ration Assistant</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Ask questions and receive answers supported by retrieved sources.'
        '</div>',
        unsafe_allow_html=True
    )

    # Display previous messages
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

            if message["role"] == "assistant" and message.get("citations"):

                with st.expander("📚 View Sources"):

                    for citation in message["citations"]:
                        st.write(citation)

    # Question input
    with st.form("chat_form", clear_on_submit=True):

        question = st.text_input(
            "Your question",
            placeholder="Example: What is the PHH monthly ration entitlement?"
        )

        send = st.form_submit_button(
            "Send Message ➤",
            type="primary"
        )

    if send and question.strip():

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.spinner("RationSahayak is thinking..."):

            try:

                response = requests.post(
                    API_URL + "/ask",
                    json={"question": question},
                    timeout=120
                )

                result = response.json()

                if response.status_code == 200:

                    answer = result["answer"]
                    citations = result.get("citations", [])

                else:

                    answer = "Unable to generate an answer: " + str(
                        result.get("detail", "Please try again later.")
                    )

                    citations = []

            except requests.RequestException:

                answer = "Unable to connect to the backend. Please start FastAPI."
                citations = []

            except ValueError:

                answer = "Invalid response received from the backend."
                citations = []

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "citations": citations,
            "question": question
        })

        st.rerun()

    # Feedback
    st.divider()
    st.markdown("### 👍 Share Your Feedback")

    last_answer = next(
        (
            message for message in reversed(st.session_state.messages)
            if message["role"] == "assistant"
        ),
        None
    )

    def save_feedback(rating):

        if last_answer is None:
            return

        DATA_DIR.mkdir(parents=True, exist_ok=True)

        file_exists = FEEDBACK_FILE.exists()

        with open(FEEDBACK_FILE, "a", newline="", encoding="utf-8") as file:

            writer = csv.writer(file)

            if not file_exists:
                writer.writerow([
                    "Timestamp",
                    "Question",
                    "Answer",
                    "Feedback"
                ])

            writer.writerow([
                datetime.now(),
                last_answer.get("question", ""),
                last_answer["content"],
                rating
            ])

    if last_answer:

        col1, col2 = st.columns(2)

        with col1:
            if st.button("👍 Helpful", use_container_width=True):
                save_feedback("Positive")
                st.success("Thank you for your feedback!")

        with col2:
            if st.button("👎 Not Helpful", use_container_width=True):
                save_feedback("Negative")
                st.success("Thank you for your feedback!")

    if st.session_state.messages and st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()


# -------------------------------
# RATION CALCULATOR
# -------------------------------

elif page == "🧾 Ration Calculator":

    st.markdown(
        '<div class="section-title">🧾 Monthly Ration Calculator</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Calculate your expected monthly foodgrain entitlement.'
        '</div>',
        unsafe_allow_html=True
    )

    with st.container(border=True):

        card_type = st.selectbox(
            "Select Ration Card Type",
            ["AAY", "PHH"]
        )

        family_size = st.number_input(
            "Number of Family Members",
            min_value=1,
            max_value=20,
            value=4
        )

        if st.button("Calculate Monthly Ration", type="primary"):

            if card_type == "AAY":
                quantity = 35
            else:
                quantity = 5 * family_size

            st.session_state.ration_slip = {
                "card_type": card_type,
                "family_size": family_size,
                "expected": quantity,
                "received": None,
                "difference": None,
                "date": datetime.now().strftime("%d-%m-%Y")
            }

    if st.session_state.ration_slip:

        slip = st.session_state.ration_slip

        st.success("Monthly entitlement calculated!")

        col1, col2, col3 = st.columns(3)

        col1.metric("Card Type", slip["card_type"])
        col2.metric("Family Members", slip["family_size"])
        col3.metric("Monthly Grain", f'{slip["expected"]} kg')

        st.metric("Expected Amount Payable", "₹0")

        st.info(
            "The price shown is based on the applicable free-foodgrain "
            "provision. Verify the current government notification."
        )


# -------------------------------
# E-POS VERIFICATION
# -------------------------------

elif page == "🔍 e-PoS Verification":

    st.markdown(
        '<div class="section-title">🔍 e-PoS Verification</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Compare your expected entitlement with the quantity received.'
        '</div>',
        unsafe_allow_html=True
    )

    slip = st.session_state.ration_slip

    if slip is None:

        st.warning(
            "Please calculate your monthly ration first "
            "using the Ration Calculator."
        )

    else:

        col1, col2 = st.columns(2)

        col1.metric("Card Type", slip["card_type"])
        col2.metric("Expected Quantity", f'{slip["expected"]} kg')

        received = st.number_input(
            "Actual Ration Received (kg)",
            min_value=0.0,
            max_value=100.0,
            value=20.0,
            step=0.5
        )

        if st.button("Compare Ration", type="primary"):

            difference = slip["expected"] - received

            st.session_state.ration_slip["received"] = received
            st.session_state.ration_slip["difference"] = difference

            st.rerun()

        slip = st.session_state.ration_slip

        if slip["received"] is not None:

            st.divider()
            st.markdown("### 📊 Comparison Result")

            col1, col2, col3 = st.columns(3)

            col1.metric("Expected", f'{slip["expected"]} kg')
            col2.metric("Received", f'{slip["received"]:g} kg')
            col3.metric("Difference", f'{abs(slip["difference"]):g} kg')

            if slip["difference"] > 0:

                st.warning(
                    f'You received {slip["difference"]:g} kg less '
                    "than your calculated entitlement. Verify your e-PoS receipt."
                )

            elif slip["difference"] < 0:

                st.info(
                    f'You received {abs(slip["difference"]):g} kg more '
                    "than your calculated entitlement. Verify the transaction."
                )

            else:

                st.success(
                    "Your received quantity matches your calculated entitlement!"
                )

            st.info(
                "This is an estimated comparison, not an official "
                "confirmation of ration distribution."
            )

            # Download ration slip
            slip_text = f"""
====================================
          RATIONSAHAYAK
          MONTHLY RATION SLIP
====================================

Date: {slip["date"]}

Card Type: {slip["card_type"]}
Family Members: {slip["family_size"]}

Expected Grain: {slip["expected"]} kg
Actually Received: {slip["received"]:g} kg
Difference: {slip["difference"]:g} kg

Expected Price: Rs. 0
Total Amount: Rs. 0

Compare these details with your official e-PoS receipt.

This is an estimated entitlement preview,
not an official ration receipt.
"""

            st.download_button(
                "📥 Download Ration Slip",
                slip_text,
                file_name="ration_slip.txt",
                mime="text/plain"
            )


# -------------------------------
# ABOUT PROJECT
# -------------------------------

elif page == "ℹ️ About Project":

    st.markdown(
        '<div class="section-title">ℹ️ About RationSahayak</div>',
        unsafe_allow_html=True
    )

    st.write(
        "RationSahayak is an AI-powered ration assistance system "
        "designed to make ration-related information easier to access."
    )

    st.write(
        "Users can ask questions about ration entitlements, "
        "understand government schemes and compare expected "
        "ration quantities with their e-PoS receipts."
    )

    st.divider()

    st.markdown("### ⚙️ Technology Stack")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Frontend**
        - Streamlit
        - Python
        - Custom CSS

        **Backend**
        - FastAPI
        - REST API
        """)

    with col2:
        st.markdown("""
        **AI and Search**
        - Large Language Model
        - Retrieval-Augmented Generation
        - ChromaDB
        - Sentence Transformers

        **Other Tools**
        - LangGraph
        - Git and GitHub
        """)


# -------------------------------
# FOOTER
# -------------------------------

st.divider()

st.markdown("""
<div class="footer">
    <b>🌾 RationSahayak</b><br>
    AI-Powered Ration Assistance System<br>
    Making ration information easier to understand and access.
</div>
""", unsafe_allow_html=True)
