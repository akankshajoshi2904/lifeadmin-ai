import streamlit as st

from utils.pdf_reader import extract_text_from_pdf
from document_analyzer import analyze_document
from task_manager import create_tasks_table, add_task, get_tasks


# -----------------------------------
# Initialize database
# -----------------------------------

create_tasks_table()


# -----------------------------------
# Streamlit configuration
# -----------------------------------

st.set_page_config(
    page_title="LifeAdmin AI",
    page_icon="🧾",
    layout="wide"
)


# -----------------------------------
# Application header
# -----------------------------------

st.title("🧾 LifeAdmin AI")
st.subheader("Your Personal Administration Agent")

st.write(
    "Upload your important documents and LifeAdmin AI "
    "will identify important information and create tasks."
)

st.divider()


# -----------------------------------
# Document upload
# -----------------------------------

st.header("📄 Upload a Document")

uploaded_file = st.file_uploader(
    "Upload a PDF document",
    type=["pdf"]
)


if uploaded_file is not None:

    st.success(f"Uploaded: {uploaded_file.name}")

    if st.button("📖 Analyze Document"):

        with st.spinner("Reading document..."):

            extracted_text = extract_text_from_pdf(uploaded_file)

        if extracted_text.strip():

            # -----------------------------------
            # Show extracted text
            # -----------------------------------

            st.subheader("📄 Extracted Text")

            st.text_area(
                "Document content",
                extracted_text,
                height=300
            )

            st.divider()

            # -----------------------------------
            # Analyze document
            # -----------------------------------

            st.subheader("🤖 Document Analysis")

            analysis = analyze_document(extracted_text)

            st.write(
                "**Document Type:**",
                analysis["document_type"]
            )

            st.write(
                "**Important Date:**",
                analysis["important_date"]
            )

            st.write(
                "**Amount:**",
                analysis["amount"]
            )

            st.write(
                "**Action Required:**",
                analysis["action_required"]
            )

            st.write(
                "**Priority:**",
                analysis["priority"]
            )

            st.divider()

            # -----------------------------------
            # Create task
            # -----------------------------------

            if analysis["action_required"]:

                document_type = analysis["document_type"]

                action = analysis["action_required"]

                task_title = f"{action} {document_type}"

                task_created = add_task(
                    title=task_title,
                    due_date=analysis["important_date"],
                    priority=analysis["priority"]
                )

                if task_created:

                    st.success(
                        f"✅ Task created: {task_title}"
                    )

                else:

                    st.info(
                        f"ℹ️ This task already exists: {task_title}"
                    )

            else:

                st.info(
                    "No action was detected in this document."
                )

        else:

            st.warning(
                "I could not extract text from this PDF. "
                "It may be a scanned/image-based document."
            )


# -----------------------------------
# Task dashboard
# -----------------------------------

st.divider()

st.header("📋 Your Tasks")

tasks = get_tasks()

if tasks:

    for task in tasks:

        task_id = task[0]
        title = task[1]
        due_date = task[2]
        priority = task[3]
        status = task[4]

        st.write(
            f"**{title}**"
        )

        st.write(
            f"Due: {due_date}  |  "
            f"Priority: {priority}  |  "
            f"Status: {status}"
        )

        st.divider()

else:

    st.info("No tasks yet.")