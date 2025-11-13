#!/usr/bin/env python3
"""
Camera và OCR Service cho Raspberry Pi 4
Chụp ảnh xe, detect biển số bằng YOLOv5, OCR bằng Tesseract
Sau đó gửi request đến backend Node.js
"""

import cv2
import pytesseract
import requests
import time
from datetime import datetime
import os

# Configuration
BACKEND_URL = "http://localhost:3001/api/vehicle"
IMAGE_SAVE_PATH = "/home/pi/parking/public/images"
CAMERA_ID_ENTRY = "CAM01"
CAMERA_ID_EXIT = "CAM02"

# Tesseract config
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

class ParkingCameraService:
    def __init__(self, camera_index=0, camera_type="entry"):
        """
        Initialize camera service
        :param camera_index: Camera index (0 for default camera)
        :param camera_type: "entry" or "exit"
        """
        self.camera = cv2.VideoCapture(camera_index)
        self.camera_type = camera_type
        self.camera_id = CAMERA_ID_ENTRY if camera_type == "entry" else CAMERA_ID_EXIT
        
    def capture_image(self):
        """Capture image from camera"""
        ret, frame = self.camera.read()
        if ret:
            return frame
        return None
    
    def detect_license_plate(self, image):
        """
        Detect license plate using YOLOv5 (simplified version)
        TODO: Integrate actual YOLOv5 model
        """
        # Placeholder: In production, use YOLOv5 here
        # For now, return the whole image
        return image
    
    def ocr_license_plate(self, plate_image):
        """
        Extract text from license plate using Tesseract OCR
        """
        # Convert to grayscale
        gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
        
        # Apply preprocessing
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        
        # OCR
        config = '--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-'
        text = pytesseract.image_to_string(gray, config=config)
        
        # Clean text
        text = text.strip().replace(' ', '').replace('\n', '')
        
        return text
    
    def save_image(self, image, license_plate):
        """Save image to disk"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.camera_type}_{license_plate}_{timestamp}.jpg"
        filepath = os.path.join(IMAGE_SAVE_PATH, filename)
        
        # Create directory if not exists
        os.makedirs(IMAGE_SAVE_PATH, exist_ok=True)
        
        cv2.imwrite(filepath, image)
        return f"/images/{filename}"
    
    def send_to_backend(self, license_plate, image_path):
        """Send vehicle data to backend"""
        endpoint = f"{BACKEND_URL}/entry" if self.camera_type == "entry" else f"{BACKEND_URL}/exit"
        
        data = {
            "licensePlate": license_plate,
            "cameraId": self.camera_id,
            "imagePath": image_path,
            "confidence": 0.95,  # TODO: Get from YOLOv5
            "ocrConfidence": 0.90  # TODO: Get from Tesseract
        }
        
        try:
            response = requests.post(endpoint, json=data)
            if response.status_code in [200, 201]:
                print(f"✅ Sent to backend: {license_plate}")
                return response.json()
            else:
                print(f"❌ Backend error: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return None
    
    def process_vehicle(self):
        """Main processing pipeline"""
        print(f"📸 Capturing image from {self.camera_type} camera...")
        
        # 1. Capture image
        image = self.capture_image()
        if image is None:
            print("❌ Failed to capture image")
            return None
        
        # 2. Detect license plate
        plate_image = self.detect_license_plate(image)
        
        # 3. OCR
        license_plate = self.ocr_license_plate(plate_image)
        
        if not license_plate or len(license_plate) < 5:
            print("❌ No valid license plate detected")
            return None
        
        print(f"🚗 Detected: {license_plate}")
        
        # 4. Save image
        image_path = self.save_image(image, license_plate)
        
        # 5. Send to backend
        result = self.send_to_backend(license_plate, image_path)
        
        return result
    
    def cleanup(self):
        """Release camera"""
        self.camera.release()

# Example usage for testing
if __name__ == "__main__":
    print("🚀 Starting Parking Camera Service...")
    print("Press Ctrl+C to stop\n")
    
    # Initialize entry camera
    entry_camera = ParkingCameraService(camera_index=0, camera_type="entry")
    
    # Initialize exit camera (if you have 2 cameras)
    # exit_camera = ParkingCameraService(camera_index=1, camera_type="exit")
    
    try:
        while True:
            # Check for trigger (button press, motion sensor, etc.)
            # For demo, process every 10 seconds
            
            print("\n" + "="*50)
            print("Waiting for vehicle...")
            time.sleep(10)  # Replace with actual trigger
            
            # Process entry
            result = entry_camera.process_vehicle()
            
            if result:
                print(f"✅ Vehicle processed: {result}")
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping service...")
        entry_camera.cleanup()
        print("✅ Service stopped")
