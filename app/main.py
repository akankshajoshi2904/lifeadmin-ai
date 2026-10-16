import sys
from pathlib import Path
from html import escape

import streamlit as st

# Ensure imports work locally and on Streamlit Community Cloud.
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

create_tasks_table()

# -------------------- Google Authentication --------------------

if not st.user.is_logged_in:
    st.markdown(
        """
        <style>
        .stApp {
            background: #f6f7fb;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("LifeAdmin AI")
    st.subheader("Your personal administration assistant")
    st.write(
        "Sign in with Google to manage your personal tasks "
        "and documents."
    )

    st.button(
        "Continue with Google",
        type="primary",
        use_container_width=True,
        on_click=st.login,
        args=("google",),
    )

    st.stop()

# Google's stable account identifier.
user_id = st.user.get("sub")

if not user_id:
    st.error(
        "Google sign-in did not provide an account identifier. "
        "Please sign out and sign in again."
    )
    st.stop()

# -------------------- Session State --------------------

defaults = {
    "prepared_request": None,
    "agent_result": None,
    "document_analysis": None,
    "document_name": None,
    "document_text": None,
    "navigation_page": "Overview",
    "pending_navigation": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Apply navigation before the radio widget is created.
pending_page = st.session_state.pop("pending_navigation", None)
if pending_page in ["Overview", "AI Assistant", "Documents", "My Tasks"]:
    st.session_state["navigation_page"] = pending_page

# -------------------- Styling --------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background: #f6f7fb;
    }

    [data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #273244;
    }

    [data-testid="stSidebar"] * {
        color: #f3f4f6;
    }

    .brand {
        font-size: 25px;
        font-weight: 700;
        letter-spacing: -1px;
        color: #ffffff;
        padding: 12px 0 2px 0;
    }

    .brand span {
        color: #a5b4fc;
    }

    .sidebar-caption {
        font-size: 12px;
        color: #9ca3af !important;
        margin-bottom: 24px;
    }

    .eyebrow {
        color: #6366f1;
        font-weight: 700;
        font-size: 12px;
        letter-spacing: 1.4px;
        text-transform: uppercase;
    }

    .hero-title {
        color: #111827;
        font-size: clamp(30px, 4vw, 42px);
        font-weight: 700;
        letter-spacing: -1.7px;
        line-height: 1.15;
        margin: 8px 0;
    }

    .hero-subtitle {
        color: #64748b;
        font-size: 15px;
        line-height: 1.7;
        max-width: 700px;
    }

    .section-title {
        color: #111827;
        font-size: 21px;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-bottom: 3px;
    }

    .section-subtitle {
        color: #64748b;
        font-size: 13px;
        margin-bottom: 18px;
    }

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        padding: 18px 20px;
        border-radius: 14px;
        box-shadow: 0 3px 12px rgba(15, 23, 42, 0.025);
    }

    div[data-testid="stMetricLabel"] {
        color: #64748b;
    }

    div[data-testid="stMetricValue"] {
        color: #111827;
        font-weight: 700;
    }

    div[data-testid="stForm"] {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        padding: 20px;
        border-radius: 16px;
    }

    div.stButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        border-radius: 10px;
        font-weight: 600;
        min-height: 42px;
        transition: all 0.15s ease;
    }

    div.stButton > button[kind="primary"],
    div[data-testid="stFormSubmitButton"] > button[kind="primary"] {
        background: #4f46e5;
        border-color: #4f46e5;
        color: #ffffff;
    }

    div.stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
        border-color: #818cf8;
    }

    div[data-testid="stFileUploader"] {
        background: #ffffff;
        border: 1px dashed #c7d2fe;
        border-radius: 14px;
        padding: 12px;
    }

    .task-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 13px;
        padding: 17px 18px;
        margin: 8px 0;
    }

    .task-name {
        color: #111827;
        font-size: 15px;
        font-weight: 700;
        overflow-wrap: anywhere;
    }

    .muted {
        color: #64748b;
        font-size: 12px;
    }

    .footer {
        color: #94a3b8;
        font-size: 12px;
        text-align: center;
        padding: 25px 0 10px 0;
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
        '<div class="sidebar-caption">'
        'YOUR PERSONAL ADMIN ASSISTANT'
        '</div>',
        unsafe_allow_html=True,
    )

    st.caption(f"Signed in as: {st.user.get('email', 'Google user')}")

    if st.button("Sign out", use_container_width=True):
        st.logout()

    page = st.radio(
        "NAVIGATION",
        ["Overview", "AI Assistant", "Documents", "My Tasks"],
        key="navigation_page",
        label_visibility="visible",
    )

    st.divider()
    st.caption("Less admin. More time for what matters.")

# -------------------- Shared Data --------------------

# Each user's tasks are identified by their Google account ID.
tasks = get_tasks(session_id=user_id)

pending_tasks = [
    task for task in tasks
    if str(task[4]).lower() == "pending"
]

completed_tasks = [
    task for task in tasks
    if str(task[4]).lower() == "completed"
]

# -------------------- Header --------------------

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
        '<div class="hero-subtitle">'
        'Keep track of important tasks, understand your documents, '
        'and let your assistant prepare actions for your approval.'
        '</div>',
        unsafe_allow_html=True,
    )

elif page == "AI Assistant":
    st.markdown(
        '<div class="hero-title">Your personal assistant.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-subtitle">'
        'Tell LifeAdmin what you need. Review its plan before '
        'any action that requires your approval.'
        '</div>',
        unsafe_allow_html=True,
    )

elif page == "Documents":
    st.markdown(
        '<div class="hero-title">Your documents, understood.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-subtitle">'
        'Extract useful dates and actions from a PDF without '
        'reading the entire document again.'
        '</div>',
        unsafe_allow_html=True,
    )

else:
    st.markdown(
        '<div class="hero-title">Everything on your plate.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-subtitle">'
        'A clear view of saved tasks, deadlines, priorities, and status.'
        '</div>',
        unsafe_allow_html=True,
    )

st.write("")

# -------------------- Overview --------------------

if page == "Overview":
    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Tasks to do", len(pending_tasks))

    with c2:
        st.metric("Completed", len(completed_tasks))

    with c3:
        st.metric(
            "Documents analyzed",
            1 if st.session_state.document_analysis else 0,
        )

    st.write("")

    st.markdown(
        '<div class="section-title">Where would you like to start?</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">'
        'Choose what you need. You can come back here anytime.'
        '</div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):
            st.subheader("AI Assistant")
            st.write(
                "Create a task, review your workload, or prepare "
                "an action with human approval."
            )

            if st.button(
                "Open assistant",
                key="overview_assistant",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.pending_navigation = "AI Assistant"
                st.rerun()

    with c2:
        with st.container(border=True):
            st.subheader("Document Intelligence")
            st.write(
                "Upload a PDF to find important dates, required "
                "actions, and priority."
            )

            if st.button(
                "Analyze a document",
                key="overview_documents",
                use_container_width=True,
            ):
                st.session_state.pending_navigation = "Documents"
                st.rerun()

    st.write("")
    st.markdown(
        '<div class="section-title">Your next tasks</div>',
        unsafe_allow_html=True,
    )

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
        st.info("You're all caught up. Add a task with the AI Assistant.")

# -------------------- AI Assistant --------------------

elif page == "AI Assistant":
    st.markdown(
        '<div class="section-title">What can I help you with?</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">'
        'Use everyday language. For example: "Remind me to submit '
        'my project report by 20 October 2026."'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.form("agent_request_form", clear_on_submit=False):
        user_request = st.text_area(
            "Your request",
            placeholder=(
                "Tell me what you need to do, finish, or keep track of..."
            ),
            height=100,
        )

        run_agent = st.form_submit_button(
            "Prepare my request",
            type="primary",
            use_container_width=True,
        )

    if run_agent:
        if not user_request.strip():
            st.warning("Please enter a request first.")
        else:
            try:
                with st.spinner("Understanding your request..."):
                    result = prepare_request(
                        user_request.strip(),
                        session_id=user_id,
                    )

                st.session_state.prepared_request = result
                st.session_state.agent_result = None

            except Exception as exc:
                st.error(
                    f"The assistant couldn't prepare this request: {exc}"
                )

    result = st.session_state.prepared_request

    if result:
        # Prevent a prepared action from another account being used.
        if result.get("session_id") != user_id:
            st.session_state.prepared_request = None
            st.session_state.agent_result = None
            st.warning(
                "This request belongs to another account or an earlier "
                "session. Please prepare your request again."
            )
            st.stop()

        st.write("")
        st.markdown(
            '<div class="section-title">Review your plan</div>',
            unsafe_allow_html=True,
        )

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
            (
                "Approved"
                if result.get("approved")
                else "Awaiting review"
                if result.get("approval_required")
                else "Ready"
            ),
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
            st.write("")
            st.warning(
                "Nothing will be changed until you approve the proposed action."
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
                        if result.get("session_id") != user_id:
                            st.error(
                                "Account mismatch. Please prepare the request again."
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

                        st.success("The approval workflow finished.")
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

                        st.info(
                            "Action rejected. No approved action was executed."
                        )
                        st.rerun()

                    except Exception as exc:
                        st.error(f"The action could not be rejected: {exc}")

        elif result.get("current_step") == "Task executed":
            st.success(result.get("response", "Action completed."))

# -------------------- Documents --------------------

elif page == "Documents":
    st.markdown(
        '<div class="section-title">Analyze a PDF</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">'
        'Your file is processed by this application. Only PDF files are accepted.'
        '</div>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose a PDF document",
        type=["pdf"],
        help="Select a PDF that contains dates, actions, or obligations.",
    )

    if uploaded_file is not None:
        if st.button(
            "Analyze document",
            type="primary",
            use_container_width=True,
        ):
            try:
                with st.spinner("Reading your document..."):
                    text = extract_text_from_pdf(uploaded_file)

                    st.session_state.document_name = uploaded_file.name
                    st.session_state.document_text = text

                    if text and text.strip():
                        st.session_state.document_analysis = analyze_document(
                            text
                        )
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
        st.write("")
        st.markdown(
            '<div class="section-title">Document findings</div>',
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            st.markdown("**Document type**")
            st.write(analysis.get("document_type") or "Not identified")

            st.markdown("**Important date**")
            st.write(analysis.get("important_date") or "No date identified")

            st.markdown("**Action required**")
            st.write(analysis.get("action_required") or "No action identified")

            st.markdown("**Priority**")
            priority = analysis.get("priority") or "Not determined"

            if priority == "High":
                st.error(f"Priority: {priority}")
            elif priority == "Medium":
                st.warning(f"Priority: {priority}")
            else:
                st.info(f"Priority: {priority}")

        if analysis.get("action_required"):
            st.info(
                "You can use the AI Assistant to prepare a task based on "
                "these findings. Review the proposed task before approving it."
            )

        with st.expander("View extracted text"):
            extracted = st.session_state.document_text or ""
            st.text(extracted[:12000])

            if len(extracted) > 12000:
                st.caption("Showing the first 12,000 characters.")

    elif st.session_state.document_name:
        st.warning(
            "No readable text was extracted. This may be a scanned PDF "
            "that requires OCR, which is not currently configured."
        )

# -------------------- My Tasks --------------------

elif page == "My Tasks":
    c1, c2, c3 = st.columns(3)

    c1.metric("Total tasks", len(tasks))
    c2.metric("Pending", len(pending_tasks))
    c3.metric("Completed", len(completed_tasks))

    st.write("")

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
    '<div class="footer">'
    'LifeAdmin AI · Personal administration, made simpler.'
    '</div>',
    unsafe_allow_html=True,
)