import logging
from inputs import get_gamepad
from inputs import devices
from .commands import Commands
from .utils import millis
from .pid import PID

logger = logging.getLogger(__name__)

class GoosekaCommands(Commands):
    """ Gamepad controller """
    
    def _get_acceleration(self, value):
        """ Returns acceleration using the value of the button 

        Keyword Arguments:
        value -- value of the button
        
        """
        
        return value


    def _get_decceleration(self, value):
        """ Returns decceleration using the value of the button

        Keyword Arguments:
        value -- value of the button
        
        """
        return value
    
    def _execute_loop_control(self, telemetry):
        """ Execute the loop control 

        Keyword arguments:
        telemetry -- dict with telemetry information

        """

        current_millis = millis()

        if (current_millis - self.last_control_ms >
            self.config["LOOP_CONTROL_MS"]):
            
            if "left" in telemetry and "right" in telemetry:
                self.current_linear_speed = (telemetry["left"]["erpm"] +
                                             telemetry["right"]["erpm"])/2.0
                
                self.linear_error = self.ideal_linear_speed - self.current_linear_speed
                linear_value = self.linear_pid.step(self.linear_error, 1)

                self.duty_left = linear_value
                self.duty_left = linear_value

                self.last_control_ms = current_millis
                
    
    def get_command(self, telemetry):
        """ Obtain the list of commands from the gamepad 

        Keyword arguments:
        telemetry -- dict with telemetry information
        """
        
        code_list = []

        logger.info("GET COMMAND ")

        events = devices.gamepads[0]._do_iter()
        logger.info("REC COMMAND ")
        if events is not None:
            
            for event in events:
                logger.info("EVENT {}:{}".format(event.code, event.state))
                # print(event.code, event.state)
                if (event.code == "ABS_Y"):
                    # Initially using a button to accelerate
                    logger.info("ACC")
                    self.ideal_linear_speed = (self.current_linear_speed +
                                               self._get_acceleration(event.state))

                elif (event.code == "ABS_RZ"):
                    # decceleration

                    logger.info("DCC")
                    self.ideal_linear_speed = max(0, self.current_linear_speed -
                                                  self._get_acceleration(event.state))

        self._execute_loop_control(telemetry)

        code_list.append(self._set_duty_left(self.duty_left))
        code_list.append(self._set_duty_right(self.duty_right))

        logger.info("LINEAR CURR {}: IDEAL {} ERROR {}".format(self.current_linear_speed, self.ideal_linear_speed, self.linear_error))

        logger.info("DUTY LEFT {} RIGHT {}".format(self.duty_left, self.duty_left))

        return code_list

    def __init__(self, config):
        """ Initialization """

        super(GoosekaCommands, self).__init__(config)
        self.last_control_ms = 0

        self.linear_error = 0
        self.duty_left = 0
        self.duty_right = 0

        self.current_linear_speed = 0
        self.ideal_linear_speed = 0
        self.ideal_angular_speed = 0

        self.linear_pid = PID(self.config["LINEAR_KP"],
                              self.config["LINEAR_KD"],
                              self.config["LINEAR_KI"],
                              self.config["LINEAR_MAX_I"])
