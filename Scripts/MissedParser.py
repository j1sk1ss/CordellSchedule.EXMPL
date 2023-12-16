from datetime import datetime

import requests
from bs4 import BeautifulSoup

from Objects.Pair import Pair
from Objects.User import User

enter_data = [
    {
        'visitor_id': '4543441',
        'adtech_uid': '54f4d6d4-bae6-4f0c-b577-ab03423ab90d%3Aosu.ru',
        'top100_id': 't1.1447118.1894625855.1690367588594',
        '_ym_uid': '1625578770885843340',
        '_ym_d': '1690367589',
        'visitor_id': '263110',
        'OSU_ANTIDDOS': '1',
        '_ym_isad': '1',
        'sputnik_session': '1702706357573|1',
        't3_sid_1447118': 's1.1384344100.1702706357669.1702706357669.78.1',
        'last_visit': '1702688357671%3A%3A1702706357671',
        '_ym_visorc': 'w',
        'OSU_SID': '5gsera2rbbm98j99cf3tmvs9j6',
    },
    {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uk;q=0.6',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.osu.ru',
        'Referer': 'https://www.osu.ru/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/120.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
]


class MissedParser:
    def legacy_is_missed(self, user, date: datetime, pair: Pair):
        missed = self.get_legacy_missed(user, date)
        for element in missed:
            if pair.time == datetime.strptime(element['Pair start'], "%H:%M").time():
                if datetime.strptime(element['Pair missed'], "%H:%M").time() < datetime.strptime('00:10', "%H:%M").time():
                    return True
                else:
                    return False

        return False

    def is_missed(self, user, pair: Pair):
        today_missed = self.get_current_missed(user)
        for element in today_missed:
            if pair.time == datetime.strptime(element['Pair start'], "%H:%M").time():
                if datetime.strptime(element['Pair missed'], "%H:%M").time() < datetime.strptime('00:10', "%H:%M").time():
                    return True
                else:
                    return False

        return False

    def get_legacy_missed(self, user, date: datetime):
        missed = self.get_missed(user)

        pairs = []
        for day in missed:
            for pair in day:
                if datetime.strptime(pair['Pair date'], "%d.%m.%Y").date() == date:
                    pairs.append(pair)

        return pairs

    def get_current_missed(self, user):
        current_day = datetime.now()
        missed = self.get_missed(user)

        pairs = []
        for day in missed:
            for pair in day:
                if datetime.strptime(pair['Pair date'], "%d.%m.%Y").date() == current_day.date():
                    pairs.append(pair)

        return pairs

    @staticmethod
    def get_missed(user: User):
        current_day = datetime.now()
        enter_response = requests.post('https://www.osu.ru/iss/lks/index.php?page=attendance', cookies=enter_data[0],
                                       headers=enter_data[1], data={
                'login': user.login,
                'opsw': '',
                'psw': user.password,
            })

        pairs_count = 0
        pairs = []
        for line in BeautifulSoup(enter_response.text, "html.parser").findAll('tr'):
            for column in line.findAll('td', class_=None):
                # Parse date and pair count
                if '.' in column.text:
                    if column.has_attr('rowspan'):
                        if datetime.strptime(column.text.split(',')[0], "%d.%m.%Y") > current_day:
                            return

                        pairs_count = int(column["rowspan"])
                        temp = []
                        for i in range(pairs_count):
                            temp.append({
                                'Pair name': '',
                                'Pair date': column.text.split(',')[0],
                                'Pair missed': '',
                                'Pair start': ''
                            })

                        pairs.append(temp)
                        continue

                # Parse missed time
                if ':' in column.text:
                    if column.has_attr('rowspan') and column.has_attr('colspan') is False:
                        pairs[-1][len(pairs[-1]) - pairs_count]['Pair start'] = column.text.split('-')[0]
                        continue

                    if column.has_attr('rowspan') is False and column.has_attr('colspan') is False:
                        pairs[-1][len(pairs[-1]) - pairs_count]['Pair missed'] = column.text
                        continue

            # Parse pair name
            for column in line.findAll('td', class_='align_left'):
                if column.has_attr('rowspan'):
                    pairs[-1][len(pairs[-1]) - pairs_count]['Pair name'] = column.text

            pairs_count -= 1
            if pairs_count <= 0:
                pairs_count = 0

        return [
            [item for item in inner_list if item['Pair name'] != '']
            for inner_list in pairs
        ]
