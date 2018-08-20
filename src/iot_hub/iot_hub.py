# uses amqp protocol to send status updates of dji tello to iot hub
# asynchronous thread
# references: https://github.com/Azure-Samples/iot-hub-python-raspberrypi-client-app/blob/master/app.py
import json
import logging
import threading
import traceback
from datetime import time

from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError, DeviceMethodReturnValue

from src.utils.tello import Tello

logger = logging.getLogger(__name__)

class Tello_Hub:

    def __init__(self, connectionString, protocol , tello):
        self.connectionString = connectionString
        self.protocol = protocol
        self.tello = tello

        if (protocol == "mqtt"):
            self._client = IoTHubClient(self.connectionString,
                                        IoTHubTransportProvider.MQTT)
        else:
            raise Exception("other protocols not supported yet.")

    @property
    def client(self):
        return self._client

    def initConnection(self):
        print("Initializing connection to hub with protocol type: {}"
              .format(self.protocol))

        try:
            self._client = IoTHubClient(self.connectionString,
                                        self.protocol)
            print("Device is connected!")
            self.client.set_message_callback(self.messageReceivedCallback)
            # self.client.set_device_twin_callback(device_twin_callback, TWIN_CONTEXT)
            # self.client.set_device_method_callback(device_method_callback, METHOD_CONTEXT)
            # self.client.set_option("messageTimeout", MESSAGE_TIMEOUT)

            # # IF HTTP PROTOCOL
            # if self.client.protocol == IoTHubTransportProvider.HTTP:
            #     self.client.set_option("timeout", TIMEOUT)
            #     self.client.set_option("MinimumPollingTime", MINIMUM_POLLING_TIME)

            # IF MQTT PROTOCOL
            if self.client.protocol == IoTHubTransportProvider.MQTT:
                # to enable MQTT logging set to 1
                self.client.set_option("logtrace", 1)

        except Exception as e:
            print(traceback.format_exc())

    def messageReceivedCallback(self, message, result, userContext):
        buffer = message.get_bytearray()
        size = len(buffer)
        print("Received Message")
        print("    Data: <<<%s>>> & Size=%d" % (buffer[:size].decode("utf-8"), size))
        map_properties = message.properties()
        key_value_pair = map_properties.get_internals()
        print("    Properties: %s" % key_value_pair)
        return IoTHubMessageDispositionResult.ACCEPTED

    def messageSentCallback(self, message, result, userContext):
        print("Confirmation[%d] received for message with result = %s" % (userContext, result))
        map_properties = message.properties()
        print("    message_id: %s" % message.message_id)
        print("    correlation_id: %s" % message.correlation_id)
        key_value_pair = map_properties.get_internals()
        print("    Properties: %s" % key_value_pair)

    def sendMessageToHub(self, message, properties):
        if not isinstance(message, IoTHubMessage):
            event = IoTHubMessage(bytearray(message, 'utf8'))

        else:
            event = message

        if len(properties) > 0:
            prop_map = event.properties()
            for key in properties:
                prop_map.add_or_update(key, properties[key])

        self.client.send_event_async(
            event, self.messageSentCallback, None)

        # self.client.send_event_async(message, self.messageReceivedCallback,
        #                              None)

    def sendImageToHub(self, filepath, filename):

        try:
            f = open(filepath, "r")
            content = f.read()
            self.client.upload_blob_async(filename, content, len(content),
                                          self.imageUploadCallback, 0)

            print("file upload initiated...")

        except Exception as e:
            print("exception occurred {}".format(traceback.format_exc()))

    def imageUploadCallback(result, userContext):
        if str(result) == "OK":
            print("... image uploaded successfully.")

        else:
            print("... file upload callback returned: " + str(result))

    # def get_battery_life(self):

    def _send_tello_updates_to_hub_thread(self):

        while True:
            logger.info("Sending tello updates to Azure IoT Hub")
            time.sleep(10)

            msg = {"deviceId": self.tello.id,
                   "speed": self.tello.speed,
                   "flight_time": self.tello.flight_time,
                   "battery": self.tello.battery}

            self.sendMessageToHub(json.dump(msg))

    def start_tello_updates_to_hub_thread(self):
        if isinstance(self.tello, Tello):
            self.send_tello_updates_to_hub_thread = threading.Thread(target=self._send_tello_updates_to_hub_thread)
            self.send_tello_updates_to_hub_thread.daemon = True
            self.send_tello_updates_to_hub_thread.start()
        else:
            raise RuntimeError("Drone has not been initialized yet.")

# custom
