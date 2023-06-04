from confluent_kafka.admin import AdminClient
from confluent_kafka import Consumer, KafkaException

# admin_client = AdminClient({"bootstrap.servers": "localhost:9092"})

# cluster_metadata = admin_client.list_topics()
# topic_metadata = cluster_metadata.topics

# for topic in topic_metadata:
#     print(topic)


def create_consumer():
    conf = {'bootstrap.servers': "PLAINTEXT://localhost:9092", # replace with your server
            'group.id': "your_group_id", # replace with your group id
            'auto.offset.reset': 'earliest'}

    consumer = Consumer(conf)
    return consumer

def consume_messages(consumer, topic):
    consumer.subscribe([topic])

    try:
        while True:
            msg = consumer.poll(1.0)  # timeout in seconds; adjust accordingly

            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                # Proper message
                print("Received message: {}".format(msg.value().decode('utf-8')))

    except KeyboardInterrupt:
        pass

    finally:
        # Close down consumer to commit final offsets.
        consumer.close()

if __name__ == "__main__":
    consumer = create_consumer()
    consume_messages(consumer, "weather")  # replace with your topic
