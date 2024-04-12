import requests
import json
from bs4 import BeautifulSoup as bs
from datetime import datetime


def nate_crawler():
    now = datetime.now().strftime('%Y%m%d%H%M')
    url = 'https://www.nate.com/js/data/jsonLiveKeywordDataV1.js?v=' + now
    r = requests.get(url).content
    keyword_list = json.loads(r.decode('euc-kr'))
    result = []
    for i in keyword_list:
        result.append(i[1])
    return result


def list_print(fct):
    count = 1
    output = []
    for item in fct:
        if count == 11:
            break
        output.append({"keyword": item})
        count += 1
    return output
