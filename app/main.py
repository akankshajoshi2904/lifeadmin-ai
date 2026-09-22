import streamlit as st

from utils.pdf_reader import extract_text_from_pdf


st.set_page_config(
    page_title="LifeAdmin AI",
    page_icon="🧾",
    layout="wide"
)


st.title("🧾 LifeAdmin AI")
st.subheader("Your Personal Administration Agent")

st.write(
    "Upload your important documents and LifeAdmin AI "
    "will help identify important information and actions."
)


st.divider()


st.header("📄 Upload a Document")

uploaded_file = st.file_uploader(
    "Upload a PDF document",
    type=["pdf"]
)


if uploaded_file is not None:

    st.success(f"Uploaded: {uploaded_file.name}")

    if st.button("📖 Read Document"):

        with st.spinner("Reading document..."):

            extracted_text = extract_text_from_pdf(uploaded_file)

        if extracted_text.strip():

            st.subheader("Extracted Text")

            st.text_area(
                "Document content",
                extracted_text,
                height=400
            )

        else:

            st.warning(
                "I could not extract text from this PDF. "
                "It may be a scanned/image-based document."
            )