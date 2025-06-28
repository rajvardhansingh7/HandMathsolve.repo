#!/usr/bin/env python3
"""
Launcher script for Hand Gesture Math Solver
Allows users to choose between standalone and web versions
"""

import sys
import subprocess
import os

def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("🤚 HAND GESTURE MATH SOLVER")
    print("=" * 60)
    print("Choose your preferred version:")
    print()

def check_dependencies():
    """Check if dependencies are installed"""
    try:
        import cv2
        import mediapipe
        import numpy
        return True
    except ImportError:
        print("❌ Missing dependencies. Please run:")
        print("   pip install -r requirements.txt")
        return False

def run_standalone():
    """Run the standalone OpenCV version"""
    print("🚀 Starting standalone version...")
    try:
        subprocess.run([sys.executable, "mathSolver.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Error running standalone version")
    except KeyboardInterrupt:
        print("\n👋 Standalone version closed")

def run_web():
    """Run the Streamlit web version"""
    print("🌐 Starting web version...")
    print("📱 Opening browser at http://localhost:8501")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Error running web version")
    except KeyboardInterrupt:
        print("\n👋 Web version closed")

def run_test():
    """Run the test script"""
    print("🧪 Running installation test...")
    try:
        subprocess.run([sys.executable, "test_installation.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Error running test")
    except KeyboardInterrupt:
        print("\n👋 Test interrupted")

def main():
    """Main launcher function"""
    print_banner()
    
    if not check_dependencies():
        return
    
    while True:
        print("1. 🖥️  Standalone OpenCV App (Recommended)")
        print("2. 🌐 Streamlit Web App")
        print("3. 🧪 Test Installation")
        print("4. 📖 View README")
        print("5. 🚪 Exit")
        print()
        
        try:
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == "1":
                run_standalone()
            elif choice == "2":
                run_web()
            elif choice == "3":
                run_test()
            elif choice == "4":
                if os.path.exists("README.md"):
                    with open("README.md", "r") as f:
                        print(f.read())
                else:
                    print("❌ README.md not found")
            elif choice == "5":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    main() 