import streamlit as st
from streamlit_webrtc import webrtc_streamer
import av, cv2
from mathSolver import process_frame, speak  # adjust names if needed

st.title("Gesture Math Solver")

def video_frame_callback(frame: av.VideoFrame):
    img = frame.to_ndarray(format="bgr24")
    result = process_frame(img)  # uses your existing processing logic
    if result is not None:
        speak(f"Result is {result}")
        cv2.putText(img, str(result), (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    return av.VideoFrame.from_ndarray(img, format="bgr24")

webrtc_streamer(key="mathsolver", video_frame_callback=video_frame_callback)
