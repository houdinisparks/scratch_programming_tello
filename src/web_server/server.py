# socket programming
import logging
import traceback

from flask import Flask
from src import tello, speech_to_text

host = 'localhost'
port = 5000
locaddr = (host, port)

# Create a logger for server.py
server_logger = logging.getLogger(__name__)

app = Flask(__name__)

global tello

@app.route("/poll")
def poll():
    """
    Sends back drone battery, flight time and speed.
    :return:
    """
    if tello.state != "disconnected":
        return "battery {}\n".format(tello.battery) + \
               "speed {}\n".format(tello.speed) + \
               "flight_time {}\n".format(tello.flight_time) + \
               "mic_state {}\n".format(speech_to_text.state) + \
               "tello_state {}".format(tello.state)

    else:
        resp = "tello disconnected. please connect tello and press 'c'"
        return "battery {}\n".format(resp) + \
               "speed {}\n".format(resp) + \
               "flight_time {}\n".format(resp) + \
               "mic_state {}\n".format(speech_to_text.state) + \
               "tello_state {}".format(resp)

    # return "ok"


@app.route("/mic")
def begin_mic():
    server_logger.info("received command {}, "
                       "translating to text.".format("mic"))
    success = False
    translated_text = "error"
    while not success:
        try:
            audio = speech_to_text.wait_for_speech_input()
            translated_text = speech_to_text.process_speech(audio)
            success = True

        except Exception:
            server_logger.info(server_logger.info("S2Text: {}".format(speech_to_text.state)))

    server_logger.info("sending result {} back to scratch"
                       .format(translated_text))

    return translated_text

@app.route("/connect_tello")
def connect_tello():
    global tello

    try:
        tello.init_connection()

    except RuntimeError as e:
        logging.error(traceback.format_exc())

    except OSError as e:
        # tello.socket.close()
        logging.error("Connection failed. Exception caught {}".format(traceback.format_exc()))

    return "ok"



@app.route("/takeoff")
def takeoff():
    tello.takeoff()
    return "ok"


@app.route("/land")
def land():
    tello.land()
    return "ok"


@app.route("/up/<distance>")
def up(distance):
    tello.move_up(distance)
    return "ok"


@app.route("/down/<distance>")
def down(distance):
    tello.move_down(distance)
    return "ok"


@app.route("/left/<distance>")
def left(distance):
    """
    # /<command>/<parameters - (stack block) processed and forwarded to drone
    # /<command>/<request_id>/<parameter> (requester block)
    :param distance:
    :return:
    """
    tello.move_left(distance)
    return "ok"


@app.route("/right/<distance>")
def right(distance):
    tello.move_right(distance)
    return "ok"


@app.route("/forward/<distance>")
def forward(distance):
    tello.move_forward(distance)
    return "ok"


@app.route("/back/<distance>")
def back(distance):
    # server_logger.debug("received from scratch")
    tello.move_backward(distance)
    return "ok"


@app.route("/cw/<angle>")
def cw(angle):
    tello.rotate_cw(angle)
    return "ok"


@app.route("/ccw/<angle>")
def ccw(angle):
    tello.rotate_ccw(angle)
    return "ok"


@app.route("/flip/<direction>")
def flip(direction):
    direction.strip()
    tello.flip(direction)
    return "ok"


@app.route("/setspeed/<speed>")
def speed(speed=5):
    tello.set_speed(speed)
    return "ok"


@app.route('/crossdomain.xml')
def flash_request():
    cross_domain_policy = "<cross-domain-policy>" + \
                          "<allow-access-from domain='*' to-ports='{}'/>".format(port) + \
                          "</cross-domain-policy>\x00"

    return cross_domain_policy


@app.route("/reset_all")
def reset_all():
    # tello.land()
    return "ok"
    # pass

# @app.after_request
# def apply_headers(response):
#     return response.data
# print(response)
# if response:
#     response.headers[]

# @app.route("/kinect/<state>")
# def kinect(state="off"):
#     # activate the kinect connection to the drone.
#     pass

# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.bind(locaddr)

# while True:
#     try:
#         msg = input("");
#
#         if not msg:
#             break
#
#         if 'end' in msg:
#             print('...')
#             sock.close()
#             break
#
#         # Send data
#         msg = msg.encode(encoding="utf-8")
#         sent = sock.sendto(msg, )
#     except KeyboardInterrupt:
#         print('\n . . .\n')
#         sock.close()
#         break

# # an async thread to process anything received on this socket.
# def processor():
#     while True:
#         try:
#             data, server = sock.recvfrom(1518)
#             cmd_received = data.decode(encoding="utf-8")
#
#             if cmd_received != "speechcommand":
#                 server_logger.info("received command {}, "
#                                    "forwarding to drone.".format(cmd_received))
#                 cmd_to_sent = tello.processCommands(cmd_received)
#
#                 # Send data
#                 cmd_to_sent = cmd_to_sent.encode(encoding="utf-8")
#                 sent = sock.sendto(cmd_to_sent, tello.tello_ip, tello.tello_port)
#
#             else:
#                 server_logger.info("received command {}, "
#                                    "translating to text.".format(cmd_received))
#
#                 audio = speech_to_text.wait_for_speech_input()
#                 translated_text = speech_to_text.process_speech(audio)
#
#                 server_logger.info("sending result {} back to scratch"
#                                    .format(translated_text))
#
#
#         except Exception as e:
#             server_logger.error("Exception occurred.", exc_info=True)
#             server_logger.info('\nExit . . .\n')
#             break


# # Create async thread to receive and send messages to tello.
# processorThread = threading.Thread(target=processor)
# processorThread.start()
