# 🎓 Apex College AI — RAG-Based Campus Knowledge Assistant

An AI-powered college information assistant and administration system built using **Retrieval-Augmented Generation (RAG)**. The platform enables students to ask department-filtered questions and receive grounded answers with citations, while offering administrators a dashboard for document lifecycle management, vector indexing, and query analytics.

---

## 🌟 Key Features

### 💬 Student Chat & RAG Experience
- **Interactive Chat Interface**: Student query assistant with real-time response rendering and conversation history.
- **Department-Wise Knowledge Scoping**: Filter answers by specific departments (*Admissions, Fees & Scholarships, Computer Science, Hostel & Mess, Placements & Careers, Exam Cell, Central Library, Student Clubs*).
- **Interactive Citations & Source Verification**: Every grounded answer displays clickable citation cards with exact document title, department, page/chunk index, similarity score, and excerpt snippet.
- **Strict Anti-Hallucination & Fallback**: Clear fallback responses when queries are out-of-scope or similarity scores are low.
- **Multi-Turn Context**: Conversational memory across chat sessions.

### 🛡️ Admin Portal & Document Management
- **Multi-Format Document Ingestion**: Upload `.pdf`, `.docx`, `.txt`, and `.md` files.
- **Document Chunking & Processing**: Sliding window recursive chunking with configurable overlap.
- **Vector Database (ChromaDB)**: Persistent semantic vector store with metadata filtering and cosine similarity.
- **Document Lifecycle Management**: Upload, inspect chunk counts, re-index embeddings, and delete documents.
- **Real-Time Analytics**: Live metrics for total documents, vector chunks, student queries, average search latency, and department distribution charts.
- **Pre-Seeded Sample Knowledge Base**: 8 built-in realistic college documents covering all departments with 1-click seeding.

---

## 🔄 RAG Pipeline Architecture

```
College Documents (PDF / DOCX / TXT)
        │
        ▼
Text Extraction (pypdf, python-docx)
        │
        ▼
Recursive Semantic Chunker (Chunk Size: 600, Overlap: 120)
        │
        ▼
Embedding Generation (Gemini / OpenAI / Local Transformers)
        │
        ▼
Vector Database (ChromaDB with Metadata Filtering)
        │
┌───────┴────────────────────────────────────────┐
│                                                │
│ Student Question                               │
│       │                                        │
│       ▼                                        │
│ Query Embedding ──► Semantic Vector Search    │
│                            │                   │
│                            ▼                   │
│                    Top-K Context Chunks        │
│                            │                   │
│                            ▼                   │
│                    Grounded System Prompt      │
│                            │                   │
│                            ▼                   │
│                    LLM Generator (Gemini/GPT)  │
│                            │                   │
└────────────────────────────┼───────────────────┘
                             │
                             ▼
               Final Answer + Document Citations
```

---

## 🛠️ Prerequisites

- **Python**: Version 3.10, 3.11, or 3.12 installed.
- **OS**: Windows 10/11, macOS, or Linux.
- **Browser**: Chrome, Edge, Firefox, or Safari.

---

## 🚀 Quick Start Guide (Run Locally)

### Step 1: Clone or Navigate to the Project Directory
Open your terminal (PowerShell, Command Prompt, or Bash) in the project directory:
```bash
cd "RAG MANAGEMENT"
```

---

### Step 2: Set Up Python Virtual Environment

#### On Windows (PowerShell):
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

#### On macOS / Linux:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

---

### Step 3: Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

---

### Step 4: Configure Environment Variables (Optional)

The application includes `.env` file ready to run.

#### To use MongoDB (Atlas or Local):
Open `.env` and set your MongoDB connection string and database name:
```env
# For MongoDB Atlas:
MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=college_rag_db

# Or for local MongoDB:
# MONGODB_URI=mongodb://localhost:27017
# MONGODB_DB_NAME=college_rag_db
```

#### To use Google Gemini (Recommended - Free Tier available):
1. Get a free API key from [Google AI Studio](https://aistudio.google.com/).
2. Open `.env` in any text editor and set:
   ```env
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

#### To use OpenAI:
1. Open `.env` and set:
   ```env
   LLM_PROVIDER=openai
   OPENAI_API_KEY=your_openai_api_key_here
   ```

#### To use 100% Free Offline / Local Mode (No API key needed):
If no API key is set, the application automatically uses its built-in local vector embedding and semantic synthesis engine!

---

### Step 5: Start the Application

#### Option A: One-Click Runner (Windows / macOS / Linux)
```bash
python run.py
```

#### Option B: Windows Batch File
Double-click `start.bat` or run:
```cmd
start.bat
```

When started, the application automatically:
1. Initializes the SQLite database.
2. Creates the default admin account.
3. Automatically pre-loads the sample college knowledge base (8 documents, 70+ chunks).
4. Launches the FastAPI web server on port **8000**.

---

### Step 6: Open the Web Application

Open your browser and navigate to:
- 🌐 **Web Application (Chat & Admin)**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- 📚 **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 📑 **ReDoc API Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🔑 Default Credentials

| Role | Email | Password |
|---|---|---|
| **Administrator** | `admin@college.edu` | `Admin@123` |
| **Student** | `student@apex.edu` | `Student@123` |
| **Guest Mode** | *(No login required to ask questions)* | — |

> 💡 **Tip**: In the login modal, click the **"Admin Demo"** or **"Student Demo"** buttons to auto-fill the credentials in 1 click!

---

## 🧪 Sample Questions to Test

Try asking the chatbot these department-specific questions:

1. **Admissions**: *"What are the eligibility criteria and accepted entrance exams for B.Tech CSE?"*
2. **Fees & Scholarships**: *"What is the annual tuition fee for B.Tech and what merit scholarships are available?"*
3. **Hostel & Living**: *"What are the curfew timings for hostellers and what meals are served in the mess?"*
4. **Placements**: *"What was the highest international package and average package for Computer Science?"*
5. **Exam Cell**: *"What is the minimum attendance requirement for semester exams and how does re-evaluation work?"*
6. **Computer Science**: *"What specialized research labs are available in the CSE department?"*
7. **Library**: *"How many books can a B.Tech student borrow and what are the library operating hours?"*
8. **Clubs & Events**: *"What technical clubs exist and when is the annual cultural fest 'AURA' held?"*
9. **Out-of-Scope Test**: *"How do I bake a chocolate cake?"* → *(Chatbot gracefully indicates information is unavailable in college documents)*.

---

## 🔬 Running Automated Tests

To run the end-to-end integration test suite (verifying document extraction, chunking, vector indexing, similarity search, and RAG generation):

```bash
python test_rag.py
```

Expected output:
```
============================================================
🧪 RUNNING RAG SYSTEM INTEGRATION TESTS
============================================================
[Step 1/5] Initializing Database & Admin Seed...
✅ Database initialized successfully.

[Step 2/5] Ingesting Sample College Documents...
✅ Ingested admission chunks + hostel chunks.
   Total vectors in ChromaDB: 28

[Step 3/5] Testing Semantic Vector Search & Department Filtering...
   Top Match: 'Hostel & Living Handbook' (Score: 0.89)
✅ Vector search & department metadata filtering passed.

[Step 4/5] Testing End-to-End RAG Pipeline with Citations...
   Latency: 35.2 ms
   Sources Count: 2
✅ RAG Pipeline answered with grounded citations.

[Step 5/5] Testing Out-of-Scope / Unknown Query Handling...
✅ Out-of-scope question handled safely.

============================================================
🎉 ALL 5 INTEGRATION TESTS PASSED SUCCESSFULLY!
============================================================
```

---

## 📁 Project Structure

```
RAG MANAGEMENT/
├── backend/
│   ├── app/
│   │   ├── config.py                 # App settings, environment vars, chunking parameters
│   │   ├── database.py               # SQLite engine, session manager, seed initial admin
│   │   ├── models.py                 # SQLAlchemy DB models & Pydantic request/response schemas
│   │   ├── main.py                   # FastAPI application, static mounts & CORS
│   │   ├── routers/
│   │   │   ├── auth.py               # JWT authentication, register & login endpoints
│   │   │   ├── chat.py               # RAG chat endpoint, session management & history
│   │   │   ├── documents.py          # Document upload, listing, re-indexing, deletion
│   │   │   └── admin.py              # Admin stats, analytics, sample data seeding
│   │   └── services/
│   │       ├── auth_service.py       # Password hashing, JWT token creation & role guards
│   │       ├── document_processor.py # PDF/DOCX/TXT extraction & recursive sliding-window chunker
│   │       ├── vector_store.py       # ChromaDB persistent store & multi-provider embeddings
│   │       └── rag_engine.py         # RAG pipeline, context builder, citations & LLM invocation
│   ├── sample_data/                  # 8 comprehensive college documents covering all departments
│   │   ├── Admissions_and_Eligibility_2026.txt
│   │   ├── Fee_Structure_and_Scholarships.txt
│   │   ├── Hostel_and_Campus_Regulations.txt
│   │   ├── Placement_and_Career_Guide.txt
│   │   ├── Examination_and_Grading_System.txt
│   │   ├── Computer_Science_Department.txt
│   │   ├── Central_Library_and_Resources.txt
│   │   └── Clubs_Sports_and_Events.txt
│   └── requirements.txt              # Python package dependencies
├── frontend/
│   ├── index.html                    # Single Page App layout with chat & admin views
│   ├── css/
│   │   └── style.css                 # Modern CSS design system, dark/light theme, animations
│   └── js/
│       ├── api.js                    # REST API client wrapper & toast notifications
│       ├── auth.js                   # Authentication state & login modal controller
│       ├── chat.js                   # Chat UI, streaming messages, citations modal & department filter
│       └── admin.js                  # Admin dashboard, metrics cards, document table & upload zone
├── .env.example                      # Configuration template
├── .env                              # Active environment configuration
├── run.py                            # Main application startup script with auto-seeding
├── start.bat                         # Windows 1-click startup script
├── test_rag.py                       # Automated RAG integration test suite
├── spec.md                           # Specification sheet (Single Source of Truth)
└── README.md                         # Complete project documentation
```

---

## 📡 Core API Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/chat/ask` | Ask question, retrieve context, generate grounded answer & citations | Optional |
| `GET` | `/api/chat/sessions` | List user conversation sessions | Optional |
| `GET` | `/api/chat/sessions/{id}/messages` | Get full message history for a conversation | Optional |
| `DELETE` | `/api/chat/sessions/{id}` | Delete a conversation session | Optional |
| `GET` | `/api/documents` | List indexed documents (with department & search filters) | No |
| `GET` | `/api/documents/departments` | List distinct departments | No |
| `POST` | `/api/documents/upload` | Upload & index PDF/DOCX/TXT document into ChromaDB | **Admin** |
| `DELETE` | `/api/documents/{id}` | Delete document & remove from ChromaDB | **Admin** |
| `POST` | `/api/documents/{id}/reindex` | Re-index document chunks | **Admin** |
| `GET` | `/api/admin/stats` | Retrieve metrics (doc count, chunks, queries, latency) | **Admin** |
| `POST` | `/api/admin/seed-sample-data` | Seed built-in sample college documents | **Admin** |
| `POST` | `/api/auth/login` | Authenticate user & get JWT token | No |
| `POST` | `/api/auth/register` | Register new student or admin account | No |
"# college-rag-assistant" 
"# college-rag-assistant" 
"# college-rag-assistant" 
