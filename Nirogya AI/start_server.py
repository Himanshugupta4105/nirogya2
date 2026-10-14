"""
Nirogya AI - Launcher Script
Starts the unified FastAPI backend & interactive frontend web application.
"""

import sys
import uvicorn

if __name__ == "__main__":
    # Ensure UTF-8 output on Windows terminal
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("=" * 70)
    print("  [+] NIROGYA AI - PERSONAL HEALTH COPILOT")
    print("  AI-Powered Medical Intelligence, Plain Language Explanations,")
    print("  Unified Health Timeline & ABDM / FHIR R4 Architecture")
    print("=" * 70)
    print("  Web Application: http://localhost:8000")
    print("  Swagger API Docs: http://localhost:8000/docs")
    print("=" * 70)
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=False)
