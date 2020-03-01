
class FakeComm(object):

    def send_packet(self, duty_left, duty_right):
        """ Send the packet with motor duties """

        pass

    def receive_telemmetry(self):
        """ Receive telemetry """

        telemetry = {
            "left": {
                "timestamp": 125,
                "temperature": 45,
                "voltage": 21,
                "current": 5,
                "power": 559,
                "erpm": 299,
                "duty": 25,
            },
            "right": {
                "timestamp": 125,
                "temperature": 45,
                "voltage": 18,
                "current": 19,
                "power": 440,
                "erpm": 325,
                "duty": 35,
            }}

        return telemetry

    def __init__(self, serial_port, serial_rate, radio_idle_timeout):
        """ Initialization """

        pass
    

