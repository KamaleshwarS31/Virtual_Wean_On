import sys
import subprocess

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

print("📦 Installing Try-On Engine Dependencies...")
try:
    install("opencv-python")
    install("mediapipe")
    print("✅ Installation complete!")
except Exception as e:
    print(f"❌ Failed to install dependencies: {e}")
    sys.exit(1)
