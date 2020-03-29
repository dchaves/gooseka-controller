import logging
import struct
import serial
import time
import json 
import paho.mqtt.client as mqtt
import socket

STATE_SOF_1 = 0x00
STATE_SOF_2 = 0x01
STATE_FRAME = 0x02

SOF_1 = 0xDE
SOF_2 = 0xAD

MAGIC_NUMBER = 0xCA

TELEMETRY_SIZE_BYTES = 30
MOTOR_POLES = 14

logger = logging.getLogger(__name__)

class MySerialComm(object):

    def _on_connect(client, userdata, flags, rc):
        """ The callback for when the client receives a CONNACK response from the server."""
        print('Connected with result code ' + str(rc))
        # client.subscribe(MQTT_TOPIC)

    def _on_message(client, userdata, msg):
        """The callback for when a PUBLISH message is received from the server."""
        # print(msg.topic + '\t' + str(msg.payload.decode('utf-8')))
        pass

    def send_packet(self, duty_left, duty_right):
        """ Send the packet with motor duties """
        message_to_send = struct.pack('<BBBBBBB', SOF_1, SOF_2, duty_left, 0, duty_right, 0, MAGIC_NUMBER)
        self.serial_port.write(message_to_send)

    def receive_telemetry(self):
        """ Receive telemetry """

        telemetry = {}
        
        while (self.serial_port.in_waiting > 0):
            received_byte = struct.unpack('B',self.serial_port.read())[0]
            # logger.info(received_byte)
            if (self.state == STATE_SOF_1):
                # logger.info("SOF_1")
                if (received_byte == SOF_1):
                    self.state = STATE_SOF_2
                    continue
            elif (self.state == STATE_SOF_2):
                # logger.info("SOF_2")
                if (received_byte == SOF_2):
                    self.buffer_index = 0
                    self.buffer = bytearray(TELEMETRY_SIZE_BYTES)
                    self.state = STATE_FRAME
                    continue
                else:
                    self.state = STATE_SOF_1
                    continue
            elif (self.state == STATE_FRAME):
                # logger.info("FRAME")
                if (self.buffer_index < TELEMETRY_SIZE_BYTES - 1):
                    self.buffer[self.buffer_index] = received_byte
                    self.buffer_index += 1
                    continue
                else:
                    self.buffer[self.buffer_index] = received_byte
                    self.state = STATE_SOF_1
                    # print ('SIZE ' + str(struct.calcsize('!LHHHHHBLHHHHHB')))
                    received_list = struct.unpack('<LHHHHHBLHHHHHB',self.buffer)

                    # Sync timestamp with first received telemetry
                    if(self.init_time == 0):
                        self.init_time = int(round(time.time() * 1000)) - received_list[0]

                    telemetry = {
                        "left": {
                            "timestamp": received_list[0] + self.init_time,
                            "temperature": received_list[1],
                            "voltage": received_list[2],
                            "current": received_list[3],
                            "power": received_list[4],
                            "erpm": received_list[5],
                            "duty": received_list[6]
                        },
                        "right": {
                            "timestamp": received_list[7] + self.init_time,
                            "temperature": received_list[8],
                            "voltage": received_list[9],
                            "current": received_list[10],
                            "power": received_list[11],
                            "erpm": received_list[12],
                            "duty": received_list[13]
                        }
                    }
                    
                    # Send data to mqtt
                    print("Received: " + json.dumps(telemetry))
                    if(self.mqtt):
                        self.mqtt_client.publish(topic=self.mqtt_topic,payload=json.dumps(telemetry))
                    continue

        return telemetry
                
    def __init__(self, serial_port, serial_rate, radio_idle_timeout, mqtt_address, mqtt_port, mqtt_user, mqtt_pass, mqtt_topic):
        """ Initialization """

        self.init_time = 0
        self.state = STATE_SOF_1
        self.serial_port = serial.Serial(serial_port, serial_rate)
        self.radio_idle_timeout = radio_idle_timeout

        try:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.username_pw_set(mqtt_user, mqtt_pass)
            self.mqtt_client.on_connect = self._on_connect
            self.mqtt_client.on_message = self._on_message
            self.mqtt_topic = mqtt_topic
            self.mqtt_client.connect(mqtt_address, mqtt_port)
            print("Running with MQTT telemetry")
            self.mqtt = True
            self.mqtt_client.loop_start()
        except socket.gaierror as error:
            print("Running without MQTT telemetry")
            self.mqtt = False
        

