from datetime import datetime, timedelta

TIME_OFFSET = 5


class Pair:
    def __init__(self, name: str, pair_type: str, audit: str, time: str, professor: str):
        self.name = name
        self.type = pair_type
        self.audit = audit

        self.time = datetime.strptime(time, "%H:%M").time()
        self.time_end = (datetime.strptime(time, "%H:%M") + timedelta(hours=1, minutes=30)).time()

        self.professor = professor


class Day:
    def __init__(self, date: str, pairs):
        self.date = datetime.strptime(date, "%d/%m/%Y").date()
        self.pairs = pairs

    def get_current_pair(self):
        current_time = (datetime.now() + timedelta(hours=TIME_OFFSET)).time()
        for pair in self.pairs:
            if pair.time < current_time < pair.time_end:
                return pair

        return None

    def get_next_pair(self):
        if self.get_current_pair() is None:
            return self.find_near_pair()[0]

        for pair in range(len(self.pairs)):
            if self.pairs[pair] == self.get_current_pair():
                if len(self.pairs) >= pair + 1:
                    return self.pairs[pair + 1]
                else:
                    return self.pairs[pair]

        return None

    def find_near_pair(self):
        current_time = (datetime.now() + timedelta(hours=TIME_OFFSET)).time()

        min_time = timedelta.max
        nearest = self.pairs[0]

        for pair in self.pairs:
            pair_datetime = datetime.combine(datetime.today(), pair.time)
            time_difference = datetime.combine(datetime.today(), current_time) - pair_datetime

            if min_time > abs(time_difference):
                min_time = abs(time_difference)
                nearest = pair

        return nearest, min_time


class Days:
    def __init__(self, days):
        self.days = days

    def get_current_day(self):
        current_time = datetime.now().strftime("%d/%m/%Y")
        return self.find_day(f'{current_time}')

    def find_near_day(self):
        current_time = (datetime.now() + timedelta(hours=TIME_OFFSET)).time()

        min_time = timedelta.max
        nearest = self.days[0]

        for pair in self.days:
            day_datetime = datetime.combine(datetime.today(), pair.time)
            time_difference = datetime.combine(datetime.today(), current_time) - day_datetime

            if min_time > abs(time_difference):
                min_time = abs(time_difference)
                nearest = pair

        return nearest, min_time

    def find_day(self, date):
        for day in self.days:
            if day.date == datetime.strptime(date, "%d/%m/%Y").date():
                return day

        return None

    def find_day_index(self, date):
        for day in range(len(self.days)):
            if self.days[day].date == datetime.strptime(date, "%d/%m/%Y").date():
                return day

        return 0
