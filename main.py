import pandas as pd
import time
import subprocess

ADDRESS = "https://www.greekembassy.org.uk/en-gb/Reservations/ctl/ViewAvailability/mid/484/List/ViewAvailabilityListSettings"


def read_tables(address):
    return pd.read_html(address)


def get_appointments_table(address):
    dfs = read_tables(address)
    table = dfs[0]
    table.columns = table.iloc[1, :]
    table = table.iloc[2:, 1:]
    table = table.set_index("Category")
    return table


def get_military(address):
    index = "3. Military Affairs / Permanent Residence Certificates - Στρατολογικά"
    table = get_appointments_table(address)
    return table.loc[index]


def has_availability(military):
    availability = military["Availability"]
    return False if availability == "0" else True


def next_available_date(military):
    return military["Next Available Date"]


def monitor():
    military = get_military(ADDRESS)
    count = 0
    while not has_availability(military):
        print(f"({count}): No appointments available")
        count += 1
        time.sleep(10)
        military = get_military(ADDRESS)
    print(f"Found an appointment, elapsed time: {count*10} seconds")
    alarm()


def alarm():
    while True:
        audio_file = "alarm.mp3"
        subprocess.call(["afplay", audio_file])


if __name__ == "__main__":
    monitor()
