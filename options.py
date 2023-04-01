XP_AIRPORT_CODES = '''//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[3]/ul/li[1]/div/div[2]/div/div[2]/div[3]/span'''
XP_PRICE = '''//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[3]/ul/li[1]/div/div[2]/div/div[2]/div[6]/div[1]/div[2]/span'''
XP_COMPANY = '''//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[3]/ul/li[1]/div/div[2]/div/div[2]/div[2]/div[2]'''
XP_TYPE = '''//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[3]/ul/li[1]/div/div[2]/div/div[2]/div[6]/div[2]'''
XP_DURATION = '''//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[3]/ul/li[1]/div/div[2]/div/div[2]/div[3]/div'''
XP_STOPS = '''//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[3]/ul/li[1]/div/div[2]/div/div[2]/div[4]/div[1]/span'''
XP_CLICK_FIRST_SORTED = '''//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[3]/ul/li[1]/div/div[2]'''
XP_NOT_FOUND = '''//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[2]/p[1]'''
XP_NOT_FOUND_MESSAGE = '''//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[2]/p[2]'''
XPATH_DICT = { 
    'codes':XP_AIRPORT_CODES,
    'price': XP_PRICE,
    'company':XP_COMPANY,
    'type': XP_TYPE,
    'duration':XP_DURATION,
    'stops':XP_STOPS,
}
XPATH_KEYS = [k for k in XPATH_DICT.items()]
XPATH_LIST = [str(v) for v in XPATH_DICT.values()]
DEFATULT_SETTINGS = '''
{
    "from": [
        "FCO",
        "NAP"
    ],
    "to": [
        "MDE",
        "BOG",
        "CTG"
    ],
    "outbound": "2023-10-01",
    "delta": 20,
    "flexdays": 4,
    "lastdate": "2024-02-15",
    "fastmode": false,
    "timeout": 10,
    "tclass": [
        "economy",
        "business",
        "first"
    ]
}'''


