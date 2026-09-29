import streamlit as st

from app.utils.pdf_reader import extract_text_from_pdf
from app.document_analyzer import analyze_document
from app.task_manager import create_tasks_table, get_tasks
from app.agents.controller import (
    prepare_request,
    approve_request,
    reject_request,
    execute_approved_request,
)


# -----------------------------------
# Initialize database
# -----------------------------------

create_tasks_table()


# -----------------------------------
# Streamlit configuration
# -----------------------------------

st.set_page_config(
    page_title="LifeAdmin AI",
    page_icon="🤖",
    layout="wide"
)


# -----------------------------------
# Session state
# -----------------------------------

if "prepared_request" not in st.session_state:
    st.session_state.prepared_request = None

if "agent_result" not in st.session_state:
    st.session_state.agent_result = None


# -----------------------------------
# Header
# -----------------------------------

st.title("🤖 LifeAdmin AI")

st.subheader("Your Agentic Personal Administration Assistant")

st.write(
    "LifeAdmin AI understands your request, creates a plan, "
    "asks for human approval, and executes approved actions."
)

st.divider()


# ===================================
# AI AGENT
# ===================================

st.header("🧠 AI Agent")

user_request = st.text_input(
    "What would you like LifeAdmin AI to do?",
    placeholder=(
        "Example: Create a task to submit my project report "
        "by 10 October 2026"
    )
)


if st.button("🚀 Run Agent"):

    if not user_request.strip():

        st.warning("Please enter a request first.")

    else:

        with st.spinner("Agent is analyzing your request..."):

            result = prepare_request(user_request)

        st.session_state.prepared_request = result
        st.session_state.agent_result = None


# -----------------------------------
# Show agent plan
# -----------------------------------

if st.session_state.prepared_request:

    result = st.session_state.prepared_request

    st.divider()

    st.header("🔍 Agent Analysis")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Detected Intent",
            result["intent"]
        )

    with col2:
        st.metric(
            "Approval Required",
            "Yes" if result["approval_required"] else "No"
        )

    with col3:
        st.metric(
            "Approved",
            "Yes" if result["approved"] else "No"
        )

    st.subheader("📋 Agent Plan")

    if result["plan"]:

        for step in result["plan"]:
            st.write(f"• {step}")

    else:

        st.info("No action plan was generated.")

    st.subheader("💬 Agent Response")

    st.info(result["response"])


    # -----------------------------------
    # Human approval
    # -----------------------------------

    if result["approval_required"]:

        st.divider()

        st.subheader("👤 Human Approval Required")

        st.warning(
            "The agent has prepared an action but will not "
            "execute it without your approval."
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "✅ Approve Action",
                use_container_width=True
            ):

                approved_state = approve_request(result)

                executed_state = execute_approved_request(
                    approved_state.__dict__
                )

                st.session_state.agent_result = executed_state

                st.success(
                    "Action approved and executed successfully."
                )

        with col2:

            if st.button(
                "❌ Reject Action",
                use_container_width=True
            ):

                rejected_state = reject_request(result)

                st.session_state.agent_result = rejected_state

                st.error(
                    "Action rejected. No changes were made."
                )


# -----------------------------------
# Execution result
# -----------------------------------

if st.session_state.agent_result:

    result = st.session_state.agent_result

    st.divider()

    st.subheader("⚡ Action Result")

    if result.current_step == "Task executed":

        st.success(
            result.response
        )

    elif result.current_step == "Action rejected":

        st.error(
            "The action was rejected and was not executed."
        )

    else:

        if result.approved:

            st.success(
                "Human approval received."
            )

        else:

            st.info(
                result.response
            )

    st.write(
        f"**Current Step:** {result.current_step}"
    )


# ===================================
# DOCUMENT ANALYSIS
# ===================================

st.divider()

st.header("📄 Document Intelligence")

st.write(
    "Upload a PDF and LifeAdmin AI will extract important "
    "information and identify potential actions."
)

uploaded_file = st.file_uploader(
    "Upload a PDF document",
    type=["pdf"]
)


if uploaded_file is not None:

    st.success(
        f"Uploaded: {uploaded_file.name}"
    )

    if st.button("📖 Analyze Document"):

        with st.spinner("Reading document..."):

            extracted_text = extract_text_from_pdf(
                uploaded_file
            )

        if extracted_text.strip():

            st.subheader("📄 Extracted Text")

            st.text_area(
                "Document content",
                extracted_text,
                height=250
            )

            analysis = analyze_document(
                extracted_text
            )

            st.divider()

            st.subheader("🤖 Document Analysis")

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    f"**Document Type:** "
                    f"{analysis['document_type']}"
                )

                st.write(
                    f"**Important Date:** "
                    f"{analysis['important_date']}"
                )

                st.write(
                    f"**Amount:** "
                    f"{analysis['amount']}"
                )

            with col2:

                st.write(
                    f"**Action Required:** "
                    f"{analysis['action_required']}"
                )

                st.write(
                    f"**Priority:** "
                    f"{analysis['priority']}"
                )

            if analysis["action_required"]:

                st.info(
                    "A potential task was detected. "
                    "Use the AI Agent above if you want "
                    "LifeAdmin AI to prepare this action "
                    "for human approval."
                )

            else:

                st.info(
                    "No action was detected in this document."
                )

        else:

            st.warning(
                "I could not extract text from this PDF. "
                "It may be a scanned or image-based document."
            )


# ===================================
# TASK DASHBOARD
# ===================================

st.divider()

st.header("📋 Task Memory")

tasks = get_tasks()

if tasks:

    for task in tasks:

        task_id = task[0]
        title = task[1]
        due_date = task[2]
        priority = task[3]
        status = task[4]

        with st.container():

            st.subheader(
                f"#{task_id} — {title}"
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(
                    f"📅 **Due:** {due_date}"
                )

            with col2:
                st.write(
                    f"⚡ **Priority:** {priority}"
                )

            with col3:
                st.write(
                    f"📌 **Status:** {status}"
                )

        st.divider()

else:

    st.info("No tasks yet.")