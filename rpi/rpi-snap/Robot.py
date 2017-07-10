#
# Author: Jean-Marc Guiraudet
#
# based on:
#
# Simple two DC motor robot class.  Exposes a simple LOGO turtle-like API for
# moving a robot forward, backward, and turning.  See RobotTest.py for an
# example of using this class.
# Author: Tony DiCola
# License: MIT License https://opensource.org/licenses/MIT
import time
import atexit
import re

from Adafruit_MotorHAT import Adafruit_MotorHAT
import RPi.GPIO as GPIO

class Robot(object):

    # List of the body position sensing swithes from front to back
    body_switch = [
        (1,1,0,0), # 0. Head on right
        (1,1,0,1), # 1. 
        (1,0,0,1), # 2. Head slight right
        (1,0,1,1), # 3. Head front
        (1,0,1,0), # 4. Head left
        (0,0,1,0), # 5. Vertical
        (1,0,1,0), # 6. Body slightly leaning down
        (1,1,1,0)] # 7. Body leaning down

    def body(self, speed, position):
        # Move the body/head to a given position
        position = min(position,7)
        if position>self.posture:
            self.back(speed)
        else:
            self.front(speed)
            position = max(position-1,0)
        while True:
            body_input = self.body_input()
            if (body_input == Robot.body_switch[position]):
                self.posture=position
                break
            elif (position<=self.posture) and (body_input == Robot.body_switch[0]) :
                # Touched first limit switch
                self.posture=0
                break
            elif (position>=self.posture) and (body_input == Robot.body_switch[-1]):
                # Touched last limit switch
                self.posture=len(Robot.body_switch)-1
                break
        self.stop_body()


    def __init__(self, addr=0x60, body_id=1, left_id=2, right_id=3, left_trim=0, right_trim=0,
                 stop_at_exit=True):
        """Create an instance of the robot.  Can specify the following optional
        parameters:
         - addr: The I2C address of the motor HAT, default is 0x60.
         - left_id: The ID of the left motor, default is 1.
         - right_id: The ID of the right motor, default is 2.
         - left_trim: Amount to offset the speed of the left motor, can be positive
                      or negative and use useful for matching the speed of both
                      motors.  Default is 0.
         - right_trim: Amount to offset the speed of the right motor (see above).
         - stop_at_exit: Boolean to indicate if the motors should stop on program
                         exit.  Default is True (highly recommended to keep this
                         value to prevent damage to the bot on program crash!).
        """
        # Initialize motor HAT and left, right motor.
        self._mh = Adafruit_MotorHAT(addr)
        self._left = self._mh.getMotor(left_id)
        self._right = self._mh.getMotor(right_id)
        self._body = self._mh.getMotor(body_id)
        self._left_trim = left_trim
        self._right_trim = right_trim
        # Start with motors turned off.
        self._left.run(Adafruit_MotorHAT.RELEASE)
        self._right.run(Adafruit_MotorHAT.RELEASE)
        self._body.run(Adafruit_MotorHAT.RELEASE)
        # Internal state
        self.posture=-1
        # Configure all motors to stop at program exit if desired.
        if stop_at_exit:
            atexit.register(self.stop)
            atexit.register(self.stop_body)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.switch = self.body_input(debouncing=False)        
        self.posture = Robot.body_switch.index(self.switch)
        
        
    def button(self):
        return GPIO.input(13)

    def body_input(self, debouncing=True):
        switch = (GPIO.input(16),GPIO.input(19),GPIO.input(20),GPIO.input(21))
        if not debouncing:
            self.switch = switch
            self.new_switch = switch
            self.last_switch_change_time = time.time()
        if switch != self.new_switch:
            # Start deboincing
            self.last_switch_change_time = time.time()
            self.new_switch = switch
        elif self.new_switch != self.switch and self.last_switch_change_time+0.100<time.time():
            # A new value is pending in self.new_switch and the debounce timeout has elapsed
            self.switch = self.new_switch        
        return self.switch

    def _left_speed(self, speed):
        """Set the speed of the left motor, taking into account its trim offset.
        """
        assert -255 <= speed <= 255, 'Speed must be a value between -255 to 255 inclusive!'
        speed = -speed  # Inverse the speed as the motor is mounted in the other direction
        speed += self._left_trim
        speed = max(-255, min(255, speed))  # Constrain speed to 0-255 after trimming.
        if speed < 0:
             speed = -speed
             self._left.run(Adafruit_MotorHAT.BACKWARD)
        else:
             self._left.run(Adafruit_MotorHAT.FORWARD)
        self._left.setSpeed(speed)

    def _right_speed(self, speed):
        """Set the speed of the right motor, taking into account its trim offset.
        """
        assert -255 <= speed <= 255, 'Speed must be a value between -255 to 255 inclusive!'
        speed += self._right_trim
        speed = max(-255, min(255, speed))  # Constrain speed to 0-255 after trimming.
        if speed < 0:
             speed = -speed
             self._right.run(Adafruit_MotorHAT.BACKWARD)
        else:
             self._right.run(Adafruit_MotorHAT.FORWARD)
        self._right.setSpeed(speed)

    def _body_speed(self, speed):
        """Set the speed of the body inclination motor.
        """
        assert 0 <= speed <= 255, 'Speed must be a value between 0 to 255 inclusive!'
        speed = max(0, min(255, speed))  # Constrain speed to 0-255 after trimming.
        self._body.setSpeed(speed)

    def stop(self):
        """Stop all movement."""
        self._left.run(Adafruit_MotorHAT.RELEASE)
        self._right.run(Adafruit_MotorHAT.RELEASE)

    def stop_body(self):
        """Stop all movement."""
        self._body.run(Adafruit_MotorHAT.RELEASE)

    def forward(self, speed, seconds=None):
        """Move forward at the specified speed (0-255).  Will start moving
        forward and return unless a seconds value is specified, in which
        case the robot will move forward for that amount of time and then stop.
        """
        # Set motor speed and move both forward.
        self._left_speed(speed)
        self._right_speed(speed)
        self._left.run(Adafruit_MotorHAT.FORWARD)
        self._right.run(Adafruit_MotorHAT.BACKWARD)
        # If an amount of time is specified, move for that time and then stop.
        if seconds is not None:
            time.sleep(seconds)
            self.stop()

    def backward(self, speed, seconds=None):
        """Move backward at the specified speed (0-255).  Will start moving
        backward and return unless a seconds value is specified, in which
        case the robot will move backward for that amount of time and then stop.
        """
        # Set motor speed and move both backward.
        self._left_speed(speed)
        self._right_speed(speed)
        self._left.run(Adafruit_MotorHAT.BACKWARD)
        self._right.run(Adafruit_MotorHAT.FORWARD)
        # If an amount of time is specified, move for that time and then stop.
        if seconds is not None:
            time.sleep(seconds)
            self.stop()

    def right(self, speed, seconds=None):
        """Spin to the right at the specified speed.  Will start spinning and
        return unless a seconds value is specified, in which case the robot will
        spin for that amount of time and then stop.
        """
        # Set motor speed and move both forward.
        self._left_speed(speed)
        self._right_speed(speed)
        self._left.run(Adafruit_MotorHAT.BACKWARD)
        self._right.run(Adafruit_MotorHAT.BACKWARD)
        # If an amount of time is specified, move for that time and then stop.
        if seconds is not None:
            time.sleep(seconds)
            self.stop()

    def left(self, speed, seconds=None):
        """Spin to the left at the specified speed.  Will start spinning and
        return unless a seconds value is specified, in which case the robot will
        spin for that amount of time and then stop.
        """
        # Set motor speed and move both forward.
        self._left_speed(speed)
        self._right_speed(speed)
        self._left.run(Adafruit_MotorHAT.FORWARD)
        self._right.run(Adafruit_MotorHAT.FORWARD)
        # If an amount of time is specified, move for that time and then stop.
        if seconds is not None:
            time.sleep(seconds)
            self.stop()


    def front(self, speed, seconds=None):
        """Spin to the right at the specified speed.  Will start spinning and
        return unless a seconds value is specified, in which case the robot will
        spin for that amount of time and then stop.
        """
        # Set motor speed and move both forward.
        self._body_speed(speed)
        self._body.run(Adafruit_MotorHAT.BACKWARD)
        # If an amount of time is specified, move for that time and then stop.
        if seconds is not None:
            time.sleep(seconds)
            self.stop_body()

    def back(self, speed, seconds=None):
        """Spin to the left at the specified speed.  Will start spinning and
        return unless a seconds value is specified, in which case the robot will
        spin for that amount of time and then stop.
        """
        # Set motor speed and move both forward.
        self._body_speed(speed)
        self._body.run(Adafruit_MotorHAT.FORWARD)
        # If an amount of time is specified, move for that time and then stop.
        if seconds is not None:
            time.sleep(seconds)
            self.stop_body()

    _wifi_level_pattern=re.compile(r'wlan0:\s+\S+\s+\S+\s+(\S+)')
    def wifi_level(self):
        "Read wireless signal level in dBm"
        with open('/proc/net/wireless') as proc:
            text = proc.read(-1)
            m = Robot._wifi_level_pattern.search(text)            
            return float(m.group(1))

            



