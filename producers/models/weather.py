import json
import logging
import random
import urllib.parse
import requests

from enum import IntEnum
from pathlib import Path
from models.producer import Producer


logger = logging.getLogger(__name__)


# [수정] 중복 코드 DRY, 생성자 안의 로직 분리
class Weather(Producer):
    status = IntEnum(
        "status", "sunny partly_cloudy cloudy windy precipitation", start=0
    )
    rest_proxy_url = "http://localhost:8082"
    key_schema = None
    value_schema = None
    winter_months = set((0, 1, 2, 3, 10, 11))
    summer_months = set((6, 7, 8))
    WEATHERTOPIC = "weather"

    def __init__(self, month):
        self.status = Weather.status.sunny
        self.temp = 70.0
        
        if month in Weather.winter_months:
            self.temp = 40.0
        elif month in Weather.summer_months:
            self.temp = 85.0

        if Weather.key_schema is None:
            with open(f"{Path(__file__).parents[0]}/schemas/weather_key.json") as f:
                Weather.key_schema = json.load(f)


        if Weather.value_schema is None:
            with open(f"{Path(__file__).parents[0]}/schemas/weather_value.json") as f:
                Weather.value_schema = json.load(f)

        super().__init__(
            Weather.WEATHERTOPIC,
            key_schema=Weather.key_schema,
            value_schema=Weather.value_schema,
            num_partitions=1,
            num_replicas=1,
        )

    def _set_weather(self, month):
        mode = 0.0
        if month in Weather.winter_months:
            mode = -1.0
        elif month in Weather.summer_months:
            mode = 1.0
        self.temp += min(max(-20.0, random.triangular(-10.0, 10.0, mode)), 100.0)
        print(f'[분석][_set_weather] self.temp: {self.temp}')
        self.status = random.choice(list(Weather.status))

    def run(self, month):
        self._set_weather(month)

        resp = requests.post(
            f"{Weather.rest_proxy_url}/topics/{self.topic_name}",
            headers={"Content-Type": "application/vnd.kafka.avro.v2+json"},
            data=json.dumps(
                {
                    "key_schema": json.dumps(self.key_schema),
                    "value_schema": json.dumps(self.value_schema),
                    "records": [
                        {
                            "key": {"timestamp": self.time_millis()},
                            "value": {
                                "temperature": int(self.temp),
                                "status": str(self.status.name),
                            },
                        }
                    ],
                }
            ),
        )

        try :
            resp.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(f"HTTP request failed: {err}")
