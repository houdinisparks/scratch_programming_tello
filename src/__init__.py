import logging
import threading
import traceback

import sys

from src.iot_hub.iot_hub import Tello_Hub
from src.utils.speech_synthesizer import SpeechToText
from src.utils.tello import Tello

# Initialise the root level logger. All subsequent loggers will be the child of this logger,
# and will inherit the settings.

logging.basicConfig(
    stream=sys.stdout,
    format="('%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt='%H:%M:%S',
    level=logging.DEBUG)

# Flask app will use this logger by default in its HTTP requests. Set it to logging.ERROR so that the
# /poll requests and response wont flood the console.
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

CONNECTIONSTRING = "Endpoint=sb://ihsuprodsgres019dednamespace.servicebus.windows.net/;SharedAccessKeyName=iothubowner;SharedAccessKey=mVK4GS/NWWjM6h0OUVMNI8kgmrYnxCuFaNdzFPtDDE4="
PROTOCOL = "mqtt"

# Instantiate the drone and speech classes. Instantiating will auto setup and connect the drone
# and microphone.
# Global Variables.
global tello
global speech_to_text
tello = None
try:
    print("Initializing backend server...\n")
    speech_to_text = SpeechToText(threshold=900, engine="google")  # noisier background -> higher threshold
    tello = Tello("192.168.10.2", 8888, imperial=False, command_timeout=0.3)
    tello.init_connection()
    # hub = Tello_Hub(CONNECTIONSTRING,PROTOCOL)
    # hub.start_tello_updates_to_hub_thread()

    import atexit
    atexit.register(tello.__del__)

except OSError as e:
    logging.warning("Tello is not connected. Please connect to the tello by pressing 'c' in the Scratch window.")

except RuntimeError as e:
    logging.warning(str(e))

except Exception as e:
    logging.error("Exception Occurred: {}".format(traceback.format_exc()))
