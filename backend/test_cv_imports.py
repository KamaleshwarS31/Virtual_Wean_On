"""
Test script to verify backend setup including Try-On Engine dependencies
"""
import sys

print("Testing imports...")

try:
    print("10. Testing opencv-python...")
    import cv2
    print(f"    ✅ OpenCV OK (version: {cv2.__version__})")
except Exception as e:
    print(f"    ❌ OpenCV failed: {e}")

try:
    print("11. Testing mediapipe...")
    import mediapipe as mp
    print("    ✅ MediaPipe OK")
    if hasattr(mp, 'solutions'):
        print("       ✅ MediaPipe Solutions OK")
    else:
        print("       ❌ MediaPipe Solutions missing")
except Exception as e:
    print(f"    ❌ MediaPipe failed: {e}")
