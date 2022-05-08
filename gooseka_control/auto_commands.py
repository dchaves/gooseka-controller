import logging
import math
import os
import re
from inputs import get_gamepad
from inputs import devices
from .commands import Commands
from .utils import millis

STATE_STOP = 0x00
STATE_STARTING = 0x01
STATE_MAXPOWER = 0x02

# State machine diagram https://docs.google.com/drawings/d/1Mk_Xc0m1AX4f9dR5dXItTYfNQN611EUfX3osR9mFplU/edit
BTN_A = "BTN_SOUTH"
BTN_B = "BTN_EAST"
BTN_Y = "BTN_NORTH"

LIGHT_TURN = 0.1
STANDARD_TURN = 0.25
HARD_TURN = 0.4

logger = logging.getLogger(__name__)

def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

class AutoCommands(Commands):
    """ Gamepad controller """
    state = STATE_STOP

    def get_command(self, telemetry):
        """ Obtain the list of commands from the keyboard 

        Keyword arguments:
        telemetry -- dict with telemetry information
        """
        code_list = []

        events = devices.gamepads[0]._do_iter()

        if events is not None:            
            for event in events:
                # logger.info("CODE: {:12} STATE:{}".format(event.code, event.state))
                if(event.code == "BTN_TL"):
                    self.light_turn_left = (event.state == 1)
                if(event.code == "BTN_TR"):
                    self.light_turn_right = (event.state == 1)
                if((event.code == "BTN_TL2") | (event.code == "BTN_DPAD_LEFT")):
                    self.turn_left = (event.state == 1)
                if((event.code == "BTN_TR2") | (event.code == "BTN_DPAD_RIGHT")) :
                    self.turn_right = (event.state == 1)
                if(event.code == "BTN_DPAD_UP"):
                    self.go_straight = (event.state == 1)

                if (self.state == STATE_STOP):
                    code_list = self.state_stop(telemetry, event.code, event.state)
                elif (self.state == STATE_STARTING):
                    code_list = self.state_starting(telemetry, event.code, event.state)
                elif (self.state == STATE_MAXPOWER):
                    code_list = self.state_maxpower(telemetry, event.code, event.state)

        return code_list

    def constrain(self, value, min, max):
        if(value < min):
            return min
        if(value > max):
            return max
        return value
    
    def calculate_turn(self):
        turn = 0.0

        if(self.light_turn_left & self.turn_left):
            turn = -HARD_TURN
        elif(self.light_turn_right & self.turn_right):
            turn = HARD_TURN
        elif(self.light_turn_left):
            turn = -LIGHT_TURN
        elif(self.light_turn_right):
            turn = LIGHT_TURN
        elif(self.turn_left):
            turn = -STANDARD_TURN
        elif(self.turn_right):
            turn = STANDARD_TURN

        turn = self.constrain(turn, -1.0, 1.0)
        return turn

    def get_starting_command(self, telemetry, code, state):
        code_list = []
        
        self.angular_duty = 128
        if(self.turn_left | self.light_turn_left):
            self.angular_duty = 0
        if(self.turn_right | self.light_turn_right):
            self.angular_duty = 255
        self.linear_duty = 40 if self.go_straight else 0
        logger.info("LINEAR: {:>3}\tANGULAR: {:>3}".format(int(self.linear_duty), int(self.angular_duty)))
        # Send commands
        code_list.append(self._set_duty_angular(self.angular_duty)) # Always starts in a straight line
        code_list.append(self._set_duty_linear(self.linear_duty)) # TODO Change fixed value to adaptive based on telemetry
        return code_list

    def get_maxpower_command(self, telemetry, code, state):
        code_list = []
        
        turning_modifier = self.calculate_turn()
        
        self.angular_duty = int(round(128.0 * (1.0 + turning_modifier)))
        self.linear_duty = 255
        logger.info("LINEAR: {:>3}\tANGULAR: {:>3}".format(int(round(self.linear_duty)), int(round(self.angular_duty))))
        # Send commands
        code_list.append(self._set_duty_linear(self.linear_duty))
        code_list.append(self._set_duty_angular(self.angular_duty))
        return code_list

    def set_led(self, leds):
        files = [f for f in os.listdir('/sys/class/leds/') if re.match(r'.*:sony[1-4]', f)]
        mask = 0x01
        for filename in sorted(files):
            f = open('/sys/class/leds/' + filename + '/brightness','w')
            if (leds & mask):
                f.write("1")
            else:
                f.write("0")
            mask = mask << 1

    def state_stop(self, telemetry, code, state):
        code_list = []
        if (code == BTN_A):
            self.set_led(0x01)
            self.state = STATE_STARTING
            print("STATE STARTING")
        if not "left" in telemetry: # Check if we have received a telemetry message. If not, do not send updated commands.
            return []
        
        if not "left" in telemetry: # Check if we have received a telemetry message. If not, do not send updated commands.
            return []
        self.angular_duty = 128
        self.linear_duty = 0
        logger.info("LINEAR: {:>3}\tANGULAR: {:>3}".format(int(round(self.linear_duty)), int(round(self.angular_duty))))
        code_list.append(self._set_duty_linear(self.linear_duty))
        code_list.append(self._set_duty_angular(self.angular_duty))
        return code_list

    def state_starting(self, telemetry, code, state):
        if (code == BTN_B):
            self.set_led(0x02)
            self.state = STATE_MAXPOWER
            print("STATE MAXPOWER")
        if (code == BTN_Y):
            self.set_led(0x00)
            self.state = STATE_STOP
            print("STATE STOP")
        
        if not "left" in telemetry: # Check if we have received a telemetry message. If not, do not send updated commands.
            return []
        return self.get_starting_command(telemetry, code, state)

    def state_maxpower(self, telemetry, code, state):
        if (code == BTN_A):
            self.set_led(0x01)
            self.state = STATE_STARTING
            print("STATE STARTING")
        if (code == BTN_Y):
            self.set_led(0x00)
            self.state = STATE_STOP
            print("STATE STOP")
        if not "left" in telemetry: # Check if we have received a telemetry message. If not, do not send updated commands.
            return []
        return self.get_maxpower_command(telemetry, code, state)

    def __init__(self, config):
        """ Initialization """
        
        super(AutoCommands, self).__init__(config)
        self.linear_duty = 0
        self.angular_duty = 128
        self.light_turn_right = False
        self.light_turn_left = False
        self.turn_left = False
        self.turn_right = False
        self.go_straight = False
        self.set_led(0x00)
        print("STATE STOP")