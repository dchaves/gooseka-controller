import logging
import scipy.stats
import random
import numpy as np
from math import exp
from .utils import millis

logger = logging.getLogger(__name__)


class FakeComm(object):

    def _get_voltage(self, power):

        voltage_noise = random.random()

        voltage = ((self.mptt_max/2.0) * exp((self.duty_left + self.duty_right)/512.0) +
                   voltage_noise)
        return voltage
        
    def send_packet(self, duty_left, duty_right):
        """ Send the packet with motor duties """

        self.duty_left = duty_left
        self.duty_right = duty_right

    def receive_telemetry(self):
        """ Receive telemetry """

        total_duty = self.duty_left + self.duty_right
        prob = self.mptt_dist.pdf(total_duty)
        panel_power = self.mptt_max * prob

            
        voltage = self._get_voltage(panel_power)
        current_prob = random.random()
        current_left = (1.0  *panel_power)/voltage * current_prob
        current_right = (1.0 *panel_power)/voltage - current_left

        erpm_left = panel_power + random.random()
        erpm_right = panel_power + random.random()

        logger.info("MAX_POWER {} CUR_POWER {} DUTY {} VOLTAGE {} CURRL {} CURRR {} DUTYL {} DUTYR {}".format(
            self.mptt_dist.pdf(self.mu) * self.mptt_max,
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
                "erpm": erpm_left,
                "duty": 25,
            },
            "right": {
                "timestamp": 125,
                "temperature": 45,
                "voltage": voltage,
                "current": current_right,
                "power": 440,
                "erpm": erpm_right,
                "duty": 35,
            }}

        if millis() - self.now > self.change_every_ms:

            self.mu = np.random.uniform(100, 300)
            self.sigma = np.random.uniform(100, 500)
            
            self.mptt_dist = scipy.stats.norm(self.mu, self.sigma)
            self.now = millis()
        
        return telemetry

    def __init__(self, serial_port, serial_rate, radio_idle_timeout,
                 mqtt_address, mqtt_port, mqtt_user, mqtt_pass, mqtt_topic):
        """ Initialization """

        self.duty_left = 0
        self.duty_right = 0        
        self.mu = 180
        self.sigma = 200

        self.mptt_dist = scipy.stats.norm(self.mu, self.sigma)
        self.mptt_max = 500
        
        self.now = millis()

        self.change_every_ms = 30000
