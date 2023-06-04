"""Methods pertaining to loading and configuring CTA "L" station data."""
import logging
from pathlib import Path
from confluent_kafka import avro
from models import Turnstile
from models.producer import Producer

logger = logging.getLogger(__name__)


# [수정] 생성자 안의 로직 분리
class Station(Producer):
    key_schema = avro.load(f"{Path(__file__).parents[0]}/schemas/arrival_key.json")
    value_schema = avro.load(f"{Path(__file__).parents[0]}/schemas/arrival_value.json")

    def __init__(self, station_id, name, color, direction_a=None, direction_b=None):
        self.name = name
        self.station_id = int(station_id)
        self.color = color
        self.dir_a = direction_a
        self.dir_b = direction_b
        self.a_train = None
        self.b_train = None
        self.turnstile = Turnstile(self)

        STATIONTOPIC = (
            'station_' +
            self.name.lower()
            .replace("/", "_and_")
            .replace(" ", "_")
            .replace("-", "_")
            .replace("'", "")
        )

        super().__init__(
            STATIONTOPIC,
            key_schema=Station.key_schema,
            value_schema=Station.value_schema,
            num_partitions=1,
            num_replicas=1,
        )

    def run(self, train, direction, prev_station_id, prev_direction):
        print(f'[분석][station_run] train: {train}')
        print(f'[분석][station_run] direction: {direction}')
        print(f'[분석][station_run] prev_station_id: {prev_station_id}')
        print(f'[분석][station_run] prev_direction: {prev_direction}')

        self.producer.produce(
            topic=self.topic_name,
            key={"timestamp": self.time_millis()},
            value={
                "station_id": int(self.station_id),
                "train_id": str(train.train_id),
                "direction": str(direction),
                "line": str(self.color.name),  
                "train_status": str(train.status.name),
                "prev_station_id": prev_station_id,
                "prev_direction": prev_direction,
            },
        )

    def __str__(self):
        return "Station | {:^5} | {:<30} | Direction A: | {:^5} | departing to {:<30} | Direction B: | {:^5} | departing to {:<30} | ".format(
            self.station_id,
            self.name,
            self.a_train.train_id if self.a_train is not None else "---",
            self.dir_a.name if self.dir_a is not None else "---",
            self.b_train.train_id if self.b_train is not None else "---",
            self.dir_b.name if self.dir_b is not None else "---",
        )

    def __repr__(self):
        return str(self)

    def arrive_a(self, train, prev_station_id, prev_direction):
        """Denotes a train arrival at this station in the 'a' direction"""
        self.a_train = train
        self.run(train, "a", prev_station_id, prev_direction)

    def arrive_b(self, train, prev_station_id, prev_direction):
        """Denotes a train arrival at this station in the 'b' direction"""
        self.b_train = train
        self.run(train, "b", prev_station_id, prev_direction)

    def close(self):
        """Prepares the producer for exit by cleaning up the producer"""
        self.turnstile.close()
        super(Station, self).close()  # [수정]This is python 2.0 style
