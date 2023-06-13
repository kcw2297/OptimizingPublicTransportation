"""Defines trends calculations for stations"""
import logging
import faust

logger = logging.getLogger(__name__)


class Station(faust.Record, validation=True, serializer="json"):
    stop_id: int
    direction_id: str
    stop_name: str
    station_name: str
    station_descriptive_name: str
    station_id: int
    order: int
    red: bool
    blue: bool
    green: bool

class TransformedStation(faust.Record, validation=True, serializer="json"):
    station_id: int
    station_name: str
    order: int
    line: str


app = faust.App("stations-stream", 
                broker="kafka://localhost:9092", 
                store="memory://")
sourceTopic = app.topic("stationDB_stations", value_type=Station)
sinkTopic = app.topic("station_faust", partitions=1)
faustTable = app.Table(
   "faust_table",
   default=TransformedStation,
   partitions=1,
   changelog_topic=sinkTopic,
)


#[Start Command]faust -A faust_stream worker -l info
@app.agent(sourceTopic)
async def process(stations):
    async for station in stations:
        print(f"[분석][faust] station: {station}")
        line = "red" if station.red else "blue" if station.blue else "green" if station.green else None
        print(f"[분석][faust] line: {line}")
        faustTable[station.station_id] = TransformedStation(
            station_id=station.station_id,
            station_name=station.station_name,
            order=station.order,
            line=line
        )

if __name__ == "__main__":
    app.main()
