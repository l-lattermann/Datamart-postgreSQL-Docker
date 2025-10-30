
import datetime
import random

start_timestamp = datetime.datetime(2022, 1, 1,)
stop_timestamp = datetime.datetime(2025, 12, 31)
time_delta = stop_timestamp - start_timestamp
timestamps = []
print(int(time_delta.total_seconds()))


'''
for dummy_id in range(40):
    random_timestamp = start_timestamp + random.randint(0, int(time_delta.total_seconds()))
    timestamps.append(random_timestamp)'''