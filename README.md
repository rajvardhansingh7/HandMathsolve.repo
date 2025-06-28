# HandMathsolve.repo

# ✋🧠 Gesture-Based Math Solver using OpenCV and MediaPipe

A real-time hand gesture-based calculator that lets users input and evaluate mathematical expressions using only hand gestures. Designed for accessibility, computer vision practice, and enhanced with modern features.

---

## 👋 About Me

Hi, I'm Rajvardhan Singh—a passionate developer combining AI, computer vision, and user-first design to create intuitive, hands-free applications.

---

## 🚀 Features

- ✅ Real-time webcam gesture detection (no special hardware)
- 🎙️ **Voice output**: program announces result aloud using `pyttsx3`
- 🌐 **Streamlit web interface**: browser-based app with live video and gesture recognition
- Supports multi-digit input (e.g., 2 → 4 → 7 becomes "247")
- Gesture-controlled arithmetic operations (`+`, `-`, `*`, `/`)
- Built-in evaluation and on-screen result display
- Hands-free **Clear**, **DELETE**, and **Exit** commands

---

## 🧠 Tech Stack

| Tool            | Purpose                                     |
|----------------|----------------------------------------------|
| Python         | Core programming language                   |
| OpenCV         | Video capture & frame rendering             |
| MediaPipe      | Hand landmark detection (21 landmark points)|
| NumPy          | Distance computation & math logic             |
| pyttsx3        | Offline text-to-speech (voice output)       |
| Streamlit      | Lightweight web UI with live video          |
| streamlit-webrtc| Browser webcam streaming                     |

---

## ✋ Supported Gestures

| Gesture                             | Function        |
|-------------------------------------|-----------------|
| 1–5 fingers (one hand)              | Digits 1–5      |
| 5 + 1-4 fingers (two hands)         | Digits 6–9      |
| One hand, no fingers               | Digit 0         |
| 1 finger each hand                  | `+` (add)       |
| 1 + 2 fingers                      | `-` (subtract)  |
| 1 + 3 fingers                      | `*` (multiply)  |
| 1 + 4 fingers                      | `/` (divide)    |
| Both hands, 0 fingers              | `=` (evaluate)  |
| Both hands, 5 fingers              | `Clear` input   |
| Both hands, 2 fingers              | `Delete` input  |
| Right index < left index (spatial) | Exit program    |

> Gestures are detected using landmark positions and finger-count logic.

---

## 🛠️ Setup & Usage

### 1. Clone the repo and install dependencies
```bash
git clone <your-repo-url>
cd mathSolver
pip install -r requirements.txt
