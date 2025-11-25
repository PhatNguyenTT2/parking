"""
Data validators for Parking System
"""
import re

def validate_license_plate(plate):
    """
    Validate Vietnamese license plate format
    
    Supported formats:
    - 2 digits + letter + 4-5 digits: 29A12345, 51D1234
    - 3 digits + letter + 4-5 digits: 123A12345, 456B1234
    
    Args:
        plate: License plate string
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not plate or not isinstance(plate, str):
        return False
    
    plate = plate.strip().upper()
    
    # Pattern for Vietnamese license plates
    patterns = [
        r'^\d{2}[A-Z]\d{4,5}$',    # 29A12345
        r'^\d{3}[A-Z]\d{4,5}$',    # 123A12345
    ]
    
    for pattern in patterns:
        if re.match(pattern, plate):
            return True
    
    return False

def validate_card_id(card_id):
    """
    Validate RFID card ID
    
    Args:
        card_id: Card ID string
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not card_id or not isinstance(card_id, str):
        return False
    
    # Card ID should be numeric and have reasonable length
    card_id = card_id.strip()
    
    if not card_id.isdigit():
        return False
    
    if len(card_id) < 4 or len(card_id) > 20:
        return False
    
    return True

def sanitize_filename(filename):
    """
    Sanitize filename to remove invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    return filename
