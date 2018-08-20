import datetime
import logging


def get_time_now():
    return datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


# def get_logger(name):
#     server_logger = logging.getLogger(name)  # __name__ reflects the name this module
#     server_logger.setLevel(logging.INFO)
#
#     # handler = logging.FileHandler("logs/{}.log".format(get_time_now()))
#     handler.setLevel(logging.INFO)
#     handler.setFormatter(logging.Formatter("('%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
#
#     server_logger.addHandler(handler)
#
#     return server_logger

