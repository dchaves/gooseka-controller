import os
import logging
from time import sleep
import numpy as np

logger = logging.getLogger(__name__)

print("Using command module: " + os.environ.get("GOOSEKA"))
if os.environ.get("GOOSEKA") == "BENCHY":
    from .benchy_commands import BenchyCommands as Commands
elif os.environ.get("GOOSEKA") == "MACHOTE":
    from .machote_commands import MachoteCommands as Commands
else:
    from .manual_commands import ManualCommands as Commands

    # print("Using command module: MANUAL")
from .commands import CommandCodes

if os.environ.get("DISABLE_SERIAL"):
    from .fake_io import FakeComm as MySerialComm

    print("Serial is DISABLED")
else:
    from .io import MySerialComm

    print("Serial is ENABLED")


class FSM_Controller(object):
    def loop(self):
        """Main loop"""

        command = Commands(self.config)

        serial_communication = MySerialComm(
            self.config["SERIAL_PORT"],
            self.config["SERIAL_RATE"],
            self.config["RADIO_IDLE_TIMEOUT"],
            self.config["MQTT_ADDRESS"],
            self.config["MQTT_PORT"],
            self.config["MQTT_USER"],
            self.config["MQTT_PASSWORD"],
            self.config["MQTT_TOPIC"],
        )
        last_duty_lineal = -1
        last_angular_velocity = -1
        duty_lineal = 0
        angular_velocity = 0

        telemetry = {}

        while 1:
            command_list = command.get_command(telemetry)

            # set duty with commands
            for _command in command_list:
                if _command[0] == CommandCodes.DUTY_LINEAL:
                    duty_lineal = _command[1]

                elif _command[0] == CommandCodes.ANGULAR_VELOCITY:
                    angular_velocity = _command[1]

            # Only send commands if something has changed
            if len(command_list) > 0:

                # limit duty to the maximum/minimum accepted
                duty_lineal = int(
                    np.clip(
                        duty_lineal, self.config["MIN_DUTY"], self.config["MAX_DUTY"]
                    )
                )

                # only send the packet if duty/angular velocity has changed
                if (
                    last_duty_lineal != duty_lineal
                    or last_angular_velocity != angular_velocity
                ):

                    serial_communication.send_packet(duty_lineal, angular_velocity)

                    last_duty_lineal = duty_lineal
                    angular_velocity = angular_velocity

            telemetry = serial_communication.receive_telemetry()
            # logger.info("LOOPS");
            # sleep(0.01)

    def __init__(self, config):
        """Initialization"""

        self.config = config
