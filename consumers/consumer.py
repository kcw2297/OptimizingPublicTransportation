"""Defines core consumer functionality"""
import logging
import confluent_kafka
from confluent_kafka import Consumer
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError
from tornado import gen
import re

logger = logging.getLogger(__name__)


class KafkaConsumer:
    """Defines the base kafka consumer class"""

    def __init__(
        self,
        topic_name_pattern,
        message_handler,
        is_avro=True,
        offset_earliest=False,
        sleep_secs=1.0,
        consume_timeout=0.1,
    ):
        """Creates a consumer object for asynchronous use"""
        self.topic_name_pattern = topic_name_pattern
        self.message_handler = message_handler
        self.sleep_secs = sleep_secs
        self.consume_timeout = consume_timeout
        self.offset_earliest = offset_earliest
        self.broker_properties = {
            "bootstrap.servers":"localhost:9092",
            "group.id":"consumer_group",
            "default.topic.config":{"auto.offset.reset":"earliest" if offset_earliest else "latest"}
        }

        if is_avro:
            self.broker_properties["schema.registry.url"] = "http://localhost:8081"
            self.consumer = AvroConsumer(self.broker_properties)
        else:
            self.consumer = Consumer(self.broker_properties)
        
        if self.topic_name_pattern == 'arrival':
            allTopics = self.consumer.list_topics().topics.keys()
            arrivalTopics = [topic for topic in allTopics if re.match("arrival_.*", topic)]
            self.consumer.subscribe(arrivalTopics, on_assign=self.on_assign)
        else:
            self.consumer.subscribe([self.topic_name_pattern], on_assign=self.on_assign)

    def on_assign(self, consumer, partitions):
        """Callback for when topic assignment takes place"""
        for partition in partitions:
            if self.offset_earliest:
                partition.offset = confluent_kafka.OFFSET_BEGINNING

        consumer.assign(partitions)

    async def consume(self):
        """Asynchronously consumes data from kafka topic"""
        while True:
            num_results = 1
            if num_results > 0:
                num_results = self._consume()
              
            await gen.sleep(self.sleep_secs)

    def _consume(self):
        """Polls for a message. Returns 1 if a message was received, 0 otherwise"""
      
        message = self.consumer.poll(timeout=self.consume_timeout)
        if message is None:
            return 0
        self.message_handler(message)
        return 1
      
 

    def close(self):
        """Cleans up any open kafka consumers"""
        self.consumer.close()