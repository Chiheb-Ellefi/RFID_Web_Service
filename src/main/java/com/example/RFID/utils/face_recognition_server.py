#!/usr/bin/env python3
"""
Face Recognition Server Script
Called by Java server to verify employee faces
Usage: python3 face_recognition_server.py <rfid> <image_url>
Exit codes: 0 = verified, 1 = not verified, 2 = error
"""

import face_recognition
import cv2
import os
import sys
import numpy as np
import time
import requests
from PIL import Image
import io

def download_image_from_url(image_url):
    """Download image from Firebase Cloud Storage URL"""
    try:
        print(f"📥 Downloading image from URL: {image_url}")

        # Download the image
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        # Convert to PIL Image
        image = Image.open(io.BytesIO(response.content))

        # Ensure image is in RGB mode
        if image.mode != 'RGB':
            print(f"🔄 Converting image from {image.mode} to RGB")
            image = image.convert('RGB')

        # Convert PIL Image to numpy array (RGB format)
        image_array = np.array(image, dtype=np.uint8)

        # Ensure the array is contiguous in memory
        image_array = np.ascontiguousarray(image_array)

        print(f"✅ Successfully downloaded image ({image_array.shape}, dtype: {image_array.dtype})")
        return image_array

    except requests.exceptions.RequestException as e:
        print(f"❌ Error downloading image: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Error processing downloaded image: {str(e)}")
        return None

def load_employee_face_from_url(image_url, rfid):
    """Load and encode employee face from Firebase URL"""
    print(f"📁 Loading employee face from URL for RFID: {rfid}")

    # Download the image from the URL
    image_array = download_image_from_url(image_url)

    if image_array is None:
        print(f"❌ Failed to download image for RFID: {rfid}")
        return None, None

    try:
        print(f"🔍 Looking for faces in image...")

        # First, try to find face locations
        face_locations = face_recognition.face_locations(image_array)

        if not face_locations:
            print(f"❌ No faces detected in the image for RFID: {rfid}")
            # Try with different detection model
            print(f"🔄 Trying with CNN model...")
            face_locations = face_recognition.face_locations(image_array, model="cnn")

        if not face_locations:
            print(f"❌ Still no faces found in the downloaded image for RFID: {rfid}")
            return None, None

        print(f"✅ Found {len(face_locations)} face(s) in the image")

        # Get face encodings from the detected faces
        encodings = face_recognition.face_encodings(image_array, face_locations)

        if encodings:
            target_encoding = encodings[0]  # Use the first face found
            print(f"✅ Successfully created face encoding for RFID: {rfid}")
            return target_encoding, rfid
        else:
            print(f"❌ Could not create face encoding for RFID: {rfid}")
            return None, None

    except Exception as e:
        print(f"❌ Error processing face encoding for RFID {rfid}: {str(e)}")
        import traceback
        traceback.print_exc()
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
                matches = face_recognition.compare_faces([target_encoding], unknown_encoding, tolerance=0.6)
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
    if len(sys.argv) != 3:
        print("❌ Usage: python3 face_recognition_server.py <rfid> <image_url>")
        sys.exit(2)

    rfid = sys.argv[1]
    image_url = sys.argv[2]

    print(f"🔐 Starting face verification for RFID: {rfid}")
    print(f"🔗 Image URL: {image_url}")

    # Load the employee's face from the Firebase URL
    target_encoding, target_rfid = load_employee_face_from_url(image_url, rfid)

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