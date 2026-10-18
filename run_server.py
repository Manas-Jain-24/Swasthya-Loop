import os
import sys
import webbrowser
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")
BACKEND_DIR = os.path.join(BASE_DIR, "backend")

def main():
    print("=" * 60)
    print(" 🏥 SWASTHYALOOP CLINICAL PLATFORM LAUNCHER")
    print(" AI-Assisted Chronic-Care Follow-up Prototype")
    print("=" * 60)
    
    python_exec = VENV_PYTHON if os.path.exists(VENV_PYTHON) else sys.executable
    print(f"Using Python runtime: {python_exec}")
    print("Starting FastAPI server at http://127.0.0.1:8001 ...")
    
    # Auto-open browser after 1.5 seconds
    def open_browser():
        import time
        time.sleep(1.5)
        webbrowser.open("http://127.0.0.1:8001")

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Run uvicorn
    cmd = [
        python_exec,
        "-m", "uvicorn",
        "app.main:app",
        "--host", "127.0.0.1",
        "--port", "8001",
        "--reload"
    ]
    subprocess.run(cmd, cwd=BACKEND_DIR)

if __name__ == "__main__":
    main()
