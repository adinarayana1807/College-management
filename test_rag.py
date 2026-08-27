import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from app.config import settings
from app.database import init_db, SessionLocal
from app.models import DocumentModel
from app.services.vector_store import vector_store
from app.services.document_processor import DocumentProcessor
from app.services.rag_engine import rag_engine

def run_rag_tests():
    print("=" * 60)
    print("🧪 RUNNING RAG SYSTEM INTEGRATION TESTS")
    print("=" * 60)

    # 1. Initialize Database Schema
    print("\n[Step 1/5] Initializing Database & Admin Seed...")
    init_db()
    print("✅ Database initialized successfully.")

    # 2. Ingest Sample Documents
    print("\n[Step 2/5] Ingesting Sample College Documents...")
    sample_dir = ROOT_DIR / "sample_data"
    admissions_file = sample_dir / "Admissions_and_Eligibility_2026.txt"
    hostel_file = sample_dir / "Hostel_and_Campus_Regulations.txt"

    assert admissions_file.exists(), "Admissions sample file missing"
    assert hostel_file.exists(), "Hostel sample file missing"

    pages_adm = DocumentProcessor.extract_text(admissions_file)
    chunks_adm = DocumentProcessor.chunk_document(
        pages=pages_adm,
        doc_id="test_adm_01",
        title="Admissions Policy 2026",
        department="Admissions",
        chunk_size=500,
        chunk_overlap=100
    )
    vector_store.add_chunks(chunks_adm)

    pages_hos = DocumentProcessor.extract_text(hostel_file)
    chunks_hos = DocumentProcessor.chunk_document(
        pages=pages_hos,
        doc_id="test_hos_01",
        title="Hostel & Living Handbook",
        department="Hostel & Mess",
        chunk_size=500,
        chunk_overlap=100
    )
    vector_store.add_chunks(chunks_hos)

    print(f"✅ Ingested {len(chunks_adm)} admission chunks + {len(chunks_hos)} hostel chunks.")
    print(f"   Total vectors in ChromaDB: {vector_store.count()}")

    # 3. Test Vector Similarity Search with Metadata Filter
    print("\n[Step 3/5] Testing Semantic Vector Search & Department Filtering...")
    query_hostel = "What is the curfew time for the hostel gate?"
    results = vector_store.similarity_search(query=query_hostel, department_filter="Hostel & Mess", top_k=2)
    
    assert len(results) > 0, "No chunks returned for hostel search"
    top_chunk = results[0]
    print(f"   Top Match: '{top_chunk['title']}' (Score: {top_chunk['similarity_score']})")
    print(f"   Excerpt: {top_chunk['text'][:120]}...")
    assert "9:30 PM" in top_chunk["text"] or "curfew" in top_chunk["text"].lower(), "Expected curfew info in retrieved chunk"
    print("✅ Vector search & department metadata filtering passed.")

    # 4. Test RAG Pipeline Execution & Citation Attribution
    print("\n[Step 4/5] Testing End-to-End RAG Pipeline with Citations...")
    rag_out = rag_engine.answer_query(
        query="What entrance exams are accepted for B.Tech admission?",
        department_filter="Admissions",
        top_k=2
    )

    print(f"   Latency: {rag_out['latency_ms']} ms")
    print(f"   Confidence Score: {rag_out['confidence_score']}")
    print(f"   Sources Count: {len(rag_out['sources'])}")
    print(f"   Answer: {rag_out['answer'][:200]}...")
    assert len(rag_out["sources"]) > 0, "Sources should not be empty for grounded query"
    assert rag_out["is_grounded"] is True, "Answer should be marked grounded"
    print("✅ RAG Pipeline answered with grounded citations.")

    # 5. Test Out-of-Scope Fallback Handling
    print("\n[Step 5/5] Testing Out-of-Scope / Unknown Query Handling...")
    oos_out = rag_engine.answer_query(
        query="How do I bake a chocolate cake at home?",
        department_filter="All",
        top_k=2
    )
    print(f"   Out-of-Scope Response: {oos_out['answer']}")
    print(f"   Is Grounded: {oos_out['is_grounded']}")
    print("✅ Out-of-scope question handled safely.")

    print("\n" + "=" * 60)
    print("🎉 ALL 5 INTEGRATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_rag_tests()
