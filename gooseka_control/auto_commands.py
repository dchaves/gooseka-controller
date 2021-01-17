import logging
import math
import os
import re
from inputs import get_gamepad
from inputs import devices
from .commands import Commands

STATE_STOP = 0x00
STATE_STARTING = 0x01
STATE_MAXPOWER = 0x02

# State machine diagram https://docs.google.com/drawings/d/1Mk_Xc0m1AX4f9dR5dXItTYfNQN611EUfX3osR9mFplU/edit
BTN_A = "BTN_SOUTH"
BTN_B = "BTN_EAST"
BTN_Y = "BTN_NORTH"

logger = logging.getLogger(__name__)

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
                # print(event.code)
                if (self.state == STATE_STOP):
                    code_list = self.state_stop(telemetry, event.code, event.state)
                elif (self.state == STATE_STARTING):
                    code_list = self.state_starting(telemetry, event.code, event.state)
                elif (self.state == STATE_MAXPOWER):
                    code_list = self.state_maxpower(telemetry, event.code, event.state)

        return code_list
    
    def get_starting_command(self, telemetry, code, state):
        code_list = []
                
        if (code == "ABS_X"):
            if abs(state - self.last_X) < 5:
                pass
            else:
                self.last_X = state
                self.steering = (state - 128) / 128.0 # Input Range: [0,255]; Output range: [-1,1]
        if (code == "ABS_RZ"):
            if abs(state - self.last_Z) < 5:
                pass
            else:
                self.last_Z = state
                self.throttle = state # Input Range: [0,255]; Output range: [0,255]

        duty_left = self.throttle * min(1, (1 + self.steering))
        duty_right = self.throttle * min(1, (1 - self.steering))

        duty_left += (duty_left - telemetry["left"]["duty"]) * self.duty_smoothing_factor
        duty_right += (duty_right - telemetry["right"]["duty"]) * self.duty_smoothing_factor

        logger.info("LEFT: {:>3}\tRIGHT: {:>3}".format(int(round(duty_left)), int(round(duty_right))))

        code_list.append(self._set_duty_left(round(duty_left)))
        code_list.append(self._set_duty_right(round(duty_right)))
        return code_list

    def get_maxpower_command(self, telemetry, code, state):
        code_list = []
                
        if (code == "ABS_X"):
            if abs(state - self.last_X) < 5:
                pass
            else:
                self.last_X = state
                self.steering = (state - 128) / 128.0 # Input Range: [0,255]; Output range: [-1,1]
        self.throttle = 255 # Input Range: [0,255]; Output range: [0,255]

        duty_left = self.throttle * min(1, (1 + self.steering))
        duty_right = self.throttle * min(1, (1 - self.steering))

        duty_left += (duty_left - telemetry["left"]["duty"]) * self.duty_smoothing_factor
        duty_right += (duty_right - telemetry["right"]["duty"]) * self.duty_smoothing_factor

        logger.info("LEFT: {:>3}\tRIGHT: {:>3}".format(int(round(duty_left)), int(round(duty_right))))

        code_list.append(self._set_duty_left(round(duty_left)))
        code_list.append(self._set_duty_right(round(duty_right)))
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
            return
        code_list.append(self._set_duty_left(0))
        code_list.append(self._set_duty_right(0))
        return code_list

    def state_starting(self, telemetry, code, state):
        code_list = []
        if (code == BTN_B):
            self.set_led(0x02)
            self.state = STATE_MAXPOWER
            print("STATE MAXPOWER")
            return
        if (code == BTN_Y):
            self.set_led(0x00)
            self.state = STATE_STOP
            print("STATE STOP")
            return
        return self.get_starting_command(telemetry, code, state)

    def state_maxpower(self, telemetry, code, state):
        code_list = []
        if (code == BTN_A):
            self.set_led(0x01)
            self.state = STATE_STARTING
            print("STATE STARTING")
            return
        if (state == BTN_Y):
            self.set_led(0x00)
            self.state = STATE_STOP
            print("STATE STOP")
            return
        return self.get_maxpower_command(telemetry, code, state)

    def __init__(self, config):
        """ Initialization """
        
        super(AutoCommands, self).__init__(config)
        self.steering = 0
        self.throttle = 0
        self.last_X = 128
        self.last_Z = 0
        self.duty_smoothing_factor = 0.8

        self.set_led(0x00)
