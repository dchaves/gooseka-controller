import logging
from inputs import get_gamepad
from inputs import devices
from .commands import Commands


logger = logging.getLogger(__name__)


class MachoteCommands(Commands):
    """Gamepad controller"""

    def get_command(self, telemetry):
        """Obtain the list of commands from the gamepad

        Keyword arguments:
        telemetry -- dict with telemetry information
        """

        code_list = []
        events = devices.gamepads[0]._do_iter()
        changed = False

        if events is not None:
            for event in events:
                # logger.info("EVENT {}:{}".format(event.code, event.state))
                # print(event.code, event.state)
                if event.code == "ABS_Z":
                    # code_list.append(self._set_duty_left(event.state))
                    # logger.info("LEFT:\t{}".format(event.state))
                    self.linear_velocity = event.state
                    changed = True
                if event.code == "ABS_RZ":
                    # code_list.append(self._set_duty_right(event.state))
                    # logger.info("RIGHT:\t{}".format(event.state))
                    self.angular_velocity = event.state
                    changed = True

                if event.code == "ABS_X":
                    self.angular_velocity = event.state
                    changed = True

        if changed:
            logger.info(
                "LEFT: {:>3}\tRIGHT: {:>3}".format(int(self.left), int(self.right))
            )
            code_list.append(self._set_duty_lineal(self.linear_velocity))
            code_list.append(self._set_angular_velocity(self.angular_velocity))
        return code_list

    def __init__(self, config):
        """Initialization"""

        super(MachoteCommands, self).__init__(config)
        self.linear_velocity = 0
        self.angular_velocity = 0
