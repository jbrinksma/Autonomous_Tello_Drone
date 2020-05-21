import cv2
import time
import sys
import numpy as np

from djitellopy import Tello

from utils import (
    print_status,
    print_warning,
    print_error
)

# Frames per second of the pygame window display
FPS = 25


ESC_KEY = 27
NO_KEY = -1

# velocity for when drone is yawing to discover surroundings
SCAN_VELOCITY = 100  # (10-100)


TIME_BTW_BATTERY_CHECKS = 0.5  # seconds


class TelloDrone():
    def __init__(self):
        """
        Get the DJITelloPy Tello object to use for communication
        with the drone.

        speed: general speed for non rc control calls (10-100)
        """

        self.tello = Tello()

        self.left_right_velocity = 0
        self.forward_backward_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0

        self.has_target = False

        self.battery_level = 0
        self.last_battery_check = 0

        self.speed = 20  # Lowest

    def cleanup(self):
        """Call this function if the script has to be stopped for whatever
        reason to make sure everything is exited cleanly"""
        self.end_drone()
        cv2.destroyAllWindows()

    def end_drone(self):
        """Lands drone and ends drone interaction"""
        self.stop_moving()
        self.tello.streamoff()
        if self.tello.is_flying:
            self.tello.land()
        self.tello.end()

    def update_battery_level(self):
        if time.time() - self.last_battery_check >= TIME_BTW_BATTERY_CHECKS:
            self.battery_level = self.tello.get_battery()
            self.last_battery_check = time.time()
        

    def update_drone_velocities_if_flying(self):
        """Move drone based on velocities only if drone is flying"""
        if not self.tello.is_flying:
            return
        self.tello.send_rc_control(self.left_right_velocity,
                                   self.forward_backward_velocity,
                                   self.up_down_velocity,
                                   self.yaw_velocity)

    def update_drone_velocities(self):
        """Move drone based on velocities"""
        self.tello.send_rc_control(self.left_right_velocity,
                                   self.forward_backward_velocity,
                                   self.up_down_velocity,
                                   self.yaw_velocity)

    def stop_moving(self):
        """Freeze in place"""
        time.sleep(self.tello.TIME_BTW_RC_CONTROL_COMMANDS)  # Delay makes sure it is sent
        self.left_right_velocity = 0
        self.forward_backward_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.update_drone_velocities()

    def scan_surroundings(self):
        """Start looking around"""
        self.yaw_velocity = SCAN_VELOCITY
        self.update_drone_velocities_if_flying()

    def find_target(self):
        # Returns False for now
        return False

    def handle_user_keypress(self):
        """Check for pressed keys.

        't': Take off
        'l': Land
        'Esc': Exit


        Returns:
            key (int): unicode value of key that was pressed, or -1 if
                       none were pressed"""
        key = cv2.waitKey(20)
        if key == ord('t'):
            print_warning("Drone taking off...")
            self.tello.takeoff()
        elif key == ord('l'):
            print_warning("Landing drone...")
            self.stop_moving()
            self.tello.land()
        elif key == ESC_KEY:
            print_warning("Stopping drone...")
        elif key == NO_KEY:
            if not self.has_target:
                self.scan_surroundings()
        return key

    def initialize_before_run(self):
        """Set up drone before we bring it to life"""
        if not self.tello.connect():
            print_error("Failed to set drone to SDK mode")
            sys.exit(-1)
        print_status("Connected to Drone")

        if not self.tello.set_speed(self.speed):
            print_error("Failed to set initial drone speed")
        print_status(f"Drone speed set to {self.speed} cm/s ({self.speed}%)")
        
        # Make sure stream is off first
        self.tello.streamoff()
        self.tello.streamon()  # Not sure why DJITelloPy doesn't return here     
        self.battery_level = self.tello.get_battery()
        print_status(f"Drone battery is at {self.battery_level}%")

        # Reset velocities
        self.update_drone_velocities()
        print_status(f"All drone velocities initialized to 0")

    def run(self, user_interface=True):
        """Bring an autonomous being to life"""
        self.initialize_before_run()
        frame_read = self.tello.get_frame_read()
        while True:
            self.update_drone_velocities_if_flying()

            if frame_read.stopped:
                frame_read.stop()
                break
            frame = cv2.cvtColor(frame_read.frame, cv2.COLOR_BGR2RGB)
            frame_ret = frame_read.frame
            tello_cam = self.tello.get_video_capture()
            time.sleep(1 / FPS)
            
            key_pressed = self.handle_user_keypress()
            if key_pressed == ESC_KEY:
                break

            # Show battery level 
            self.update_battery_level()
            cv2.putText(frame_ret,f"Battery: {self.battery_level}%",(32,664),cv2.FONT_HERSHEY_SIMPLEX,1,(0, 0, 255), thickness=2)
            cv2.imshow(f'Tello Tracking...', frame_ret)

        self.cleanup()  # Clean exit


def main():
    drone = TelloDrone()
    try:
        drone.run(user_interface=True)
    except Exception:
        drone.cleanup()  # Clean (as possible) exit


if __name__ == '__main__':
    main()
