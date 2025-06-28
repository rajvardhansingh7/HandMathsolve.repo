import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av
import cv2
import numpy as np
import mediapipe as mp
import time
from threading import Thread
import queue

# Global variables for state management
if 'expression' not in st.session_state:
    st.session_state.expression = ""
if 'result' not in st.session_state:
    st.session_state.result = ""
if 'last_update_time' not in st.session_state:
    st.session_state.last_update_time = 0
if 'last_finger_count' not in st.session_state:
    st.session_state.last_finger_count = None

# MediaPipe setup
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Gesture recognition parameters
GESTURE_BUFFER_SIZE = 3
MOVEMENT_THRESHOLD = 0.03

# Session state for debouncing and stability
if 'last_gestures' not in st.session_state:
    st.session_state.last_gestures = []
if 'last_digit' not in st.session_state:
    st.session_state.last_digit = None
if 'last_hand_pos' not in st.session_state:
    st.session_state.last_hand_pos = None

def speak(text):
    """Text-to-speech function with error handling"""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        # Silently fail if TTS is not available
        pass

def euclidean_distance(p1, p2):
    """Calculate distance between two points"""
    return np.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

def count_fingers(hand_landmarks, label):
    """Count fingers that are up"""
    tip_ids = [4, 8, 12, 16, 20]
    fingers = []
    
    if label == "Left":
        fingers.append(1 if hand_landmarks.landmark[tip_ids[0]].x > hand_landmarks.landmark[tip_ids[0]-1].x else 0)
    else:
        fingers.append(1 if hand_landmarks.landmark[tip_ids[0]].x < hand_landmarks.landmark[tip_ids[0]-1].x else 0)
    
    for ids in range(1, 5):
        if hand_landmarks.landmark[tip_ids[ids]].y < hand_landmarks.landmark[tip_ids[ids]-2].y:
            fingers.append(1)
        else:
            fingers.append(0)
    
    return fingers.count(1)

def detect_gesture(hand1_data, hand2_data):
    (hand1, label1), (hand2, label2) = hand1_data, hand2_data
    f1 = count_fingers(hand1, label1)
    f2 = count_fingers(hand2, label2)
    # Identify left and right hands
    if label1 == "Right":
        right_hand, left_hand = hand1, hand2
    else:
        right_hand, left_hand = hand2, hand1
    # Exit gesture: right index < left index (spatial)
    if right_hand.landmark[8].x < left_hand.landmark[8].x:
        return "exit"
    # Gesture mapping
    if f1 == 1 and f2 == 1:
        return "+"
    elif (f1 == 1 and f2 == 2) or (f1 == 2 and f2 == 1):
        return "-"
    elif (f1 == 1 and f2 == 3) or (f1 == 3 and f2 == 1):
        return "*"
    elif (f1 == 1 and f2 == 4) or (f1 == 4 and f2 == 1):
        return "/"
    elif (f1 == 2 and f2 == 2):
        return "del"
    elif (f1 == 1 and f2 == 5) or (f1 == 5 and f2 == 1):
        return "6"
    elif (f1 == 2 and f2 == 5) or (f1 == 5 and f2 == 2):
        return "7"
    elif (f1 == 3 and f2 == 5) or (f1 == 5 and f2 == 3):
        return "8"
    elif (f1 == 4 and f2 == 5) or (f1 == 5 and f2 == 4):
        return "9"
    elif f1 == 0 and f2 == 0:
        return "="
    elif f1 == 5 and f2 == 5:
        return "clear"
    return None

class MathSolverTransformer(VideoTransformerBase):
    def __init__(self):
        self.hands = mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.85,
            min_tracking_confidence=0.85
        )
        self.delay = 1.25
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        current_time = time.time()
        hand_data = []
        # Process hand landmarks
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, hand_handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                label = hand_handedness.classification[0].label
                hand_data.append((hand_landmarks, label))
                mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            # Single hand detection for digits 0-5
            if len(hand_data) == 1:
                hand_landmarks, label = hand_data[0]
                fingers_up = count_fingers(hand_landmarks, label)
                # Calculate hand movement
                hand_center = hand_landmarks.landmark[0]
                if st.session_state.last_hand_pos is not None:
                    movement = np.sqrt((hand_center.x - st.session_state.last_hand_pos[0])**2 + (hand_center.y - st.session_state.last_hand_pos[1])**2)
                else:
                    movement = 0
                st.session_state.last_hand_pos = (hand_center.x, hand_center.y)
                if (fingers_up in [0, 1, 2, 3, 4, 5] and
                    current_time - st.session_state.last_update_time > self.delay and
                    movement < MOVEMENT_THRESHOLD):
                    if st.session_state.last_digit != fingers_up:
                        st.session_state.last_digit = fingers_up
                        st.session_state.last_update_time = current_time
                        st.session_state.expression += str(fingers_up)
            # Two hand detection for operations and multi-digit numbers
            if len(hand_data) == 2:
                gesture = detect_gesture(hand_data[0], hand_data[1])
                st.session_state.last_gestures.append(gesture)
                if len(st.session_state.last_gestures) > GESTURE_BUFFER_SIZE:
                    st.session_state.last_gestures.pop(0)
                if (gesture and st.session_state.last_gestures.count(gesture) == GESTURE_BUFFER_SIZE and
                    current_time - st.session_state.last_update_time > self.delay):
                    if gesture == "clear":
                        st.session_state.expression = ""
                        st.session_state.result = ""
                    elif gesture == "del":
                        st.session_state.expression = st.session_state.expression[:-1]
                    elif gesture == "=":
                        try:
                            st.session_state.result = str(eval(st.session_state.expression))
                            Thread(target=speak, args=(f"Result is {st.session_state.result}",)).start()
                        except:
                            st.session_state.result = "Error"
                    elif gesture == "exit":
                        st.session_state.expression = ""
                        st.session_state.result = ""
                        st.session_state.last_gestures = []
                        st.session_state.last_digit = None
                        st.session_state.last_hand_pos = None
                        st.session_state.last_update_time = current_time
                        # Optionally, you can add a message or stop the stream
                    else:
                        st.session_state.expression += gesture
                    st.session_state.last_update_time = current_time
                    st.session_state.last_gestures = []
        else:
            st.session_state.last_hand_pos = None
            st.session_state.last_digit = None
            st.session_state.last_gestures = []
        cv2.putText(img, f'Expression: {st.session_state.expression}', 
                   (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        cv2.putText(img, f'Result: {st.session_state.result}', 
                   (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
        return img

def main():
    st.set_page_config(
        page_title="Hand Gesture Math Solver",
        page_icon="🧮",
        layout="wide"
    )
    
    st.title("🤚 Hand Gesture Math Solver")
    st.markdown("---")
    
    # Sidebar with instructions
    with st.sidebar:
        st.header("📖 How to Use")
        st.markdown("""
        **Single Hand Gestures:**
        - 1-5 fingers: Input digits 1-5
        - 0 fingers: Input digit 0
        
        **Two Hand Gestures:**
        - 1 finger each: Addition (+)
        - 1 + 2 fingers: Subtraction (-)
        - 1 + 3 fingers: Multiplication (*)
        - 1 + 4 fingers: Division (/)
        - 0 fingers each: Evaluate (=)
        - 5 fingers each: Clear
        - 2 fingers each: Delete last digit
        - 1 + 5 fingers: Digit 6
        - 2 + 5 fingers: Digit 7
        - 3 + 5 fingers: Digit 8
        - 4 + 5 fingers: Digit 9
        """)
        
        st.header("🎯 Tips")
        st.markdown("""
        - Keep your hands clearly visible
        - Hold gestures steady for 1-2 seconds
        - Ensure good lighting
        - Position hands at comfortable distance
        """)
        
        # Clear button
        if st.button("🗑️ Clear All"):
            st.session_state.expression = ""
            st.session_state.result = ""
            st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📹 Live Camera Feed")
        webrtc_ctx = webrtc_streamer(
            key="mathsolver",
            video_transformer_factory=MathSolverTransformer,
            rtc_configuration={
                "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
            },
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )
    
    with col2:
        st.header("📊 Current Status")
        
        # Display current expression and result
        st.subheader("Expression:")
        st.code(st.session_state.expression if st.session_state.expression else "No input yet")
        
        st.subheader("Result:")
        if st.session_state.result:
            st.success(st.session_state.result)
        else:
            st.info("No result yet")
        
        # Status indicators
        st.subheader("Status:")
        if webrtc_ctx.state.playing:
            st.success("✅ Camera Active")
        else:
            st.warning("⏸️ Camera Paused")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Built using OpenCV, MediaPipe, and Streamlit</p>
        <p>Press 'Start' to begin gesture recognition</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    st.markdown("""
    ---
    ### 🌐 To deploy this app for a public/forever link:
    1. Push your code to GitHub.
    2. Go to [Streamlit Community Cloud](https://streamlit.io/cloud).
    3. Click 'New app', connect your repo, and deploy!
    4. You'll get a public link you can use forever (as long as you keep the repo and Streamlit Cloud account).
    """)
