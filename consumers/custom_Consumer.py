from confluent_kafka import Consumer, KafkaException
import json
import re
from confluent_kafka.avro import AvroConsumer

consumer = AvroConsumer({
    "bootstrap.servers":"localhost:9092",
    "group.id":"my_group",
    "auto.offset.reset":"earliest",
    "schema.registry.url" : "http://localhost:8081"
})

def print_assignment(consumer, partitions):
    print('Assignment:', partitions)

# Subscribe to topic
topics = consumer.list_topics().topics.keys()
filtered_topics = [topic for topic in topics if re.match("arrival_.*", topic)] 
print(f'[분석][custom] filtertopic: {filtered_topics}')

consumer.subscribe(filtered_topics, on_assign=print_assignment) 

try:
    while True:
        msg = consumer.poll(1.0)  # timeout set to 1 second
       
        if msg is None:
            print('[분석][custom]]no message found')
            continue
        if msg.error():
            print('[분석][custom] 에러 발생')
            raise KafkaException(msg.error())
        else:
            print('[분석][custom] 메시지를 받았습니다.')
            message = msg.value()
            print('Received message:', message)

except KeyboardInterrupt:
    consumer.close()

