from datetime import datetime, timedelta


TIME_OFFSET = 0


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
        return self.find_day(datetime.now().date())

    def find_near_day(self):
        current_time = (datetime.now() + timedelta(hours=TIME_OFFSET)).time()

        min_time = timedelta.max
        nearest = self.days[0]

        for day in self.days:
            day_datetime = datetime.combine(day.date, current_time)
            time_difference = datetime.now() - day_datetime

            if min_time > abs(time_difference):
                min_time = abs(time_difference)
                nearest = day

        return nearest, min_time

    def find_day(self, date):
        for day in self.days:
            if day.date == date:
                return day

        return self.find_near_day()[0]

    def find_day_index(self, date):
        for day in range(len(self.days)):
            if self.days[day].date == date:
                return day

        return 0
