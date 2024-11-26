import cv2
import pytesseract

# Initialize the video capture (camera)
cap = cv2.VideoCapture("/dev/video0")  # Adjust if necessary for your camera device

if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

# Start capturing frames
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to grayscale for better OCR accuracy
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Optionally apply thresholding or blurring to improve OCR accuracy
    # gray = cv2.GaussianBlur(gray, (5, 5), 0)
    # _, gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # Use pytesseract to extract text from the image
    text = pytesseract.image_to_string(gray)

    # Print the recognized text
    if text.strip():
        print("Recognized text:", text)

    # Exit condition for testing purposes
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera
cap.release()
