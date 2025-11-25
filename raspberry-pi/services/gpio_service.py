"""
GPIO Service
Handles GPIO control for gates, LEDs, and buzzer
"""
import time

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False

from config.settings import GATE_OPEN_DURATION, LED_BLINK_INTERVAL, BUZZER_BEEP_DURATION
from config.pins import (
    ENTRY_GATE_PIN, ENTRY_GREEN_LED, ENTRY_RED_LED, ENTRY_BUZZER,
    EXIT_GATE_PIN, EXIT_GREEN_LED, EXIT_RED_LED, EXIT_BUZZER,
    SERVO_FREQUENCY, SERVO_OPEN_ANGLE, SERVO_CLOSE_ANGLE
)
from utils.logger import get_logger

logger = get_logger(__name__)

class GPIOService:
    """Service to handle GPIO control"""
    
    def __init__(self, lane_type='entry'):
        """
        Initialize GPIO service
        
        Args:
            lane_type: 'entry' or 'exit'
        """
        self.lane_type = lane_type
        self.gpio_available = GPIO_AVAILABLE
        
        if lane_type == 'entry':
            self.gate_pin = ENTRY_GATE_PIN
            self.green_led = ENTRY_GREEN_LED
            self.red_led = ENTRY_RED_LED
            self.buzzer = ENTRY_BUZZER
        else:
            self.gate_pin = EXIT_GATE_PIN
            self.green_led = EXIT_GREEN_LED
            self.red_led = EXIT_RED_LED
            self.buzzer = EXIT_BUZZER
        
        self.servo_pwm = None
        
        if self.gpio_available:
            self._init_gpio()
        else:
            logger.warning("⚠️ GPIO not available, running in simulation mode")
    
    def _init_gpio(self):
        """Initialize GPIO pins"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Setup LED pins
            GPIO.setup(self.green_led, GPIO.OUT)
            GPIO.setup(self.red_led, GPIO.OUT)
            GPIO.setup(self.buzzer, GPIO.OUT)
            
            # Setup servo pin
            GPIO.setup(self.gate_pin, GPIO.OUT)
            self.servo_pwm = GPIO.PWM(self.gate_pin, SERVO_FREQUENCY)
            self.servo_pwm.start(0)
            
            # Initial state: all off
            GPIO.output(self.green_led, GPIO.LOW)
            GPIO.output(self.red_led, GPIO.LOW)
            GPIO.output(self.buzzer, GPIO.LOW)
            
            logger.info(f"✅ GPIO initialized for {self.lane_type} lane")
            
        except Exception as e:
            logger.error(f"❌ GPIO initialization error: {e}")
            self.gpio_available = False
    
    def _angle_to_duty_cycle(self, angle):
        """
        Convert servo angle to PWM duty cycle
        
        Args:
            angle: Angle in degrees (0-180)
            
        Returns:
            float: Duty cycle (2-12)
        """
        return 2 + (angle / 18)
    
    def open_gate(self):
        """Open gate (rotate servo to open position)"""
        if not self.gpio_available or not self.servo_pwm:
            logger.warning("⚠️ GPIO not available, simulating gate open")
            time.sleep(1)
            return
        
        try:
            logger.info("🚪 Opening gate...")
            duty = self._angle_to_duty_cycle(SERVO_OPEN_ANGLE)
            self.servo_pwm.ChangeDutyCycle(duty)
            time.sleep(1)  # Wait for servo to move
            self.servo_pwm.ChangeDutyCycle(0)  # Stop sending signal
            logger.info("✅ Gate opened")
            
        except Exception as e:
            logger.error(f"❌ Gate open error: {e}")
    
    def close_gate(self):
        """Close gate (rotate servo to closed position)"""
        if not self.gpio_available or not self.servo_pwm:
            logger.warning("⚠️ GPIO not available, simulating gate close")
            time.sleep(1)
            return
        
        try:
            logger.info("🚪 Closing gate...")
            duty = self._angle_to_duty_cycle(SERVO_CLOSE_ANGLE)
            self.servo_pwm.ChangeDutyCycle(duty)
            time.sleep(1)  # Wait for servo to move
            self.servo_pwm.ChangeDutyCycle(0)  # Stop sending signal
            logger.info("✅ Gate closed")
            
        except Exception as e:
            logger.error(f"❌ Gate close error: {e}")
    
    def green_led_on(self):
        """Turn on green LED"""
        if not self.gpio_available:
            logger.info("💚 [SIM] Green LED ON")
            return
        
        try:
            GPIO.output(self.green_led, GPIO.HIGH)
            logger.info("💚 Green LED ON")
        except Exception as e:
            logger.error(f"❌ Green LED error: {e}")
    
    def green_led_off(self):
        """Turn off green LED"""
        if not self.gpio_available:
            return
        
        try:
            GPIO.output(self.green_led, GPIO.LOW)
        except Exception as e:
            logger.error(f"❌ Green LED error: {e}")
    
    def red_led_on(self):
        """Turn on red LED"""
        if not self.gpio_available:
            logger.info("🔴 [SIM] Red LED ON")
            return
        
        try:
            GPIO.output(self.red_led, GPIO.HIGH)
            logger.info("🔴 Red LED ON")
        except Exception as e:
            logger.error(f"❌ Red LED error: {e}")
    
    def red_led_off(self):
        """Turn off red LED"""
        if not self.gpio_available:
            return
        
        try:
            GPIO.output(self.red_led, GPIO.LOW)
        except Exception as e:
            logger.error(f"❌ Red LED error: {e}")
    
    def all_leds_off(self):
        """Turn off all LEDs"""
        self.green_led_off()
        self.red_led_off()
    
    def blink_green(self, times=3):
        """
        Blink green LED
        
        Args:
            times: Number of blinks
        """
        for _ in range(times):
            self.green_led_on()
            time.sleep(LED_BLINK_INTERVAL)
            self.green_led_off()
            time.sleep(LED_BLINK_INTERVAL)
    
    def blink_red(self, times=3):
        """
        Blink red LED
        
        Args:
            times: Number of blinks
        """
        for _ in range(times):
            self.red_led_on()
            time.sleep(LED_BLINK_INTERVAL)
            self.red_led_off()
            time.sleep(LED_BLINK_INTERVAL)
    
    def beep(self, times=1):
        """
        Beep buzzer
        
        Args:
            times: Number of beeps
        """
        if not self.gpio_available:
            logger.info(f"🔊 [SIM] BEEP x{times}")
            return
        
        try:
            for _ in range(times):
                GPIO.output(self.buzzer, GPIO.HIGH)
                time.sleep(BUZZER_BEEP_DURATION)
                GPIO.output(self.buzzer, GPIO.LOW)
                time.sleep(BUZZER_BEEP_DURATION)
        except Exception as e:
            logger.error(f"❌ Buzzer error: {e}")
    
    def success_feedback(self):
        """Visual and audio feedback for success"""
        self.green_led_on()
        self.beep(1)
        time.sleep(1)
        self.green_led_off()
    
    def error_feedback(self):
        """Visual and audio feedback for error"""
        self.blink_red(3)
        self.beep(3)
    
    def cleanup(self):
        """Cleanup GPIO resources"""
        try:
            if self.gpio_available:
                if self.servo_pwm:
                    self.servo_pwm.stop()
                self.all_leds_off()
                GPIO.output(self.buzzer, GPIO.LOW)
                GPIO.cleanup()
                logger.info("✅ GPIO cleanup completed")
        except Exception as e:
            logger.error(f"❌ GPIO cleanup error: {e}")
