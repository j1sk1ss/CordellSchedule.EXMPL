from datetime import datetime, timedelta


class Pair:
    def __init__(self, name: str, pair_type: str, audit: str, time: str, professor: str):
        self.name = name
        self.type = pair_type
        self.audit = audit

        self.time = datetime.strptime(time, "%H:%M").time()
        self.time_end = (datetime.strptime(time, "%H:%M") + timedelta(hours=1, minutes=30)).time()

        self.professor = professor
