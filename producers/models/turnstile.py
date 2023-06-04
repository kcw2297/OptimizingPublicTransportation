import logging
from pathlib import Path

from confluent_kafka import avro

from models.producer import Producer
from models.turnstile_hardware import TurnstileHardware


logger = logging.getLogger(__name__)


class Turnstile(Producer):
    key_schema = avro.load(f"{Path(__file__).parents[0]}/schemas/turnstile_key.json")
    value_schema = avro.load(
        f"{Path(__file__).parents[0]}/schemas/turnstile_value.json"
    )

    def __init__(self, station):
        self.station = station
        self.turnstile_hardware = TurnstileHardware(station)

        STATIONTOPIC = (
            'turnstile_' +
            station.name.lower()
            .replace("/", "_and_")
            .replace(" ", "_")
            .replace("-", "_")
            .replace("'", "")
        )

        super().__init__(
            STATIONTOPIC,
            key_schema=Turnstile.key_schema,
            value_schema=Turnstile.value_schema,
            num_partitions=1,
            num_replicas=1,
        )

    def run(self, timestamp, time_step):

        num_entries = self.turnstile_hardware.get_entries(timestamp, time_step)

        print(f'[분석][turnstile_run] Start Looping num_entries')

        print(f'[분석][turnstile_run] num_entries : {num_entries}')
        print(f'[분석][turnstile_run] station_id : {self.station.station_id}')
        print(f'[분석][turnstile_run] station_name : {self.station.name}')
        print(f'[분석][turnstile_run] self.station.color.name : {self.station.color.name}')
        for _ in range(num_entries):
            self.producer.produce(
                    topic=self.topic_name,
                    key={"timestamp": self.time_millis()},
                    value={
                            "station_id"  : int(self.station.station_id),
                            "station_name": str(self.station.name),
                            "line"        : str(self.station.color.name)
                    },
            )
            print(f'[분석][turnstile_run] {self.station.name} : success produce!!!!!!!!!!')
