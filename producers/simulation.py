# Libraries
import datetime
import time
import logging
import logging.config
import pandas as pd
from pathlib import Path
from enum import IntEnum
# Local Modules
from connector import configure_connector
from models import Line, Weather

# Import logging before models to ensure configuration is picked up
logging.config.fileConfig(f"{Path(__file__).parents[0]}/logging.ini")

logger = logging.getLogger(__name__)


# [수정] logger의 사용 여부 조사하기
class TimeSimulation:
    weekdays = IntEnum("weekdays", "mon tue wed thu fri sat sun", start=0)
    ten_min_frequency = datetime.timedelta(minutes=10)

    def __init__(self, sleep_seconds=5, time_step=None, schedule=None):
        """Initializes the time simulation"""
        self.sleep_seconds = sleep_seconds
        self.time_step = time_step
        if self.time_step is None:
            self.time_step = datetime.timedelta(minutes=self.sleep_seconds)

        # Read data from disk
        self.raw_df = pd.read_csv(
            f"{Path(__file__).parents[0]}/data/cta_stations.csv"
        ).sort_values("order")

        # Define the train schedule (same for all trains)
        self.schedule = schedule
        if schedule is None:
            self.schedule = {
                TimeSimulation.weekdays.mon: {0: TimeSimulation.ten_min_frequency},
                TimeSimulation.weekdays.tue: {0: TimeSimulation.ten_min_frequency},
                TimeSimulation.weekdays.wed: {0: TimeSimulation.ten_min_frequency},
                TimeSimulation.weekdays.thu: {0: TimeSimulation.ten_min_frequency},
                TimeSimulation.weekdays.fri: {0: TimeSimulation.ten_min_frequency},
                TimeSimulation.weekdays.sat: {0: TimeSimulation.ten_min_frequency},
                TimeSimulation.weekdays.sun: {0: TimeSimulation.ten_min_frequency},
            }

        self.train_lines = [
            Line(Line.colors.blue, self.raw_df[self.raw_df["blue"]]),
            Line(Line.colors.red, self.raw_df[self.raw_df["red"]]),
            Line(Line.colors.green, self.raw_df[self.raw_df["green"]]),
        ]

    def run(self):
        curr_time = datetime.datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        print('[분석][simulation_run] connector configure 시작')
        configure_connector()
        print('[분석][simulation_run] weather topic creation')
        weather = Weather(curr_time.month)
        try:
            while True:
                if curr_time.minute == 0:
                    print('[분석][simulation_run] weather run 시작')
                    weather.run(curr_time.month)
                print('[분석][simulation_run] line run => turnstile/station 시작')
                _ = [line.run(curr_time, self.time_step) for line in self.train_lines]
                curr_time = curr_time + self.time_step
                time.sleep(self.sleep_seconds)
        except KeyboardInterrupt as e:
            print("Shutting down!!!!!!!!!!!!!!!!!!!! close the Topics")
            _ = [line.close() for line in self.train_lines]


if __name__ == "__main__":
    TimeSimulation().run()
