# references: https://realpython.com/python-speech-recognition/#how-speech-recognition-works-an-overview
# https://github.com/Uberi/speech_recognition/blob/master/examples/microphone_recognition.py
# used for offline translation, as once once connected to tello, wifi is not available.
import logging
from enum import Enum

import speech_recognition as sr

logger = logging.getLogger(__name__)


class SpeechToText:

    def __init__(self, threshold=3500, engine="google"):
        self._recognizer = sr.Recognizer()
        self._mic = sr.Microphone(device_index=0)
        self._recognizer.dynamic_energy_threshold = False
        self._recognizer.energy_threshold = threshold  # https://github.com/Uberi/speech_recognition/blob/master/reference/library-reference.rst
        self._state = self.State.READY
        self._engine = engine

    class State(Enum):
        READY = 0
        WAITING = 1
        PROCESSING = 2
        ERROR = 3
        MIC_TIMEOUT = 4
        API_TIMEOUT = 5

        def __str__(self):
            state_desc = ""
            if self.value == 0:
                state_desc = "SpeechToText ready, mic has been setup."
            elif self.value == 1:
                state_desc = "Waiting for speech input... please speak into the mic"
            elif self.value == 2:
                state_desc = "Speech detected, sending for translation..."
            elif self.value == 3:
                state_desc = "ERROR: Unable to deciper what you have said, please speak into the mic again."
            elif self.value == 4:
                state_desc = "Error: Mic listener time out. please speak into the mic again."
            elif self.value == 5:
                state_desc = "ERROR: Unable to contact api, please try again,"

            return state_desc

    # todo: implement an observer design pattern, server as observer listening fr changes in speechtotext state.
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if self._state != value:
            logger.info(str(value))
        self._state = value

    @property
    def engine(self):
        return self._engine

    @engine.setter
    def engine(self, value):
        self._engine = value

    @property
    def mic(self):
        return self._mic

    @property
    def recognizer(self):
        return self._recognizer

    def wait_for_speech_input(self):
        audio = None
        try:
            self.state = self.state.WAITING
            with self._mic as source:
                self._recognizer.adjust_for_ambient_noise(source)
                audio = self._recognizer.listen(source, timeout=5.0)
        except sr.WaitTimeoutError:
            self.state = self.state.MIC_TIMEOUT

        except Exception:
            self.state = self.state.ERROR

        return audio

    def process_speech(self, audio):

        msg = ""

        try:
            self.state = self.state.PROCESSING
            if self._engine == "google":
                msg = self.recognizer.recognize_google(audio)

            elif self._engine == "sphinx":
                msg = self.recognizer.recognize_sphinx(audio)

            self.state = self.state.READY
        except sr.UnknownValueError:
            self.state = self.state.ERROR

        except sr.RequestError:
            self.state = self.state.API_TIMEOUT

        return msg
