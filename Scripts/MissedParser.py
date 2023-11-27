import requests

cookies = {
    'visitor_id': '4543441',
    'adtech_uid': '54f4d6d4-bae6-4f0c-b577-ab03423ab90d%3Aosu.ru',
    'top100_id': 't1.1447118.1894625855.1690367588594',
    '_ym_uid': '1625578770885843340',
    '_ym_d': '1690367589',
    'visitor_id': '263110',
    'OSU_ANTIDDOS': '1',
    '_ym_isad': '1',
    '_ym_visorc': 'w',
    'sputnik_session': '1701099816585|1',
    'last_visit': '1701081816751%3A%3A1701099816751',
    't3_sid_1447118': 's1.16633807.1701098410100.1701099816754.65.3',
    'OSU_SID': '9atnb4me1pf0ivoancrn6tujs6',
    'ESDIRSESSID': 'X9X1SDD2MRNRV3548JBVJKKJ0EDPFGD3',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uk;q=0.6',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    # 'Cookie': 'visitor_id=4543441; adtech_uid=54f4d6d4-bae6-4f0c-b577-ab03423ab90d%3Aosu.ru; top100_id=t1.1447118.1894625855.1690367588594; _ym_uid=1625578770885843340; _ym_d=1690367589; visitor_id=263110; OSU_ANTIDDOS=1; _ym_isad=1; _ym_visorc=w; sputnik_session=1701099816585|1; last_visit=1701081816751%3A%3A1701099816751; t3_sid_1447118=s1.16633807.1701098410100.1701099816754.65.3; OSU_SID=9atnb4me1pf0ivoancrn6tujs6; ESDIRSESSID=X9X1SDD2MRNRV3548JBVJKKJ0EDPFGD3',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

params = {
    'page': 'attendance',
}

response = requests.get('https://www.osu.ru/iss/lks/index.php', params=params, cookies=cookies, headers=headers)
print(response.text)