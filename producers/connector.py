import json
import logging
import requests

logger = logging.getLogger(__name__)

KAFKA_CONNECT_URL = "http://localhost:8083/connectors"
CONNECTOR_NAME = "stationDB"
DOCKERPOSTGRES = "postgres"

def configure_connector():
    connectorGetResponse = requests.get(f"{KAFKA_CONNECT_URL}/{CONNECTOR_NAME}")

    if connectorGetResponse.status_code == 200:
        print("이미 해당 stream을 생성하였습니다.")
        return

    connectorPostResponse = requests.post(
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
                    "batch.max.rows": "50",  # source를 batch할 최대 행의 수입니다. 한번에 메모리에 적재될 양을 정합니다.
                    "table.whitelist": "stations",
                    "connection.url": f"jdbc:postgresql://{DOCKERPOSTGRES}:5432/cta",
                    "connection.user": "cta_admin",
                    "connection.password": "chicago",
                    "mode": "incrementing",
                    "incrementing.column.name": "stop_id",
                    "topic.prefix": f"{CONNECTOR_NAME}_",
                    "poll.interval.ms": "3600000",
                },
            }
        ),
    )

    try:
        connectorPostResponse.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.error(f"HTTP error occurred: {err}")
    else:
        print("Post connectorResponse:", connectorPostResponse.content)


if __name__ == "__main__":
    configure_connector()
