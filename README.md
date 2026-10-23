# 🎓 CampusAI — AI-Powered College Study Assistant

**Your syllabus. Your AI. Your success.**

CampusAI is an AI-powered study assistant that helps college students learn from their own PDF notes. Students can ask questions about their study materials, generate summaries, create multiple-choice questions, and prepare revision questions.

## 🚀 Live Demo

**Try CampusAI:** https://aman26032005-campusai-app-bz1jtt.streamlit.app/

**Source Code:** https://github.com/aman26032005/CampusAI

## ✨ Features

- **Ask CampusAI:** Ask questions about uploaded study materials.
- **Multiple PDF Support:** Upload and search across multiple documents.
- **Source References:** View document names and relevant PDF page numbers.
- **Note Summaries:** Generate summaries to help review study topics.
- **MCQ Generation:** Create multiple-choice questions with answers.
- **Revision Questions:** Generate practice questions for exam preparation.
- **Document Filtering:** Select which uploaded PDFs to search.
- **Follow-up Questions:** Continue discussing your study materials.
- **Web Dashboard:** Access study tools through a Streamlit interface.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | Web interface |
| Groq API | Language-model access |
| GPT-OSS 20B | AI model used by the application |
| PyPDF | PDF text extraction |
| scikit-learn | TF-IDF retrieval and cosine similarity |
| python-dotenv | Local environment configuration |

## 🧠 How It Works

1. A student uploads one or more PDF documents.
2. CampusAI extracts text from the documents.
3. The extracted text is divided into smaller chunks with page metadata.
4. TF-IDF and cosine similarity identify relevant passages.
5. Relevant passages are provided to the AI model as context.
6. CampusAI generates answers and displays source references.

### Architecture

```text
Student
   |
   v
Streamlit Interface
   |
   v
PDF Upload and Text Extraction
   |
   v
Text Chunking and Page Metadata
   |
   v
TF-IDF Retrieval
   |
   v
Relevant Passages
   |
   v
Groq API — GPT-OSS 20B
   |
   v
Answers, Summaries, MCQs and Revision Questions
```

## 💻 Run Locally

### Prerequisites

- Python installed
- Git
- A Groq API key
- An internet connection for AI requests

### 1. Clone the repository

```bash
git clone https://github.com/aman26032005/CampusAI.git
cd CampusAI
```

### 2. Create a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure your API key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Replace the placeholder with your own API key.

**Never commit your `.env` file or expose your API key publicly.**

### 5. Start CampusAI

```powershell
python -m streamlit run app.py
```

Open the local address displayed in the terminal.

## 📖 How to Use

1. Open CampusAI.
2. Upload your college notes as PDF files.
3. Select the documents you want to use.
4. Ask questions about the material.
5. Generate summaries to review key topics.
6. Create MCQs for practice.
7. Generate revision questions before examinations.

## ⚠️ Current Limitations

- Scanned PDFs may require OCR to extract their text.
- Retrieval uses TF-IDF rather than semantic embeddings.
- AI answers can be incomplete or incorrect.
- Source references identify retrieved passages but do not guarantee every claim is correct.
- Chat history is session-based and is not permanently stored.
- AI features require a valid API key and internet access.

## 🔐 Security

- Store API keys in environment variables or your deployment platform's secrets manager.
- Never publish `.env` files or API credentials.
- Keep secrets out of source code, screenshots, logs, and Git commits.
- Configure `GROQ_API_KEY` in Streamlit Community Cloud's Secrets settings when deploying.

## 🗺️ Future Improvements

- Semantic search with open-source embedding models.
- OCR support for scanned study materials.
- Interactive quizzes with scoring.
- Downloadable summaries and practice tests.
- Persistent study sessions.
- Improved retrieval evaluation and answer verification.

## 🎯 Project Goal

CampusAI explores how open-weight language models and document retrieval can make AI-assisted studying more accessible and useful for college students.

## 📄 License

No open-source license has been selected yet. Choose a license before presenting the project as officially licensed open-source software.

## 🙌 Acknowledgements

Built with Python, Streamlit, Groq, PyPDF, and scikit-learn.