# 🎓 CampusAI — AI-Powered College Study Assistant

**Your syllabus. Your AI. Your success.**

CampusAI is an AI-powered study assistant that helps college students understand their study materials, summarize notes, and prepare for examinations using their own PDF documents.

Built with Python, Streamlit, Groq, and open-weight AI models, CampusAI combines language-model responses with lightweight document retrieval to make studying more interactive.

## ✨ Features

- **Ask questions:** Ask questions about uploaded college notes.
- **Multiple PDF support:** Upload and search across multiple PDF documents.
- **Source references:** Display document names and PDF page numbers for retrieved passages.
- **Smart summaries:** Generate summaries of notes and selected topics.
- **MCQ generation:** Create multiple-choice practice questions with answers and explanations.
- **Revision preparation:** Generate short-answer and long-answer exam questions.
- **Document filtering:** Choose which PDFs CampusAI should search.
- **Follow-up questions:** Continue a conversation about your study materials.
- **Modern dashboard:** View your uploaded documents and study-library statistics.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | Web interface |
| Groq API | Access to the language model |
| OpenAI GPT-OSS 20B | AI model used by the application |
| PyPDF | Extract text from PDF documents |
| scikit-learn | TF-IDF retrieval and cosine similarity |
| python-dotenv | Load environment variables securely |

## ⚙️ How It Works

1. A student uploads one or more PDF files.
2. CampusAI extracts selectable text from each PDF page.
3. The extracted text is split into overlapping chunks.
4. TF-IDF and cosine similarity identify passages relevant to a question or topic.
5. The selected passages and their source labels are sent to the language model.
6. CampusAI displays the generated response and retrieved source references.

### Architecture

```text
Student
   |
   v
Streamlit Web Interface
   |
   v
PDF Upload and Text Extraction
   |
   v
Text Chunking with Page Metadata
   |
   v
TF-IDF Retrieval and Cosine Similarity
   |
   v
Relevant Passages + Source Labels
   |
   v
Groq API — GPT-OSS 20B
   |
   v
Answers, Summaries, MCQs and Revision Questions
```

## 🚀 Installation

### Prerequisites

- Python 3.10 or newer
- pip
- A Groq API key
- An internet connection for AI requests

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd CampusAI
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual GitHub repository URL.

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install streamlit pypdf groq python-dotenv scikit-learn
```

### 4. Configure the API key

Create a file named `.env` in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Replace the placeholder with your own API key.

**Security:** Never commit your `.env` file or publish your API key.

### 5. Run CampusAI

```powershell
python -m streamlit run app.py
```

Open the local address displayed in your terminal.

## 📖 How to Use

1. Launch CampusAI.
2. Upload your college notes as PDF files.
3. Select the PDFs you want to search.
4. Open **Ask CampusAI** to ask questions.
5. Use **Summarize Notes** to review a topic.
6. Use **Generate MCQs** to practise.
7. Use **Revision Questions** to prepare for exams.

## ⚠️ Current Limitations

- Scanned PDFs may require OCR before their text can be extracted.
- Retrieval uses TF-IDF rather than a semantic embedding model.
- Answers may be incomplete or incorrect and should be checked against the original notes.
- Chat history is session-based and is not permanently stored.
- AI features require an internet connection and a valid API key.
- API access and usage may be subject to provider limits and charges.

## 🔒 Security

- Store API credentials in environment variables.
- Do not commit `.env` files.
- Do not expose private API keys in screenshots, logs, or public repositories.
- Configure secrets securely when deploying the application.

## 🗺️ Future Improvements

- Semantic search using open-source embedding models.
- Persistent chat history and user accounts.
- OCR support for scanned notes.
- Downloadable study summaries and practice tests.
- Interactive MCQ quizzes with scoring.
- Subject-wise study collections.
- Deployment with secure server-side secrets.

## 🎯 Project Goal

CampusAI aims to make AI-assisted learning more accessible by helping students work directly with their existing study materials.

The project explores how open-weight language models and lightweight retrieval techniques can support everyday college learning.

## 📄 License

A license has not yet been selected. Choose an open-source license before publishing the project as an open-source contribution.

## 🙌 Acknowledgements

Built using Python, Streamlit, scikit-learn, PyPDF, and the Groq API.