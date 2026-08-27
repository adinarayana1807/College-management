import requests
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000"

def test_all_endpoints():
    print("=" * 60)
    print("🌐 HTTP INTEGRATION TEST SUITE")
    print("=" * 60)

    # 1. Test Static Files & Index
    print("\n[1/6] Testing Frontend Web App & Static Files...")
    r_index = requests.get(f"{BASE_URL}/")
    assert r_index.status_code == 200, f"Index failed: {r_index.status_code}"
    assert "<title>Apex College AI" in r_index.text, "Index HTML missing title"

    r_css = requests.get(f"{BASE_URL}/css/style.css")
    assert r_css.status_code == 200, f"CSS failed: {r_css.status_code}"

    r_js = requests.get(f"{BASE_URL}/js/chat.js")
    assert r_js.status_code == 200, f"JS failed: {r_js.status_code}"
    print("✅ Frontend HTML, CSS, and JS static assets loaded properly.")

    # 2. Health Endpoint
    print("\n[2/6] Testing Health API...")
    r_health = requests.get(f"{BASE_URL}/api/health")
    assert r_health.status_code == 200
    print(f"✅ Health Status: {r_health.json()}")

    # 3. Auth Login Endpoint
    print("\n[3/6] Testing Admin Authentication...")
    r_login = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@college.edu",
        "password": "Admin@123"
    })
    assert r_login.status_code == 200, f"Login failed: {r_login.text}"
    token_data = r_login.json()
    token = token_data["access_token"]
    print(f"✅ Login successful for {token_data['user']['email']} (Role: {token_data['user']['role']})")

    headers = {"Authorization": f"Bearer {token}"}

    # 4. Document Listing API
    print("\n[4/6] Testing Document List & Departments API...")
    r_docs = requests.get(f"{BASE_URL}/api/documents")
    assert r_docs.status_code == 200
    docs = r_docs.json()
    print(f"✅ Total indexed documents in library: {len(docs)}")
    for d in docs[:3]:
        print(f"   - {d['title']} ({d['department']}) - {d['chunk_count']} chunks")

    # 5. RAG Chat Endpoint (Admissions query)
    print("\n[5/6] Testing RAG Chat Pipeline API...")
    r_chat = requests.post(f"{BASE_URL}/api/chat/ask", json={
        "query": "What are the B.Tech programs offered and eligibility criteria?",
        "department_filter": "Admissions",
        "top_k": 3
    })
    assert r_chat.status_code == 200, f"Chat failed: {r_chat.text}"
    chat_data = r_chat.json()
    print(f"✅ RAG Chat Response Received ({chat_data['latency_ms']} ms):")
    print(f"   Is Grounded: {chat_data['is_grounded']}")
    print(f"   Citations Count: {len(chat_data['sources'])}")
    if chat_data['sources']:
        print(f"   Top Citation: {chat_data['sources'][0]['title']} ({chat_data['sources'][0]['department']})")

    # 6. Admin Analytics API
    print("\n[6/6] Testing Admin Dashboard Analytics API...")
    r_stats = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
    assert r_stats.status_code == 200
    stats = r_stats.json()
    print(f"✅ Admin Stats:")
    print(f"   - Total Documents: {stats['total_documents']}")
    print(f"   - Total Vector Chunks: {stats['total_chunks']}")
    print(f"   - Total Queries: {stats['total_queries']}")
    print(f"   - Active Departments: {', '.join(stats['active_departments'])}")
    print(f"   - Vector DB Status: {stats['vector_store_status']}")

    print("\n" + "=" * 60)
    print("🎉 ALL HTTP API & FRONTEND ENDPOINTS VERIFIED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    test_all_endpoints()
