import logging
import threading
import sys

# initiatiing the src module will start the connection with Tello
from src.web_server.server import app

# We only need this for local development.
if __name__ == '__main__':
    print("Running server application...\n")
    logger = logging.getLogger(__name__)
    logger.info("")
    app.run(debug=True, use_reloader=False)  # use_reloader stops it from initialising twice.
