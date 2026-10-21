
import sys
from pathlib import Path
from html import escape

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.utils.pdf_reader import extract_text_from_pdf
from app.document_analyzer import analyze_document
from app.task_manager import create_tasks_table, get_tasks
from app.agents.controller import (
    prepare_request,
    approve_request,
    reject_request,
    execute_approved_request,
)

st.set_page_config(
    page_title="LifeAdmin AI",
    page_icon="L",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- Google authentication --------------------

if not st.user.is_logged_in:
    st.title("Welcome to LifeAdmin AI")
    st.write("Sign in with Google to securely access your personal tasks.")
    st.button(
        "Continue with Google",
        on_click=st.login,
        args=("google",),
        type="primary",
        use_container_width=True,
    )
    st.stop()

# Use Google's stable account identifier to isolate each user's tasks.
user_subject = st.user.get("sub")
if not user_subject:
    st.error(
        "Google did not provide a user identifier. "
        "Please sign out and sign in again."
    )
    st.stop()

session_id = f"google:{user_subject}"

create_tasks_table()

# -------------------- Session state --------------------

defaults = {
    "prepared_request": None,
    "agent_result": None,
    "document_analysis": None,
    "document_name": None,
    "document_text": None,
    "navigation_page": "Overview",
    "pending_selection": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -------------------- Navigation callbacks --------------------

def navigate_to(page_name: str):
    """Update the navigation radio through a pre-rerun callback."""
    st.session_state.navigation_page = page_name


# -------------------- Styling --------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        font-size: 16px;
    }

    .stApp {
        background: #f6f7fb;
    }

    .block-container {
        max-width: 1500px;
        padding: 1rem 2rem 2rem;
    }

    [data-testid="stSidebar"] {
        background: #111827;
    }

    [data-testid="stSidebar"] * {
        color: #f3f4f6;
    }

    .brand {
        font-size: 28px;
        font-weight: 700;
        color: white;
        padding: 12px 0 4px;
    }

    .brand span {
        color: #a5b4fc;
    }

    .sidebar-caption {
        font-size: 13px;
        color: #9ca3af !important;
        margin-bottom: 26px;
    }

    .eyebrow {
        color: #6366f1;
        font-weight: 700;
        font-size: 13px;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    .hero-title {
        color: #111827;
        font-size: clamp(34px, 3.2vw, 48px);
        font-weight: 700;
        line-height: 1.15;
        margin: 10px 0 12px;
    }

    .hero-subtitle {
        color: #64748b;
        font-size: 17px;
        line-height: 1.75;
        max-width: 820px;
    }

    .section-title {
        color: #111827;
        font-size: 25px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .section-subtitle {
        color: #64748b;
        font-size: 16px;
        margin-bottom: 22px;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e5e7eb;
        padding: 22px;
        border-radius: 16px;
    }

    div[data-testid="stForm"] {
        background: white;
        border: 1px solid #e5e7eb;
        padding: 24px;
        border-radius: 18px;
    }

    div.stButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        border-radius: 11px;
        font-size: 15px;
        font-weight: 600;
        min-height: 46px;
    }

    .task-name {
        color: #111827;
        font-size: 18px;
        font-weight: 700;
        overflow-wrap: anywhere;
    }

    .footer {
        color: #94a3b8;
        font-size: 13px;
        text-align: center;
        padding: 32px 0 12px;
    }

    #MainMenu, footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------- Sidebar --------------------

with st.sidebar:
    st.markdown(
        '<div class="brand">LifeAdmin<span>.</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sidebar-caption">YOUR PERSONAL ADMIN ASSISTANT</div>',
        unsafe_allow_html=True,
    )

    page = st.radio(
        "NAVIGATION",
        ["Overview", "AI Assistant", "Documents", "My Tasks"],
        key="navigation_page",
    )

    st.divider()
    st.caption(f"Signed in as {st.user.get('email', 'Google user')}")

    if st.button(
        "Sign out",
        use_container_width=True,
        key="sign_out_button",
    ):
        st.logout()

    st.caption("Less admin. More time for what matters.")


# -------------------- Shared data --------------------

tasks = get_tasks(session_id=session_id)

pending_tasks = [
    task for task in tasks
    if str(task[4]).lower() == "pending"
]

completed_tasks = [
    task for task in tasks
    if str(task[4]).lower() == "completed"
]

st.markdown(
    '<div class="eyebrow">YOUR DAY, SIMPLIFIED</div>',
    unsafe_allow_html=True,
)

if page == "Overview":
    st.markdown(
        '<div class="hero-title">Make room for what matters.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-subtitle">Keep track of tasks, understand '
        'your documents, and prepare actions for your approval.</div>',
        unsafe_allow_html=True,
    )

elif page == "AI Assistant":
    st.markdown(
        '<div class="hero-title">Your personal assistant.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-subtitle">Tell LifeAdmin what you need. '
        'Review its plan before any action.</div>',
        unsafe_allow_html=True,
    )

elif page == "Documents":
    st.markdown(
        '<div class="hero-title">Your documents, understood.</div>',
        unsafe_allow_html=True,
    )

else:
    st.markdown(
        '<div class="hero-title">Everything on your plate.</div>',
        unsafe_allow_html=True,
    )

st.write("")


# -------------------- Overview --------------------

if page == "Overview":
    c1, c2, c3 = st.columns(3)
    c1.metric("Tasks to do", len(pending_tasks))
    c2.metric("Completed", len(completed_tasks))
    c3.metric(
        "Documents analyzed",
        1 if st.session_state.document_analysis else 0,
    )

    st.write("")
    st.markdown("### Where would you like to start?")

    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):
            st.subheader("AI Assistant")
            st.write("Create, update, complete, or delete tasks.")
            st.button(
                "Open assistant",
                type="primary",
                use_container_width=True,
                on_click=navigate_to,
                args=("AI Assistant",),
                key="open_assistant_button",
            )

    with c2:
        with st.container(border=True):
            st.subheader("Document Intelligence")
            st.write("Find dates and actions in a PDF.")
            st.button(
                "Analyze a document",
                use_container_width=True,
                on_click=navigate_to,
                args=("Documents",),
                key="open_documents_button",
            )

    st.markdown("### Your next tasks")

    if pending_tasks:
        for task in pending_tasks[:4]:
            with st.container(border=True):
                st.markdown(
                    f'<div class="task-name">{escape(str(task[1]))}</div>',
                    unsafe_allow_html=True,
                )
                a, b, c = st.columns(3)
                a.caption(f"Due: {task[2] or 'Not set'}")
                b.caption(f"Priority: {task[3] or 'Medium'}")
                c.caption(f"Status: {task[4]}")
    else:
        st.info(
            "You're all caught up. Add a task with the AI Assistant."
        )


# -------------------- AI Assistant --------------------

elif page == "AI Assistant":
    st.markdown("### What can I help you with?")

    pending_selection = st.session_state.pending_selection
    candidates = (
        pending_selection.get("candidate_tasks", [])
        if pending_selection else []
    )

    with st.form("agent_request_form", clear_on_submit=False):
        if pending_selection and candidates:
            st.info(
                "The assistant needs you to identify a task. "
                "Enter its number below. Your original request "
                "will be preserved."
            )

            for index, task in enumerate(candidates, start=1):
                st.write(
                    f"**{index}.** {task.get('title', 'Untitled task')} "
                    f"— {task.get('status', 'Unknown')} "
                    f"(ID {task.get('id')})"
                )

            task_number = st.text_input(
                "Your answer (enter the task number)",
                placeholder="For example: 2",
            )
            user_request = ""
        else:
            user_request = st.text_area(
                "Your request",
                placeholder=(
                    "For example: Delete my gym task, change its priority, "
                    "or remind me to submit my report."
                ),
                height=110,
            )
            task_number = ""

        submitted = st.form_submit_button(
            "Continue" if pending_selection else "Prepare my request",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        try:
            if pending_selection and candidates:
                if not task_number.strip().isdigit():
                    st.error("Enter a valid task number, such as 1 or 2.")
                else:
                    choice = int(task_number.strip())

                    if choice < 1 or choice > len(candidates):
                        st.error(
                            f"Choose a number between 1 and {len(candidates)}."
                        )
                    else:
                        selected_candidate = candidates[choice - 1]
                        original_request = pending_selection["original_request"]

                        with st.spinner("Preparing the selected task..."):
                            result = prepare_request(
                                original_request,
                                session_id=session_id,
                                chosen_task_id=int(selected_candidate["id"]),
                            )

                        st.session_state.prepared_request = result
                        st.session_state.agent_result = None

                        if result.get("clarification_required"):
                            new_candidates = result.get("candidate_tasks", [])
                            st.session_state.pending_selection = {
                                "original_request": original_request,
                                "candidate_tasks": new_candidates,
                            }
                        else:
                            st.session_state.pending_selection = None

                        st.rerun()

            elif not user_request.strip():
                st.warning("Please enter a request first.")

            else:
                with st.spinner("Understanding your request..."):
                    result = prepare_request(
                        user_request.strip(),
                        session_id=session_id,
                    )

                st.session_state.prepared_request = result
                st.session_state.agent_result = None

                if (
                    result.get("clarification_required")
                    and result.get("candidate_tasks")
                ):
                    st.session_state.pending_selection = {
                        "original_request": user_request.strip(),
                        "candidate_tasks": result["candidate_tasks"],
                    }
                else:
                    st.session_state.pending_selection = None

                st.rerun()

        except Exception as exc:
            st.error(f"The assistant couldn't prepare this request: {exc}")

    result = st.session_state.prepared_request

    if result:
        if result.get("session_id") != session_id:
            st.session_state.prepared_request = None
            st.session_state.pending_selection = None
            st.warning("Session mismatch. Please prepare your request again.")
            st.stop()

        st.write("")
        st.markdown("### Review your plan")

        c1, c2, c3 = st.columns(3)
        c1.metric(
            "Request type",
            str(result.get("intent", "Unknown")).replace("_", " ").title(),
        )
        c2.metric(
            "Approval needed",
            "Yes" if result.get("approval_required") else "No",
        )
        c3.metric(
            "Status",
            "Awaiting review" if result.get("approval_required")
            else "Needs clarification" if result.get("clarification_required")
            else "Ready",
        )

        with st.container(border=True):
            st.subheader("Proposed action")

            plan = result.get("plan") or []
            if plan:
                for index, step in enumerate(plan, start=1):
                    st.markdown(f"**{index}.** {step}")
            else:
                st.write("No action plan was generated.")

            st.subheader("Assistant response")
            st.write(result.get("response", "No response available."))

        if result.get("approval_required"):
            st.warning(
                "Nothing will change until you approve the proposed action."
            )

            c1, c2 = st.columns(2)

            with c1:
                if st.button(
                    "Approve and execute",
                    type="primary",
                    use_container_width=True,
                    key="approve_agent_action",
                ):
                    try:
                        if result.get("session_id") != session_id:
                            st.error(
                                "Session mismatch. Prepare the request again."
                            )
                            st.stop()

                        approved_state = approve_request(result)
                        executed_state = execute_approved_request(
                            approved_state.__dict__
                        )

                        st.session_state.agent_result = executed_state
                        st.session_state.prepared_request = (
                            executed_state.__dict__
                        )
                        st.session_state.pending_selection = None

                        st.success(executed_state.response)
                        st.rerun()

                    except Exception as exc:
                        st.error(f"The action could not be executed: {exc}")

            with c2:
                if st.button(
                    "Reject action",
                    use_container_width=True,
                    key="reject_agent_action",
                ):
                    try:
                        rejected_state = reject_request(result)
                        st.session_state.agent_result = rejected_state
                        st.session_state.prepared_request = (
                            rejected_state.__dict__
                        )
                        st.session_state.pending_selection = None
                        st.info("Action rejected. No changes were made.")
                        st.rerun()

                    except Exception as exc:
                        st.error(f"The action could not be rejected: {exc}")

        elif result.get("current_step") == "Task executed":
            st.success(result.get("response", "Action completed."))


# -------------------- Documents --------------------

elif page == "Documents":
    st.markdown("### Analyze a PDF")

    uploaded_file = st.file_uploader(
        "Choose a PDF document",
        type=["pdf"],
    )

    if uploaded_file is not None:
        if st.button("Analyze document", type="primary"):
            try:
                with st.spinner("Reading your document..."):
                    text = extract_text_from_pdf(uploaded_file)
                    st.session_state.document_name = uploaded_file.name
                    st.session_state.document_text = text

                    if text and text.strip():
                        st.session_state.document_analysis = analyze_document(text)
                    else:
                        st.session_state.document_analysis = None

            except Exception as exc:
                st.error(f"Unable to analyze this PDF: {exc}")

    if st.session_state.document_name:
        st.caption(
            f"Last selected document: {st.session_state.document_name}"
        )

    analysis = st.session_state.document_analysis

    if analysis:
        with st.container(border=True):
            st.markdown("**Document type**")
            st.write(analysis.get("document_type") or "Not identified")

            st.markdown("**Important date**")
            st.write(analysis.get("important_date") or "No date identified")

            st.markdown("**Action required**")
            st.write(analysis.get("action_required") or "No action identified")

            st.markdown("**Priority**")
            st.write(analysis.get("priority") or "Not determined")

        with st.expander("View extracted text"):
            st.text((st.session_state.document_text or "")[:12000])

    elif st.session_state.document_name:
        st.warning(
            "No readable text was extracted. Scanned PDFs may require OCR."
        )


# -------------------- My Tasks --------------------

elif page == "My Tasks":
    c1, c2, c3 = st.columns(3)
    c1.metric("Total tasks", len(tasks))
    c2.metric("Pending", len(pending_tasks))
    c3.metric("Completed", len(completed_tasks))

    filter_status = st.selectbox(
        "Show tasks",
        ["All", "Pending", "Completed"],
    )

    visible_tasks = tasks

    if filter_status != "All":
        visible_tasks = [
            task for task in tasks
            if str(task[4]).lower() == filter_status.lower()
        ]

    if visible_tasks:
        for task in visible_tasks:
            task_id, title, due_date, priority, status = task[:5]

            with st.container(border=True):
                st.markdown(
                    f'<div class="task-name">{escape(str(title))}</div>',
                    unsafe_allow_html=True,
                )

                a, b, c = st.columns(3)
                a.caption(f"Due date: {due_date or 'Not set'}")
                b.caption(f"Priority: {priority or 'Medium'}")
                c.caption(f"Status: {status}")

                st.caption(f"Task ID: {task_id}")
    else:
        st.info("No tasks match this filter.")


# -------------------- Footer --------------------

st.markdown(
    '<div class="footer">LifeAdmin AI · Personal administration, made simpler.</div>',
    unsafe_allow_html=True,
)
