import logging
import time

from confluent_kafka import avro
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.avro import AvroProducer

logger = logging.getLogger(__name__)


# [수정] 생성자 안의 로직 분리
class Producer:
    existing_topics = set([])

    def __init__(
        self,
        topic_name,
        key_schema,
        value_schema=None,
        num_partitions=1,
        num_replicas=1,
    ):
        self.topic_name = topic_name
        self.key_schema = key_schema
        self.value_schema = value_schema
        self.num_partitions = num_partitions
        self.num_replicas = num_replicas
        self.broker_properties = {
            "bootstrap.servers": "PLAINTEXT://localhost:9092",
            "schema.registry.url": "http://localhost:8081/",
        }
        self.producer = AvroProducer(
            self.broker_properties,
            default_key_schema=self.key_schema,
            default_value_schema=self.value_schema,
        )

        if self.topic_name not in Producer.existing_topics:
            self.create_topic()
            Producer.existing_topics.add(self.topic_name)

    def create_topic(self):
        admin_client = AdminClient(
            {"bootstrap.servers": self.broker_properties["bootstrap.servers"]}
        )
        topic_metadata = admin_client.list_topics(timeout=5)
        if self.topic_name in topic_metadata.topics:
            logger.info(f"{self.topic_name} already exists. Skipping topic creation")
        else:
            futures = admin_client.create_topics(
                [
                    NewTopic(
                        topic=self.topic_name,
                        num_partitions=self.num_partitions,
                        replication_factor=self.num_replicas,
                        config={
                            "cleanup.policy": "delete",
                            "compression.type": "lz4",
                            "delete.retention.ms": "2000",
                            "file.delete.delay.ms": "2000",
                        },
                    )
                ]
            )

            for _, future in futures.items():
                try:
                    future.result()
                    logger.info(f"{self.topic_name} topic created")
                except Exception as e:
                    logger.error(f"Failed to create topic {self.topic_name}: {e}")

    def time_millis(self):
        return int(round(time.time() * 1000))

    def close(self):
        """Prepares the producer for exit by cleaning up the producer"""
        self.producer.flush(timeout=10)

    def time_millis(self):
        """Use this function to get the key for Kafka Events"""
        return int(round(time.time() * 1000))
