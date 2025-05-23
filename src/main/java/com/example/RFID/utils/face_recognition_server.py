#!/usr/bin/env python3
"""
Face Recognition Server Script
Called by Java server to verify employee faces
Usage: python3 face_recognition_server.py <rfid>
Exit codes: 0 = verified, 1 = not verified, 2 = error
"""

import face_recognition
import cv2
import os
import sys
import numpy as np
import time

def load_employee_face(known_faces_dir="known_faces", rfid=None):
    """Load and encode employee face from the known faces directory"""
    if not os.path.exists(known_faces_dir):
        print(f"❌ Directory '{known_faces_dir}' not found!")
        return None, None

    # Look for the employee's image file using RFID
    target_encoding = None
    target_file = None

    # Check different possible file extensions
    possible_extensions = ['.jpg', '.jpeg', '.png', '.bmp']

    for ext in possible_extensions:
        potential_file = f"{rfid}{ext}"
        file_path = os.path.join(known_faces_dir, potential_file)

        if os.path.exists(file_path):
            target_file = potential_file
            break

    if not target_file:
        print(f"❌ No image found for RFID '{rfid}' in '{known_faces_dir}'!")
        available_files = [f for f in os.listdir(known_faces_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        print(f"   Available image files: {available_files}")
        return None, None

    try:
        print(f"📁 Loading employee face: {target_file}")

        # Load the employee's image
        image_path = os.path.join(known_faces_dir, target_file)
        image = face_recognition.load_image_file(image_path)

        # Get face encodings
        encodings = face_recognition.face_encodings(image)

        if encodings:
            target_encoding = encodings[0]
            print(f"✅ Successfully loaded face for RFID: {rfid}")
            return target_encoding, rfid
        else:
            print(f"❌ No face found in: {target_file}")
            return None, None

    except Exception as e:
        print(f"❌ Error loading {target_file}: {str(e)}")
        return None, None

def verify_face_with_camera(target_encoding, rfid, timeout_seconds=10):
    """Verify face using webcam with timeout"""
    print(f"🔍 Starting face verification for RFID: {rfid}")
    print(f"⏱️  Verification timeout: {timeout_seconds} seconds")

    # Open webcam
    video_capture = cv2.VideoCapture(0)

    if not video_capture.isOpened():
        print("❌ Error: Could not open webcam!")
        return False

    # Set camera properties for better performance
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    video_capture.set(cv2.CAP_PROP_FPS, 30)

    start_time = time.time()
    process_this_frame = True
    verification_successful = False
    consecutive_matches = 0
    required_matches = 3  # Require 3 consecutive matches for verification

    print("📷 Camera ready. Please look at the camera...")

    while True:
        ret, frame = video_capture.read()

        if not ret:
            print("❌ Error: Could not read frame from webcam!")
            break

        # Check timeout
        elapsed_time = time.time() - start_time
        if elapsed_time > timeout_seconds:
            print(f"⏰ Verification timeout ({timeout_seconds}s)")
            break

        # Only process every other frame for better performance
        if process_this_frame:
            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Find faces in current frame
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            face_match_found = False

            for unknown_encoding in face_encodings:
                # Compare with the target face
                matches = face_recognition.compare_faces([target_encoding], unknown_encoding, tolerance=0.8)
                distance = face_recognition.face_distance([target_encoding], unknown_encoding)[0]

                if matches[0] and distance < 0.5:  # Stricter threshold for security
                    confidence = round((1 - distance) * 100, 1)
                    consecutive_matches += 1
                    face_match_found = True
                    print(f"✅ Face match found! Confidence: {confidence}% (Match {consecutive_matches}/{required_matches})")

                    if consecutive_matches >= required_matches:
                        print(f"🎉 Face verification successful for RFID: {rfid}")
                        verification_successful = True
                        break

            if not face_match_found:
                consecutive_matches = 0  # Reset counter if no match found

        process_this_frame = not process_this_frame

        if verification_successful:
            break

        # Optional: Display frame (comment out for headless operation)
        # cv2.imshow(f"Verifying {rfid}", frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

    # Clean up
    video_capture.release()
    cv2.destroyAllWindows()

    return verification_successful

def main():
    """Main verification function"""
    if len(sys.argv) != 3   :
        print("❌ Usage: python3 face_recognition_server.py <rfid>")
        sys.exit(2)

    rfid = sys.argv[1]
    print(f"🔐 Starting face verification for RFID: {rfid}")

    # Load the employee's face from the known faces directory
    """Main verification function"""
    if len(sys.argv) != 3:  # Now expects RFID and path
        print("❌ Usage: python3 face_recognition_server.py <rfid> <known_faces_path>")
        sys.exit(2)

    rfid = sys.argv[1]
    known_faces_path = sys.argv[2]
    print(f"🔐 Starting face verification for RFID: {rfid}")

    # Load the employee's face from the known faces directory
    target_encoding, target_rfid = load_employee_face(known_faces_path, rfid)
# rest of the function remains the same

    if target_encoding is None:
        print(f"❌ Could not load face data for RFID: {rfid}")
        sys.exit(1)  # Face data not found

    # Perform face verification with camera
    verification_result = verify_face_with_camera(target_encoding, rfid, timeout_seconds=15)

    if verification_result:
        print(f"✅ Face verification SUCCESSFUL for RFID: {rfid}")
        sys.exit(0)  # Success
    else:
        print(f"❌ Face verification FAILED for RFID: {rfid}")
        sys.exit(1)  # Verification failed

if __name__ == "__main__":
    main()