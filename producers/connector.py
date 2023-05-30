import json
import logging
import requests

logger = logging.getLogger(__name__)

KAFKA_CONNECT_URL = "http://localhost:8083/connectors"
CONNECTOR_NAME = "stations"


def configure_connector():
    logging.debug("creating or updating kafka connect connector...")

    resp = requests.get(f"{KAFKA_CONNECT_URL}/{CONNECTOR_NAME}")
    if resp.status_code == 200:
        logging.debug("connector already created skipping recreation")
        return

    resp = requests.post(
        KAFKA_CONNECT_URL,
        headers={"Content-Type": "application/json"},
        data=json.dumps(
            {
                "name": CONNECTOR_NAME,
                "config": {
                    "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
                    "key.converter": "org.apache.kafka.connect.json.JsonConverter",  # connector convert data from connector format to the kafka message format
                    "key.converter.schemas.enable": "false",  # specify whether the converter should include schema information in the messages.
                    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
                    "value.converter.schemas.enable": "false",
                    "batch.max.rows": "500",  # source를 batch할 최대 행의 수입니다. 한번에 메모리에 적재될 양을 정합니다.
                    "connection.url": "jdbc:postgresql://localhost:5432/cta",
                    "connection.user": "cta_admin",
                    "connection.password": "chicago",
                    "table.whitelist": "stations",
                    "mode": "incrementing",
                    "incrementing.column.name": "stop_id",
                    "topic.prefix": "stations-",
                    "poll.interval.ms": "3600000",
                },
            }
        ),
    )

    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.error(f"HTTP error occurred: {err}")
    else:
        logging.debug("connector created successfully")


if __name__ == "__main__":
    configure_connector()
