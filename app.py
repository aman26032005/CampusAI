import os
import hashlib
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

load_dotenv()

st.set_page_config(
    page_title="CampusAI | AI Study Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL = "openai/gpt-oss-20b"

# Add your GROQ_API_KEY to .env.
# Never put the actual key in this file.
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error(
        "Groq API key not found. Add GROQ_API_KEY to your .env file."
    )
    st.stop()

client = Groq(api_key=api_key)


# --------------------------------------------------
# PROFESSIONAL UI
# --------------------------------------------------

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 2rem;
        border-radius: 20px;
        background: linear-gradient(120deg, #14213d, #315c91);
        color: white;
        margin-bottom: 1.5rem;
    }

    .hero h1 {
        color: white;
        font-size: 2.6rem;
        margin-bottom: 0.4rem;
    }

    .hero p {
        color: #e3edff;
        font-size: 1.05rem;
        margin-bottom: 0;
    }

    .small-note {
        color: #808899;
        font-size: 0.9rem;
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(128, 128, 128, 0.25);
        padding: 14px;
        border-radius: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>🎓 CampusAI</h1>
        <p>Your syllabus. Your AI. Your success.</p>
        <p>Understand concepts, prepare for exams, and study smarter.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "documents" not in st.session_state:
    st.session_state.documents = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "document_signature" not in st.session_state:
    st.session_state.document_signature = ""


# --------------------------------------------------
# PDF PROCESSING
# --------------------------------------------------

def split_into_chunks(text, max_words=220, overlap=40):
    """Create overlapping text chunks."""

    words = text.split()

    if not words:
        return []

    output = []
    start = 0

    while start < len(words):
        end = min(start + max_words, len(words))
        output.append(" ".join(words[start:end]))

        if end == len(words):
            break

        start = end - overlap

    return output


def extract_pdfs(uploaded_files):
    """Extract text while preserving document names and PDF pages."""

    all_chunks = []
    document_names = []
    pages_with_text = 0
    total_pages = 0

    for uploaded_file in uploaded_files:
        file_bytes = uploaded_file.getvalue()
        file_hash = hashlib.sha256(file_bytes).hexdigest()[:12]

        reader = PdfReader(BytesIO(file_bytes))
        document_names.append(uploaded_file.name)
        total_pages += len(reader.pages)

        for page_number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""

            if not page_text.strip():
                continue

            pages_with_text += 1

            for chunk_number, chunk_text in enumerate(
                split_into_chunks(page_text), start=1
            ):
                all_chunks.append(
                    {
                        "document": uploaded_file.name,
                        "document_id": file_hash,
                        "page": page_number,
                        "chunk": chunk_number,
                        "text": chunk_text,
                    }
                )

    return all_chunks, document_names, total_pages, pages_with_text


# --------------------------------------------------
# RETRIEVAL
# --------------------------------------------------

def retrieve_chunks(question, chunks, top_k=5, selected_documents=None):
    """Find relevant PDF passages using TF-IDF and cosine similarity."""

    if not chunks:
        return []

    selected_documents = selected_documents or []

    candidates = [
        item
        for item in chunks
        if not selected_documents
        or item["document"] in selected_documents
    ]

    if not candidates:
        return []

    texts = [item["text"] for item in candidates]

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
    )

    try:
        matrix = vectorizer.fit_transform(texts)
        query_vector = vectorizer.transform([question])
        scores = cosine_similarity(query_vector, matrix).ravel()
    except ValueError:
        return []

    ranked_indices = scores.argsort()[::-1]
    results = []

    for index in ranked_indices:
        score = float(scores[index])

        if score <= 0:
            continue

        item = dict(candidates[index])
        item["score"] = score
        results.append(item)

        if len(results) >= top_k:
            break

    return results


# --------------------------------------------------
# AI HELPER
# --------------------------------------------------

def ask_ai(system_prompt, user_prompt, max_tokens=1200):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_tokens,
    )

    return response.choices[0].message.content or ""


def make_context(retrieved_chunks):
    """Format retrieved passages with verifiable source labels."""

    return "\n\n".join(
        (
            f"[Document: {item['document']} | "
            f"PDF Page: {item['page']}]\n"
            f"{item['text']}"
        )
        for item in retrieved_chunks
    )


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown("## 🎓 CampusAI")
    st.caption("Your personal AI study companion")
    st.divider()

    feature = st.radio(
        "Navigate",
        [
            "🏠 Dashboard",
            "💬 Ask CampusAI",
            "📝 Summarize Notes",
            "✅ Generate MCQs",
            "📚 Revision Questions",
        ],
    )

    st.divider()

    st.markdown("### 📂 Your Study Library")

    uploaded_files = st.file_uploader(
        "Upload one or more PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        help="You can select multiple college notes PDFs.",
    )

    if uploaded_files:
        signature = hashlib.sha256(
            "".join(
                f"{file.name}:{len(file.getvalue())}:"
                f"{hashlib.sha256(file.getvalue()).hexdigest()}"
                for file in uploaded_files
            ).encode()
        ).hexdigest()

        if signature != st.session_state.document_signature:
            try:
                with st.spinner("Reading your study materials..."):
                    (
                        extracted_chunks,
                        document_names,
                        total_pages,
                        pages_with_text,
                    ) = extract_pdfs(uploaded_files)

                st.session_state.documents = extracted_chunks
                st.session_state.document_names = document_names
                st.session_state.total_pages = total_pages
                st.session_state.pages_with_text = pages_with_text
                st.session_state.document_signature = signature

                # New document collection = new conversation.
                st.session_state.chat_history = []

            
            except Exception as error:
                error_message = str(error).lower()

                if "rate limit" in error_message or "429" in error_message:
                    st.warning(
                        "CampusAI is receiving too many requests right now. "
                        "Please wait a moment and try again."
                    )
                elif (
                    "authentication" in error_message
                    or "401" in error_message
                    or "403" in error_message
                ):
                    st.error(
                        "CampusAI could not authenticate with the AI service. "
                        "Please check the server's API configuration."
                    )
                elif "timeout" in error_message:
                    st.warning(
                        "The AI service took too long to respond. "
                        "Please try again."
                    )
                else:
                    st.error(
                        "CampusAI couldn't generate an answer this time. "
                        "Please try again in a moment."
                    )
                st.stop()

        st.success(
            f"{len(st.session_state.document_names)} PDF(s) loaded"
        )

        for name in st.session_state.document_names:
            st.caption(f"📄 {name}")

        if st.button("Clear study library"):
            st.session_state.documents = []
            st.session_state.chat_history = []
            st.session_state.document_signature = ""
            st.rerun()

    else:
        if st.session_state.documents:
            st.info("Your current study materials are loaded.")
        else:
            st.info("Upload PDFs to start studying.")

    st.divider()

    st.caption("Powered by Groq + open-weight AI")
    st.caption("PDF retrieval: TF-IDF + cosine similarity")


# --------------------------------------------------
# CHECK DOCUMENTS
# --------------------------------------------------

documents = st.session_state.documents

if not documents:
    st.markdown("## Welcome to your study workspace 👋")
    st.write(
        "Upload your college notes using the sidebar to unlock "
        "your AI study tools."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 💬 Ask questions")
        st.write("Understand difficult concepts using your notes.")

    with col2:
        st.markdown("### 📝 Summarize")
        st.write("Turn lengthy notes into easier revision material.")

    with col3:
        st.markdown("### ✅ Practice")
        st.write("Generate MCQs and exam revision questions.")

    st.info(
        "Tip: Use text-based PDFs for the best results. "
        "Scanned PDFs may require OCR."
    )
    st.stop()


# --------------------------------------------------
# DOCUMENT FILTER
# --------------------------------------------------

all_document_names = st.session_state.document_names

with st.sidebar:
    selected_documents = st.multiselect(
        "Search within these PDFs",
        options=all_document_names,
        default=all_document_names,
        help="Select the documents CampusAI should use.",
    )

if not selected_documents:
    st.warning("Select at least one PDF in the sidebar.")
    st.stop()


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

if feature == "🏠 Dashboard":
    st.subheader("Your Study Dashboard")
    st.write("Everything you need to study smarter, in one place.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("PDF Documents", len(all_document_names))

    with col2:
        st.metric("Text Chunks", len(documents))

    with col3:
        st.metric("Pages with Text", st.session_state.pages_with_text)

    st.divider()

    st.markdown("### What would you like to do today?")

    card1, card2 = st.columns(2)

    with card1:
        st.markdown("#### 💬 Ask CampusAI")
        st.write("Ask questions about your selected college notes.")
        st.caption("Use the sidebar to open Ask CampusAI.")

    with card2:
        st.markdown("#### 📝 Summarize Notes")
        st.write("Generate a quick summary of a topic.")
        st.caption("Use the sidebar to open Summarize Notes.")

    card3, card4 = st.columns(2)

    with card3:
        st.markdown("#### ✅ Generate MCQs")
        st.write("Create practice tests from your study material.")

    with card4:
        st.markdown("#### 📚 Revision Questions")
        st.write("Prepare short-answer and long-answer questions.")

    st.divider()

    st.markdown("### Your Study Library")

    for name in all_document_names:
        st.markdown(f"- 📄 {name}")

    st.caption(
        "Answers are generated from retrieved passages. "
        "Always verify important information against your original notes."
    )


# --------------------------------------------------
# ASK CAMPUSAI
# --------------------------------------------------

elif feature == "💬 Ask CampusAI":
    st.subheader("💬 Ask CampusAI")
    st.write("Ask questions and explore the answers in your notes.")

    with st.expander("Conversation history", expanded=True):
        if not st.session_state.chat_history:
            st.caption("Your questions will appear here.")

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

                if message.get("sources"):
                    st.caption("Sources: " + ", ".join(message["sources"]))

    question = st.chat_input("Ask a question about your notes...")

    if question:
        previous_messages = st.session_state.chat_history[-6:]

        with st.spinner("Searching your notes..."):
            retrieved = retrieve_chunks(
                question,
                documents,
                top_k=5,
                selected_documents=selected_documents,
            )

        if not retrieved:
            st.warning(
                "I couldn't find relevant passages. Try using a keyword "
                "from your notes or selecting another PDF."
            )

        else:
            context = make_context(retrieved)

            history_text = "\n\n".join(
                f"{item['role'].upper()}: {item['content']}"
                for item in previous_messages
            )

            system_prompt = (
                "You are CampusAI, a helpful college study assistant. "
                "Use the supplied PDF passages as the primary evidence. "
                "Do not invent facts, quotations, or page numbers. "
                "Cite supported claims using labels such as "
                "[Document: notes.pdf | PDF Page: 4]. "
                "If the passages do not answer the question, say so. "
                "If earlier conversation is provided, use it only to "
                "understand follow-up questions; factual answers must "
                "remain grounded in the retrieved passages. "
                "Explain clearly for a college student."
            )

            user_prompt = (
                f"Recent conversation:\n{history_text or 'None'}\n\n"
                f"Current question:\n{question}\n\n"
                f"Retrieved PDF passages:\n{context}"
            )

            try:
                with st.spinner("CampusAI is preparing your answer..."):
                    answer = ask_ai(system_prompt, user_prompt)

                sources = sorted({
                    f"{item['document']} — page {item['page']}"
                    for item in retrieved
                })

                st.session_state.chat_history.append(
                    {
                        "role": "user",
                        "content": question,
                    }
                )

                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    }
                )

                st.rerun()

            except Exception as error:
                st.error(f"AI request failed: {error}")

    if st.button("Clear conversation"):
        st.session_state.chat_history = []
        st.rerun()

    with st.expander("How did CampusAI find this answer?"):
        if st.session_state.chat_history:
            last_answer = next(
                (
                    item for item in reversed(st.session_state.chat_history)
                    if item["role"] == "assistant"
                ),
                None,
            )

            if last_answer:
                st.caption(
                    "The assistant uses TF-IDF similarity to retrieve passages "
                    "from your selected PDFs. The source list shows which document "
                    "pages were provided to the AI as context. These are retrieved "
                    "sources, not proof that every statement in the answer is correct. "
                    "Check the cited passages when accuracy is important."
                   
                )


# --------------------------------------------------
# SUMMARIZE NOTES
# --------------------------------------------------

elif feature == "📝 Summarize Notes":
    st.subheader("📝 Summarize Your Notes")
    st.write("Create a focused summary from the selected PDFs.")

    topic = st.text_input(
        "Topic or keyword",
        placeholder="Example: Operating systems, DBMS, thermodynamics",
    )

    if st.button("Generate Summary", type="primary"):
        if topic.strip():
            retrieved = retrieve_chunks(
                topic,
                documents,
                top_k=8,
                selected_documents=selected_documents,
            )
            context = make_context(retrieved)
        else:
            filtered = [
                item for item in documents
                if item["document"] in selected_documents
            ]

            context = make_context(filtered[:30])

        if not context.strip():
            st.warning("No matching text was found.")
        else:
            try:
                with st.spinner("Summarizing your notes..."):
                    summary = ask_ai(
                        "Summarize the supplied college notes with clear "
                        "headings, key concepts, and definitions. "
                        "Do not add unsupported facts. Include source "
                        "document and page labels for key claims.",
                        f"Create a useful student-friendly summary:\n{context}",
                    )

                st.markdown("### Your Summary")
                st.markdown(summary)

            except Exception as error:
                st.error(f"Summary failed: {error}")


# --------------------------------------------------
# GENERATE MCQS
# --------------------------------------------------

elif feature == "✅ Generate MCQs":
    st.subheader("✅ Generate Practice MCQs")

    topic = st.text_input(
        "Optional topic",
        placeholder="Example: Python loops",
        key="mcq_topic",
    )

    number = st.slider(
        "Number of questions",
        min_value=3,
        max_value=10,
        value=5,
        key="mcq_number",
    )

    if st.button("Create MCQs", type="primary"):
        if topic.strip():
            retrieved = retrieve_chunks(
                topic,
                documents,
                top_k=8,
                selected_documents=selected_documents,
            )
            context = make_context(retrieved)
        else:
            filtered = [
                item for item in documents
                if item["document"] in selected_documents
            ]
            context = make_context(filtered[:30])

        if not context.strip():
            st.warning("No matching study material was found.")
        else:
            try:
                with st.spinner("Creating your practice test..."):
                     result = ask_ai(
                        "You are an expert college exam question setter. "
                        "Create multiple-choice questions using only the supplied "
                        "study notes. Do not use unsupported outside facts. "
                        "For every question, follow this exact structure:\n"
                        "1. Question number and question text.\n"
                        "2. Difficulty: Easy, Medium, or Hard.\n"
                        "3. Four options labelled A, B, C, and D.\n"
                        "4. Exactly one correct answer.\n"
                        "5. Correct answer with its option letter.\n"
                        "6. A brief explanation grounded in the notes.\n"
                        "7. Source document and PDF page, when identifiable.\n\n"
                        "Make incorrect options plausible but clearly incorrect "
                        "according to the supplied notes. Avoid duplicate questions, "
                        "ambiguous wording, and questions with multiple correct "
                        "answers. Distribute correct options across A, B, C, and D "
                        "where practical. If the notes cannot support a question, "
                        "do not invent it. If the notes contain insufficient "
                        "information for the requested number, say so.",
                        f"Create up to {number} high-quality MCQs from these notes. "
                        "Use the optional topic as the focus if one is provided.\n\n"
                        f"Topic: {topic.strip() or 'General revision'}\n\n"
                        f"Study notes:\n{context}",
                        max_tokens=2200,
                    )

                st.markdown("### Your Practice Test")
                st.markdown(result)

            except Exception as error:
                st.error(f"MCQ generation failed: {error}")


# --------------------------------------------------
# REVISION QUESTIONS
# --------------------------------------------------

elif feature == "📚 Revision Questions":
    st.subheader("📚 Exam Revision Questions")

    topic = st.text_input(
        "Optional topic",
        placeholder="Example: Database normalization",
        key="revision_topic",
    )

    number = st.slider(
        "Number of questions",
        min_value=3,
        max_value=10,
        value=5,
        key="revision_number",
    )

    if st.button("Generate Revision Questions", type="primary"):
        if topic.strip():
            retrieved = retrieve_chunks(
                topic,
                documents,
                top_k=8,
                selected_documents=selected_documents,
            )
            context = make_context(retrieved)
        else:
            filtered = [
                item for item in documents
                if item["document"] in selected_documents
            ]
            context = make_context(filtered[:30])

        if not context.strip():
            st.warning("No matching study material was found.")
        else:
            try:
                with st.spinner("Preparing exam questions..."):
                    result = ask_ai(
                        "You are an expert college exam preparation assistant. "
                        "Generate revision questions using only the supplied "
                        "study notes. Do not invent facts or introduce unsupported "
                        "topics.\n\n"
                        "Create a balanced selection of questions appropriate "
                        "for a college student. Include short-answer questions "
                        "testing definitions and key facts, long-answer questions "
                        "testing explanations and comparisons, and conceptual "
                        "questions testing understanding and application.\n\n"
                        "For every question, provide:\n"
                        "1. Question number and question text.\n"
                        "2. Type: Short Answer, Long Answer, or Conceptual.\n"
                        "3. Difficulty: Easy, Medium, or Hard.\n"
                        "4. A concise answer outline with the main points expected "
                        "in a good exam answer.\n"
                        "5. Source document and PDF page when identifiable.\n\n"
                        "Keep answers proportionate to the question type. "
                        "Avoid duplicate questions. If the supplied notes do not "
                        "contain enough information, acknowledge the limitation "
                        "instead of making up content.",
                        f"Create up to {number} exam-focused revision questions.\n\n"
                        f"Topic: {topic.strip() or 'General revision'}\n\n"
                        f"Study notes:\n{context}",
                        max_tokens=2200,
                    )
                        

                st.markdown("### Revision Questions")
                st.markdown(result)

            except Exception as error:
                st.error(f"Question generation failed: {error}")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:#808899;">
        🎓 CampusAI · AI-powered learning from your own study materials
    </div>
    """,
    unsafe_allow_html=True,
)