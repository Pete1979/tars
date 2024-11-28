import cv2
import pytesseract
from modules.camera import capture_frame

def describe_camera_view(cap):
    print("Capturing frame for OCR...")
    try:
        frame = capture_frame(cap)
        if frame is None:
            return "Failed to capture image."
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)
        return f"The camera sees the following text: {text}" if text.strip() else "I could not detect any text."
    except Exception as e:
        print(f"Error describing camera view: {e}")
        return "Error describing camera view."