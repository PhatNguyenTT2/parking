"""
Camera Service
Handles camera capture and OCR for license plate recognition
"""
import cv2
import numpy as np
import time
from datetime import datetime
from pathlib import Path

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

from config.settings import (
    CAMERA_RESOLUTION, 
    CAMERA_WARMUP_TIME,
    OCR_CONFIDENCE_THRESHOLD,
    IMAGE_STORAGE_PATH
)
from config.pins import CAMERA_ID
from utils.logger import get_logger
from utils.validators import validate_license_plate, sanitize_filename

logger = get_logger(__name__)

class CameraService:
    """Service to handle camera capture and OCR"""
    
    def __init__(self, camera_id=CAMERA_ID):
        self.camera_id = camera_id
        self.camera = None
        self._init_camera()
    
    def _init_camera(self):
        """Initialize camera with retry logic"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self.camera = cv2.VideoCapture(self.camera_id)
                
                if not self.camera.isOpened():
                    raise Exception("Camera not opened")
                
                # Set resolution
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_RESOLUTION[0])
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_RESOLUTION[1])
                
                # Warm up camera
                logger.info(f"⏳ Camera warming up for {CAMERA_WARMUP_TIME}s...")
                time.sleep(CAMERA_WARMUP_TIME)
                
                # Test capture
                ret, frame = self.camera.read()
                if not ret:
                    raise Exception("Test capture failed")
                
                logger.info(f"✅ Camera {self.camera_id} initialized successfully")
                return
                
            except Exception as e:
                retry_count += 1
                logger.error(f"❌ Camera init error (attempt {retry_count}/{max_retries}): {e}")
                
                if self.camera:
                    self.camera.release()
                
                if retry_count < max_retries:
                    time.sleep(2)
        
        logger.warning("⚠️ Camera initialization failed, running in simulation mode")
        self.camera = None
    
    def capture_image(self, save_path=None):
        """
        Capture image from camera
        
        Args:
            save_path: Optional path to save image
            
        Returns:
            numpy.ndarray: Captured image or None
        """
        if not self.camera:
            logger.warning("⚠️ Camera not available, using simulation mode")
            # Create a dummy image for testing
            dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(dummy_image, "SIMULATION MODE", (100, 240),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            if save_path:
                cv2.imwrite(save_path, dummy_image)
                logger.info(f"💾 Dummy image saved to: {save_path}")
            
            return dummy_image
        
        try:
            ret, frame = self.camera.read()
            
            if not ret:
                logger.error("❌ Failed to capture image")
                return None
            
            logger.info("✅ Image captured successfully")
            
            # Save image if path provided
            if save_path:
                cv2.imwrite(save_path, frame)
                logger.info(f"💾 Image saved to: {save_path}")
            
            return frame
            
        except Exception as e:
            logger.error(f"❌ Capture error: {e}")
            return None
    
    def preprocess_image(self, image):
        """
        Preprocess image for better OCR results
        
        Args:
            image: Input image
            
        Returns:
            numpy.ndarray: Preprocessed image
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply bilateral filter to reduce noise
            filtered = cv2.bilateralFilter(gray, 11, 17, 17)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                filtered, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
            
            return thresh
            
        except Exception as e:
            logger.error(f"❌ Preprocessing error: {e}")
            return image
    
    def detect_license_plate(self, image):
        """
        Detect license plate region in image
        
        Args:
            image: Input image
            
        Returns:
            numpy.ndarray: Cropped license plate image or full image
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply edge detection
            edges = cv2.Canny(gray, 30, 200)
            
            # Find contours
            contours, _ = cv2.findContours(
                edges.copy(),
                cv2.RETR_TREE,
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Sort contours by area
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
            
            license_plate = None
            
            # Find rectangular contour (license plate)
            for contour in contours:
                perimeter = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.018 * perimeter, True)
                
                # License plate typically has 4 corners
                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Check aspect ratio (license plates are wider than tall)
                    aspect_ratio = w / float(h)
                    if 2.0 <= aspect_ratio <= 5.0:
                        license_plate = gray[y:y+h, x:x+w]
                        logger.info(f"✅ License plate region detected (aspect ratio: {aspect_ratio:.2f})")
                        break
            
            if license_plate is None:
                logger.warning("⚠️ License plate region not detected, using full image")
                license_plate = gray
            
            return license_plate
            
        except Exception as e:
            logger.error(f"❌ License plate detection error: {e}")
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def ocr_recognize(self, image):
        """
        Perform OCR on image to extract license plate text
        
        Args:
            image: Input image
            
        Returns:
            str: Recognized license plate or None
        """
        if not OCR_AVAILABLE:
            logger.warning("⚠️ OCR not available, using simulation mode")
            return "29A12345"  # Test license plate
        
        try:
            # Detect license plate region
            plate_image = self.detect_license_plate(image)
            
            # Preprocess for better OCR
            if len(plate_image.shape) == 2:  # Already grayscale
                preprocessed = self.preprocess_image(cv2.cvtColor(plate_image, cv2.COLOR_GRAY2BGR))
            else:
                preprocessed = self.preprocess_image(plate_image)
            
            # OCR configuration for license plates
            custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            
            # Perform OCR
            text = pytesseract.image_to_string(
                Image.fromarray(preprocessed),
                config=custom_config
            )
            
            # Clean up text
            text = text.strip().replace(' ', '').replace('-', '').upper()
            
            # Get confidence score
            try:
                ocr_data = pytesseract.image_to_data(
                    Image.fromarray(preprocessed),
                    config=custom_config,
                    output_type=pytesseract.Output.DICT
                )
                
                confidences = [int(conf) for conf in ocr_data['conf'] if conf != '-1']
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            except:
                avg_confidence = 50  # Default confidence
            
            logger.info(f"📝 OCR Result: '{text}' (confidence: {avg_confidence:.1f}%)")
            
            # Validate license plate format
            if validate_license_plate(text):
                if avg_confidence >= OCR_CONFIDENCE_THRESHOLD * 100:
                    logger.info(f"✅ Valid license plate detected: {text}")
                    return text
                else:
                    logger.warning(f"⚠️ Low confidence OCR result: {text} ({avg_confidence:.1f}%)")
                    return text  # Return anyway, let backend handle validation
            else:
                logger.warning(f"⚠️ Invalid license plate format: {text}")
                return None
            
        except Exception as e:
            logger.error(f"❌ OCR error: {e}")
            return None
    
    def capture_and_recognize(self, lane_type='entry'):
        """
        Capture image and perform OCR in one step
        
        Args:
            lane_type: 'entry' or 'exit'
            
        Returns:
            tuple: (license_plate, image_path)
        """
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = sanitize_filename(f"{lane_type}_{timestamp}.jpg")
        save_path = IMAGE_STORAGE_PATH / filename
        
        # Capture image
        image = self.capture_image(str(save_path))
        
        if image is None:
            return None, None
        
        # Perform OCR
        license_plate = self.ocr_recognize(image)
        
        return license_plate, str(save_path)
    
    def cleanup(self):
        """Release camera resources"""
        try:
            if self.camera:
                self.camera.release()
                logger.info("✅ Camera released")
        except Exception as e:
            logger.error(f"❌ Camera cleanup error: {e}")
