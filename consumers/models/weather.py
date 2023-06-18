"""Contains functionality related to Weather"""
import logging
import json


logger = logging.getLogger(__name__)


class Weather:
    """Defines the Weather model"""

    def __init__(self):
        """Creates the weather model"""
        self.temperature = 70.0
        self.status = "sunny"

    def process_message(self, message):
        """Handles incoming weather data"""
        try:
            print(f"[분석][weather] messge: {message}")
            value = json.loads(message.value())
            print(f"[분석][weather] value: {value}")

            self.temperature = value.get('temperature')
            self.status = value.get('status')
        except Exception as e:
            print(f"[분석][weather] weather 메시지를 파싱하는데 실패하였습니다.")


