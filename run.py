import os
import sys
from pathlib import Path

# Add backend directory to Python path
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import uvicorn
from app.config import settings
from app.database import init_db, SessionLocal
from app.models import DocumentModel
from app.services.vector_store import vector_store
from app.services.document_processor import DocumentProcessor

def auto_seed_if_empty():
    """Seeds sample documents if database and vector store are empty on initial run."""
    db = SessionLocal()
    try:
        count = db.query(DocumentModel).count()
        if count == 0:
            print("📦 Initial launch detected: Pre-loading sample college knowledge base...")
            sample_dir = ROOT_DIR / "sample_data"
            if sample_dir.exists():
                dept_map = {
                    "admissions": "Admissions",
                    "fee": "Fees & Scholarships",
                    "scholarship": "Fees & Scholarships",
                    "hostel": "Hostel & Mess",
                    "placement": "Placements & Careers",
                    "examination": "Exam Cell",
                    "exam": "Exam Cell",
                    "cs": "Computer Science",
                    "computer_science": "Computer Science",
                    "library": "Central Library",
                    "clubs": "Student Clubs & Sports",
                    "sports": "Student Clubs & Sports"
                }
                sample_files = list(sample_dir.glob("*.txt"))
                for f in sample_files:
                    stem = f.stem.lower()
                    dept = "General"
                    for key, d in dept_map.items():
                        if key in stem:
                            dept = d
                            break
                    title = f.stem.replace("_", " ").title()
                    doc_id = f"sample_{f.stem[:15]}"
                    dest_path = settings.UPLOAD_DIR / f"{doc_id}_{f.name}"
                    
                    with open(f, "rb") as src, open(dest_path, "wb") as dst:
                        dst.write(src.read())
                    
                    pages = DocumentProcessor.extract_text(dest_path)
                    chunks = DocumentProcessor.chunk_document(
                        pages=pages,
                        doc_id=doc_id,
                        title=title,
                        department=dept,
                        chunk_size=settings.CHUNK_SIZE,
                        chunk_overlap=settings.CHUNK_OVERLAP
                    )
                    chunk_count = vector_store.add_chunks(chunks)

                    doc_record = DocumentModel(
                        doc_id=doc_id,
                        title=title,
                        filename=f.name,
                        file_path=str(dest_path),
                        file_type="txt",
                        department=dept,
                        file_size_bytes=os.path.getsize(dest_path),
                        chunk_count=chunk_count,
                        status="indexed",
                        version="1.0"
                    )
                    db.add(doc_record)
                db.commit()
                print(f"✅ Successfully indexed {len(sample_files)} sample college documents ({vector_store.count()} chunks)!")
    except Exception as e:
        print(f"⚠️ Auto-seed note: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 65)
    print("🎓 APEX COLLEGE AI ASSISTANT — RAG KNOWLEDGE SYSTEM")
    print("=" * 65)
    print(f"📁 Root Directory: {ROOT_DIR}")
    print(f"🧠 Vector Store: ChromaDB ({settings.CHROMA_PERSIST_DIR})")
    print(f"🗄️ Database: SQLite ({settings.SQLITE_DB_PATH})")
    
    # Initialize DB schema
    init_db()
    
    # Auto-seed sample knowledge
    auto_seed_if_empty()
    
    print("\n🚀 Starting Web Application...")
    print("👉 Student Chat & Admin Portal: http://127.0.0.1:8000")
    print("👉 Interactive API Documentation: http://127.0.0.1:8000/docs")
    print("👉 Default Admin Account: admin@college.edu | Password: Admin@123")
    print("=" * 65 + "\n")
    
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False, app_dir=str(BACKEND_DIR))
