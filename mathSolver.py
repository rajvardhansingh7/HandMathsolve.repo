import cv2 as cv
import mediapipe as mp
import numpy as np
import time
import pyttsx3
import sys

# Initialize text-to-speech engine
try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)   # speaking speed
    engine.setProperty('volume', 0.9) # volume scale (0.0–1.0)
    TTS_AVAILABLE = True
except:
    print("Warning: Text-to-speech not available. Install pyttsx3 for voice output.")
    TTS_AVAILABLE = False

def speak(text):
    """Text-to-speech function with error handling"""
    if TTS_AVAILABLE:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")

# MediaPipe setup
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2, 
    min_detection_confidence=0.85,  # Increased confidence
    min_tracking_confidence=0.85   # Increased confidence
)

# Buffer for gesture debouncing
GESTURE_BUFFER_SIZE = 3
last_gestures = []
last_digit = None
last_hand_pos = None
MOVEMENT_THRESHOLD = 0.03  # Only accept digit if hand is relatively still

def euclidean_distance(p1, p2):
    """Calculate Euclidean distance between two points"""
    return np.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

def count_fingers(hand_landmarks, label):
    """Count fingers that are up based on landmark positions"""
    tip_ids = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky tips
    fingers = []
    
    # Check thumb (different logic for left/right hand)
    if label == "Left":
        fingers.append(1 if hand_landmarks.landmark[tip_ids[0]].x > hand_landmarks.landmark[tip_ids[0]-1].x else 0)
    else:
        fingers.append(1 if hand_landmarks.landmark[tip_ids[0]].x < hand_landmarks.landmark[tip_ids[0]-1].x else 0)
    
    # Check other fingers
    for ids in range(1, 5):
        if hand_landmarks.landmark[tip_ids[ids]].y < hand_landmarks.landmark[tip_ids[ids]-2].y:
            fingers.append(1)
        else:
            fingers.append(0)
    
    return fingers.count(1)

def detect_gesture(hand1_data, hand2_data):
    """Detect gestures for different mathematical operations"""
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
    dist = euclidean_distance(hand1.landmark[8], hand2.landmark[8])
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

def print_instructions():
    """Print usage instructions"""
    print("\n" + "="*60)
    print("🤚 HAND GESTURE MATH SOLVER - INSTRUCTIONS")
    print("="*60)
    print("Single Hand Gestures:")
    print("  • 1-5 fingers: Input digits 1-5")
    print("  • 0 fingers: Input digit 0")
    print("\nTwo Hand Gestures:")
    print("  • 1 finger each: Addition (+)")
    print("  • 1 + 2 fingers: Subtraction (-)")
    print("  • 1 + 3 fingers: Multiplication (*)")
    print("  • 1 + 4 fingers: Division (/)")
    print("  • 0 fingers each: Evaluate (=)")
    print("  • 5 fingers each: Clear")
    print("  • 2 fingers each: Delete last digit")
    print("  • 1 + 5 fingers: Digit 6")
    print("  • 2 + 5 fingers: Digit 7")
    print("  • 3 + 5 fingers: Digit 8")
    print("  • 4 + 5 fingers: Digit 9")
    print("\nControls:")
    print("  • Press 'q' or ESC to quit")
    print("  • Press 'c' to clear")
    print("  • Hold gestures steady for 1-2 seconds")
    print("="*60 + "\n")

def main():
    """Main function for the standalone math solver"""
    print_instructions()
    
    # Initialize variables
    last_finger_count = None
    last_update_time = 0
    delay = 1.25
    expression = ""
    result = ""
    global last_gestures, last_digit, last_hand_pos
    
    # Initialize webcam
    cap = cv.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam!")
        return
    
    print("Starting camera... Press 'q' to quit.")
    
    try:
        while True:
            success, image = cap.read()
            if not success:
                print("Error: Could not read frame!")
                break
                
            # Mirror the image for intuitive interaction
            image = cv.flip(image, 1)
            
            # Convert to RGB for MediaPipe
            img_rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
            result_hands = hands.process(img_rgb)
            
            current_time = time.time()
            hand_data = []
            
            # Process hand landmarks
            if result_hands.multi_hand_landmarks and result_hands.multi_handedness:
                for hand_landmarks, hand_handedness in zip(result_hands.multi_hand_landmarks, result_hands.multi_handedness):
                    label = hand_handedness.classification[0].label
                    hand_data.append((hand_landmarks, label))
                    mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Single hand detection for digits 0-5
                if len(hand_data) == 1:
                    hand_landmarks, label = hand_data[0]
                    fingers_up = count_fingers(hand_landmarks, label)
                    # Calculate hand movement
                    hand_center = hand_landmarks.landmark[0]
                    if last_hand_pos is not None:
                        movement = np.sqrt((hand_center.x - last_hand_pos[0])**2 + (hand_center.y - last_hand_pos[1])**2)
                    else:
                        movement = 0
                    last_hand_pos = (hand_center.x, hand_center.y)
                    # Only accept digit if hand is relatively still
                    if (fingers_up in [0, 1, 2, 3, 4, 5] and 
                        current_time - last_update_time > delay and
                        movement < MOVEMENT_THRESHOLD):
                        if last_digit != fingers_up:
                            last_digit = fingers_up
                            last_update_time = current_time
                            expression += str(fingers_up)
                            print(f"Added digit: {fingers_up}")
                
                # Two hand detection for operations and multi-digit numbers
                if len(hand_data) == 2:
                    gesture = detect_gesture(hand_data[0], hand_data[1])
                    # Debounce: Only accept gesture if it appears in 3 consecutive frames
                    last_gestures.append(gesture)
                    if len(last_gestures) > GESTURE_BUFFER_SIZE:
                        last_gestures.pop(0)
                    if (gesture and last_gestures.count(gesture) == GESTURE_BUFFER_SIZE and
                        current_time - last_update_time > delay):
                        if gesture == "clear":
                            expression = ""
                            result = ""
                            print("Cleared expression")
                        elif gesture == "del":
                            expression = expression[:-1]
                            print("Deleted last character")
                        elif gesture == "=":
                            try:
                                result = str(eval(expression))
                                print(f"Result: {result}")
                                speak(f"Result is {result}")
                            except Exception as e:
                                result = "Error"
                                print(f"Evaluation error: {e}")
                        elif gesture == "exit":
                            print("Exit gesture detected!")
                            break
                        else:
                            expression += gesture
                            print(f"Added operation: {gesture}")
                        last_update_time = current_time
                        last_gestures = []
            else:
                last_hand_pos = None
                last_digit = None
                last_gestures = []
            
            # Display expression and result on the frame
            cv.putText(image, f'Expression: {expression}', 
                      (10, 50), cv.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            cv.putText(image, f'Result: {result}', 
                      (10, 100), cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
            
            # Display instructions on frame
            cv.putText(image, "Press 'q' to quit, 'c' to clear", 
                      (10, image.shape[0] - 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Show the frame
            cv.imshow("Hand Gesture Math Solver", image)
            
            # Handle keyboard input
            key = cv.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 'q' or ESC
                break
            elif key == ord('c'):
                expression = ""
                result = ""
                print("Cleared via keyboard")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        cap.release()
        cv.destroyAllWindows()
        print("Math Solver closed.")

if __name__ == "__main__":
    main()