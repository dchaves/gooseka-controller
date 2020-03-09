import numpy as np
import logging
from inputs import get_gamepad
from inputs import devices
from .commands import Commands
from .utils import millis
from .mptt import MPTT
from .pid import PID

logger = logging.getLogger(__name__)

class GoosekaCommands(Commands):
    """ Gamepad controller """
    
    def _get_acceleration(self, value):
        """ Returns acceleration using the value of the button 

        Keyword Arguments:
        value -- value of the button
        
        """        
        return value * self.config["FF_GAIN"]

    def _get_decceleration(self, value):
        """ Returns decceleration using the value of the button

        Keyword Arguments:
        value -- value of the button
        
        """
        return value * self.config["FF_GAIN"]

    def _filter_duty_slew_rate(self, duty, past_duty):
        """ Filter duty using slew rate to avoid brownouts 

        Keywored arguments:
        duty -- target duty
        past_duty -- current duty

        """

        if "MOT_SLEWRATE" in self.config and self.config["MOT_SLEWRATE"] > 0:
            if abs(duty - past_duty) > (
                    (self.config["MAX_DUTY"] - self.config["MIN_DUTY"]) *
                    (1.0/self.config["MOT_SLEWRATE"]) * self.config["LOOP_CONTROL_MS"]/1000.0):

                if duty - past_duty > 0:
                    return past_duty + (
                        (self.config["MAX_DUTY"] - self.config["MIN_DUTY"]) *
                        (1.0/self.config["MOT_SLEWRATE"]) * self.config["LOOP_CONTROL_MS"]/1000.0)

                else:
                    return past_duty - (
                        (self.config["MAX_DUTY"] - self.config["MIN_DUTY"]) *
                        (1.0/self.config["MOT_SLEWRATE"]) * self.config["LOOP_CONTROL_MS"]/1000.0)
        return duty
    
    def _execute_loop_control(self, telemetry, execute_mptt):
        """ Execute the loop control 

        Keyword arguments:
        telemetry -- dict with telemetry information
        execute_mptt -- true if mptt should be calculated

        """        
        current_millis = millis()
        if (current_millis - self.last_control_ms >
            self.config["LOOP_CONTROL_MS"]):
            
            if "left" in telemetry and "right" in telemetry:
                # Get linear velocity
                
                self.current_linear_speed = (telemetry["left"]["erpm"] +
                                             telemetry["right"]["erpm"])/2.0
                
                self.linear_error = self.ideal_linear_speed - self.current_linear_speed
                linear_value = self.linear_pid.step(self.linear_error, 1)

                # get angular velocity
                self.current_angular_speed = (telemetry["left"]["erpm"] -
                                              telemetry["right"]["erpm"])

                self.angular_error = self.ideal_angular_speed - self.current_angular_speed
                angular_value = self.angular_pid.step(self.angular_error, 1)
                
                
                logger.info("IDEAL {} CURRENT {} ERROR {}".format(self.ideal_linear_speed, self.current_linear_speed, self.linear_error))
                
                target_left = linear_value + angular_value
                target_right = linear_value - angular_value

                logger.info("PRESLEW {} {}".format(target_left, target_right))
                
                target_left = self._filter_duty_slew_rate(target_left, self.duty_left)
                target_right = self._filter_duty_slew_rate(target_right, self.duty_right)

                logger.info("TARGETSLEW {} {}".format(target_left, target_right))
                
                if execute_mptt:
                    logger.info("Executing MPTT")
                    # FIXME mptt duty should be modified here
                    total_duty = self.mptt.step(telemetry, self.duty_left + self.duty_left)

                    logger.info("Executing MPTT {} {}".format(total_duty, self.duty_left + self.duty_right))
                    
                    if total_duty < target_left + target_right:
                        new_target_left = ((1.0 * target_left) / (target_left + target_right)) * total_duty
                        new_target_right = ((1.0 * target_right) / (target_left + target_right)) * total_duty

                        target_left = new_target_left
                        target_right = new_target_right
                        
                        logger.info("LEFT {} RIGHT {}".format(
                            target_left,
                            target_right))

                # limit duty to the maximum/minimum accepted
                target_left = np.clip(target_left, self.config["MIN_DUTY"],
                                    self.config["MAX_DUTY"])

                target_right = np.clip(target_right, self.config["MIN_DUTY"],
                                     self.config["MAX_DUTY"])

                logger.info("TARGET LEFT {} RIGHT {}".format(target_left, target_right))
                    
                self.duty_left = target_left
                self.duty_right = target_right

                self.last_control_ms = current_millis
                     
    def get_command(self, telemetry):
        """ Obtain the list of commands from the gamepad 

        Keyword arguments:
        telemetry -- dict with telemetry information
        """
        
        code_list = []

        # Enable mptt if running (it will be disable under specific conditions)
        if self.is_running:
            mptt_flag = True
        else:
            mptt_flag = False
        
        events = devices.gamepads[0]._do_iter()
        if events is not None:            
            for event in events:
                logger.info("EVENT {}:{}".format(event.code, event.state))
                # print(event.code, event.state)
                if (event.code == "ABS_Y"):
                    # Initially using a button to accelerate
                    self.last_button_event = event.state
                    
                elif (event.code == "ABS_RZ"):
                    # decceleration

                    self.last_button_event = -event.state
                    
                    # reset mptt
                    self.mptt.reset()
                    mptt_flag = False

                elif (event.code == "BTN_THUMB2"):
                    # Change state to running state
                    
                    self.is_running = True
                    # reset mptt
                    self.last_button_event = None
                    self.mptt.reset()

                elif (event.code == "BTN_THUMB"):
                    # change state to stop state
                    self.is_running = False
                    # reset mptt
                    self.mptt.reset()
                    mptt_flag = False

                        
        if not self.is_running:
            # Maximum deceleration
            self.ideal_linear_speed = max(
                0, self.current_linear_speed -
                self._get_acceleration(self.config["FF_MAX_ACC"]))

        elif (self.last_button_event is None or
              (self.last_button_event < self.config["HIST_FF"]) and
              (self.last_button_event > - self.config["HIST_FF"])):
            self.ideal_linear_speed = max(
                0, self.current_linear_speed +
                self._get_acceleration(self.config["FF_MAX_ACC"]))
        else:
            self.ideal_linear_speed = max(0, self.current_linear_speed +
                                          self._get_acceleration(self.last_button_event))
            
            
            logger.info("MANUAL")
                        
        self._execute_loop_control(telemetry, execute_mptt=mptt_flag)

        code_list.append(self._set_duty_left(self.duty_left))
        code_list.append(self._set_duty_right(self.duty_right))

        #logger.info("LINEAR CURR {}: IDEAL {} ERROR {}".format(
        #    self.current_linear_speed, self.ideal_linear_speed, self.linear_error))

        #logger.info("DUTY LEFT {} RIGHT {}".format(self.duty_left, self.duty_left))

        return code_list

    def __init__(self, config):
        """ Initialization """

        super(GoosekaCommands, self).__init__(config)

        self.last_button_event = None
        
        self.is_running = False

        self.mptt = MPTT(PID(self.config["MPTT_KP"],
                             self.config["MPTT_KD"],
                             self.config["MPTT_KI"],
                             self.config["MPTT_MAX_I"]))
        
        self.last_control_ms = 0

        self.linear_error = 0
        self.duty_left = 0
        self.duty_right = 0

        self.current_linear_speed = 0
        self.ideal_linear_speed = 0

        self.current_angular_speed = 0
        self.ideal_angular_speed = 0
        self.angular_error = 0

        self.linear_pid = PID(self.config["LINEAR_KP"],
                              self.config["LINEAR_KD"],
                              self.config["LINEAR_KI"],
                              self.config["LINEAR_MAX_I"])

        self.angular_pid = PID(self.config["ANGULAR_KP"],
                               self.config["ANGULAR_KD"],
                               self.config["ANGULAR_KI"],
                               self.config["ANGULAR_MAX_I"])

        
