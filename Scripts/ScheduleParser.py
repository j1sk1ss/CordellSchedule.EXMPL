import requests
from bs4 import BeautifulSoup

from Objects.Pair import Pair, Days, Day


class Parser:
    def __init__(self, link, pairs):
        self.link = link
        self.pairs = pairs

    def parse(self):
        answer = requests.get(self.link)
        soup = BeautifulSoup(answer.text, "html.parser")

        dates, auditors, pairs, pair_types, pairs_time, professors = [], [], [], [], [], []

        for day in soup.findAll('tr'):
            current_pairs = day.findAll('td', class_=self.pairs)
            date = day.findAll('td', class_=None)

            if date is not None and current_pairs is not None:
                day_auditors = []
                day_pairs = []
                day_types = []
                day_prof = []
                day_pair_times = []
                for pair in current_pairs:
                    pair_data = pair.findAll('a')

                    temp_pair = pair.find('span', class_='dis').text
                    temp = pair_data[0].find('span', class_='aud').text
                    temp_prof = pair_data[1].find('span', class_='p').text
                    if temp == '' or temp is None:
                        continue

                    day_pair_times.append(PairType().times[int(pair['pare_id']) - 1])
                    day_types.append(PairType().types[list(pair['class'])[0]])

                    day_auditors.append(temp)
                    day_pairs.append(temp_pair)
                    day_prof.append(temp_prof)

                if len(day_auditors) > 0:
                    pairs_time.append(day_pair_times)
                    auditors.append(day_auditors)
                    pairs.append(day_pairs)
                    professors.append(day_prof)
                    pair_types.append(day_types)

                    for current_date in date:
                        if current_date.text != ' ':
                            dates.append(current_date.text.replace(')', '').split('(')[0])

        days = []
        for i in range(len(pairs_time)):
            pairs_objects = []
            for j in range(len(pairs_time[i])):
                pairs_objects.append(Pair(pairs[i][j], pair_types[i][j], auditors[i][j], pairs_time[i][j], professors[i][j]))

            days.append(Day(dates[i].replace('.', '/'), pairs_objects))

        return Days(days)


class PairType:
    def __init__(self):
        self.practice = ['pr coming', 'pr passed']
        self.laboratory = ['lb coming', 'lb passed']
        self.lection = ['l coming', 'l passed']

        self.types = {
            'l': 'Lc.',
            'lb': 'Lb.',
            'pr': 'Pr.'
        }

        self.times = ['8:00', '9:40', '11:20', '13:20', '15:00', '16:40', '18:20', '20:00']

    def get_all(self):
        return [*self.practice, *self.laboratory, *self.lection]

    def get_labs(self):
        return [*self.laboratory]

    def get_practice(self):
        return [*self.practice]

    def get_lections(self):
        return [*self.lection]
