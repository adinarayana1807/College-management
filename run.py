#!/usr/bin/env python
"""
Main application startup script for Apex College AI
"""

import sys
import uvicorn
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

if __name__ == '__main__':
    print()
    print('=' * 60)
    print('🎓 Apex College AI - RAG Assistant')
    print('=' * 60)
    print('📡 Starting FastAPI server...')
    print('🌐 Open your browser to: http://127.0.0.1:8000')
    print('📚 API Docs: http://127.0.0.1:8000/docs')
    print('=' * 60)
    print()
    
    uvicorn.run(
        'app.main:app',
        host='127.0.0.1',
        port=8000,
        reload=True,
        log_level='info'
    )
