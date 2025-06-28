#!/usr/bin/env python3
"""
Test script to verify installation and dependencies for Hand Gesture Math Solver
"""

import sys
import importlib

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name or module_name} - OK")
        return True
    except ImportError as e:
        print(f"❌ {package_name or module_name} - FAILED: {e}")
        return False

def test_opencv():
    """Test OpenCV functionality"""
    try:
        import cv2
        print(f"✅ OpenCV version: {cv2.__version__}")
        
        # Test camera access
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Camera access - OK")
            cap.release()
        else:
            print("⚠️  Camera access - No camera detected")
        
        return True
    except Exception as e:
        print(f"❌ OpenCV test failed: {e}")
        return False

def test_mediapipe():
    """Test MediaPipe functionality"""
    try:
        import mediapipe as mp
        print(f"✅ MediaPipe version: {mp.__version__}")
        
        # Test hand detection initialization
        hands = mp.solutions.hands.Hands()
        print("✅ MediaPipe Hands - OK")
        return True
    except Exception as e:
        print(f"❌ MediaPipe test failed: {e}")
        return False

def test_tts():
    """Test text-to-speech functionality"""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        print("✅ Text-to-speech - OK")
        return True
    except Exception as e:
        print(f"⚠️  Text-to-speech - Not available: {e}")
        return False

def test_streamlit():
    """Test Streamlit functionality"""
    try:
        import streamlit
        print(f"✅ Streamlit version: {streamlit.__version__}")
        return True
    except Exception as e:
        print(f"❌ Streamlit test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Hand Gesture Math Solver Installation")
    print("=" * 50)
    
    # Test Python version
    print(f"🐍 Python version: {sys.version}")
    if sys.version_info >= (3, 7):
        print("✅ Python version - OK")
    else:
        print("❌ Python version - Requires Python 3.7 or higher")
        return False
    
    print("\n📦 Testing Dependencies:")
    print("-" * 30)
    
    # Test core dependencies
    dependencies = [
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("mediapipe", "MediaPipe"),
        ("pyttsx3", "pyttsx3"),
        ("streamlit", "Streamlit"),
        ("av", "PyAV"),
    ]
    
    all_passed = True
    for module, name in dependencies:
        if not test_import(module, name):
            all_passed = False
    
    print("\n🔧 Testing Functionality:")
    print("-" * 30)
    
    # Test specific functionality
    if test_opencv():
        test_mediapipe()
        test_tts()
        test_streamlit()
    else:
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Your system is ready to run the Hand Gesture Math Solver.")
        print("\n🚀 You can now run:")
        print("   • Standalone app: python mathSolver.py")
        print("   • Web app: streamlit run app.py")
    else:
        print("❌ Some tests failed. Please install missing dependencies:")
        print("   pip install -r requirements.txt")
    
    print("=" * 50)
    return all_passed

if __name__ == "__main__":
    main() 