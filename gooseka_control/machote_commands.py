import logging
from sqlite3 import Timestamp
from inputs import get_gamepad
from inputs import devices
from .commands import Commands


logger = logging.getLogger(__name__)

class MachoteCommands(Commands):
    """Gamepad controller"""
    last_telemetry = {"left": {"timestamp": 0}}

    def get_command(self, telemetry):
        """Obtain the list of commands from the gamepad

        Keyword arguments:
        telemetry -- dict with telemetry information
        """

        code_list = []
        events = devices.gamepads[0]._do_iter()

        if events is not None:
            for event in events:
                # logger.info("EVENT {}:{}".format(event.code, event.state))
                # print(event.code, event.state)
                if event.code == "ABS_Z":
                    # code_list.append(self._set_duty_left(event.state))
                    # logger.info("LEFT:\t{}".format(event.state))
                    self.linear_duty = event.state
                    
                if event.code == "ABS_RZ":
                    # code_list.append(self._set_duty_right(event.state))
                    # logger.info("RIGHT:\t{}".format(event.state))
                    # self.angular_duty = event.state
                    # changed = True
                    pass

                if event.code == "ABS_X":
                    # self.angular_duty = event.state
                    # changed = True
                    pass

                if event.code == "BTN_DPAD_LEFT":
                    # event.state == 1 MEANS PUSHED
                    # event.state == 0 MEANS RELEASED
                    pass

                if event.code == "BTN_DPAD_RIGHT":
                    # event.state == 1 MEANS PUSHED
                    # event.state == 0 MEANS RELEASED
                    pass

        if "left" in telemetry:
            # logger.info(telemetry)
            logger.info(
                "LINEAR: {:>3}\tANGULAR: {:>3}".format(int(self.linear_duty), int(self.angular_duty))
            )

            # TODO DELETE ME
            self.angular_duty = 128 # ALWAYS STRAIGTH
            # END TODO
            code_list.append(self._set_duty_linear(self.linear_duty))
            code_list.append(self._set_duty_angular(self.angular_duty))
        return code_list

    def __init__(self, config):
        """Initialization"""

        super(MachoteCommands, self).__init__(config)
        self.linear_duty = 0
        self.angular_duty = 0
