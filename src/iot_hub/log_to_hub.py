#
# from src.web_server.server import tello
#
#
# def get_battery():
#     tello.get_battery()

import json
import logging
from datetime import time

from src import tello
from src.iot_hub.iot_hub import Tello_Hub

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# todo: async thread to log updates to iot hub
def send_updates_to_hub():
    connection_string = "Endpoint=sb://ihsuprodsgres019dednamespace.servicebus.windows.net/;SharedAccessKeyName=iothubowner;SharedAccessKey=mVK4GS/NWWjM6h0OUVMNI8kgmrYnxCuFaNdzFPtDDE4="
    protocol = "mqtt"
    iothub = Tello_Hub(connection_string,protocol)

    while True:
        logger.info("Sending tello updates to Azure IoT Hub")
        time.sleep(10)

        msg = {"deviceId": tello.id,
               "speed": tello.speed,
               "flight_time": tello.flight_time,
               "battery": tello.battery}

        iothub.sendMessageToHub(json.dump(msg))
