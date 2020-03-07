import logging
import scipy.stats
import random
from math import exp

logger = logging.getLogger(__name__)


class FakeComm(object):

    def _get_voltage(self, power):

        voltage_noise = random.random()

        voltage = (self.mptt_max/2.0) * exp((self.duty_left + self.duty_right)/512.0) #+ voltage_noise
        return voltage
        

        
    def send_packet(self, duty_left, duty_right):
        """ Send the packet with motor duties """

        self.duty_left = duty_left
        self.duty_right = duty_right

    def receive_telemmetry(self):
        """ Receive telemetry """

        total_duty = self.duty_left + self.duty_right
        prob = self.mptt_dist.pdf(total_duty)
        panel_power = self.mptt_max * prob

            
        voltage = self._get_voltage(panel_power)
        current_prob = random.random()
        current_left = (1.0  *panel_power)/voltage * current_prob
        current_right = (1.0 *panel_power)/voltage - current_left

        logger.info("MAX_POWER {} CUR_POWER {} DUTY {} VOLTAGE {} CURRL {} CURRR {} DUTYL {} DUTYR {}".format(
            self.mptt_dist.pdf(180)* 50,
            panel_power, total_duty, voltage,
            current_left,
            current_right,
            self.duty_left,
            self.duty_right))
  
        
        telemetry = {
            "left": {
                "timestamp": 125,
                "temperature": 45,
                "voltage": voltage,
                "current": current_left,
                "power": 559,
                "erpm": 299,
                "duty": 25,
            },
            "right": {
                "timestamp": 125,
                "temperature": 45,
                "voltage": voltage,
                "current": current_right,
                "power": 440,
                "erpm": 325,
                "duty": 35,
            }}

        return telemetry

    def __init__(self, serial_port, serial_rate, radio_idle_timeout):
        """ Initialization """

        self.duty_left = 0
        self.duty_right = 0

        self.mptt_dist = scipy.stats.norm(180, 80)
        self.mptt_max = 50

        
        

                                      

