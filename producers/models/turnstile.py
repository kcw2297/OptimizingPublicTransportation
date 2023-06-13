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

        TURNSTILETOPIC = 'turnstileRawData'

        super().__init__(
            TURNSTILETOPIC,
            key_schema=Turnstile.key_schema,
            value_schema=Turnstile.value_schema,
            num_partitions=1,
            num_replicas=1,
        )

    def run(self, timestamp, time_step):

        num_entries = self.turnstile_hardware.get_entries(timestamp, time_step)

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
