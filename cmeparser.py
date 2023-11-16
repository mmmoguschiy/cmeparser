import sys
import requests
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

class st:
    def __init__(self, st, cs, ps, ci, pi, c, p, ct, pt):
        self.strike = st
        self.cset = cs
        self.pset = ps
        self.cint = ci
        self.pint = pi
        self.call = c
        self.put = p
        self.cit = ct
        self.pit = pt
        
def max_pain(strikes, calls, puts):
    total = np.array(calls) + np.array(puts)
    max_pain_index = np.argmin(np.abs(total - strikes))
    
    return strikes[max_pain_index]


h = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
    "Host": "www.cmegroup.com",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4",
    "Connection": "keep-alive",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "http://www.cmegroup.com"}

try:
    #    r = requests.get('https://www.cmegroup.com/CmeWS/mvc/Settlements/Options/Settlements/8116/OOF?monthYear=EUU'+sys.argv[1]+'21&strategy=DEFAULT&optionProductId=8116&optionExpiration=8116-'+sys.argv[1]+'1&tradeDate='+sys.argv[2], timeout=2.50, headers=h).json()
    r = requests.get(
        'https://www.cmegroup.com/CmeWS/mvc/Settlements/Options/Settlements/8116/OOF?monthYear=EUU' +
        sys.argv[1] +
        '23&strategy=DEFAULT&optionProductId=8116&optionExpiration=8116-' +
        sys.argv[1] +
        '3&tradeDate=' +
        sys.argv[2],
        timeout=2.50,
        headers=h).json()
#                      https://www.cmegroup.com/CmeWS/mvc/Settlements/Options/Settlements/8116/OOF?                               strategy=DEFAULT&optionProductId=8116&monthYear=EUUZ23&optionExpiration=8116-Z3&tradeDate=11/14/2023
#                      https://www.cmegroup.com/CmeWS/mvc/Settlements/Options/Settlements/8116/OOF?strategy=DEFAULT&optionProductId=8116&monthYear=EUUZ23&optionExpiration=8116-Z3&tradeDate=11/14/2023

    last_quotes = [
        (item['strike'],
         item['type'],
         item['settle'],
         item['openInterest']) for item in r['settlements']]
except requests.ReadTimeout:
    print("wait error")

cp = []
for item in last_quotes:
    if str(item[0]) == "Total":
        continue

    y = False
#    strike = float(item[0]) / 10000
    strike = float(item[0])
    for i in cp:
        if i.strike == strike:
            if item[2] == "CAB":
                settle = 0.00005
            else:
                settle = float(item[2].replace('.', '0.'))
            interest = int(item[3].replace(',', ''))
            if item[1] == "Put":
                i.pset = settle
                i.pint = interest
                i.put = settle * interest
            if item[1] == "Call":
                i.call = settle * interest
            y = True
            break
    if y:
        continue
    if item[2] == "CAB":
        settle = 0.00005
    else:
        settle = float(item[2].replace('.', '0.'))
    interest = int(item[3].replace(',', ''))
    if item[1] == "Put":
        put = settle * interest
        cp.append(st(strike, 0.0, settle, 0, interest, 0.0, 0.0, 0.0, 0.0))
    if item[1] == "Call":
        call = settle * interest
        cp.append(st(strike, settle, 0.0, interest, 0, call, 0.0, 0.0, 0.0))

for item in cp:
    print(
        item.strike,
        item.cset,
        item.pset,
        item.cint,
        item.pint,
        item.call,
        item.put)
        
strikes = [item.strike for item in cp]
cinp_values = [item.cint for item in cp]
pint_values = [item.pint for item in cp]

calls = [item.cset for item in cp]
puts = [item.pset for item in cp]

max_pain(strikes, calls, puts)

bar_width = 0.35

plt.bar(np.arange(len(strikes)), cinp_values, width=bar_width, label='CINP')
plt.bar(np.arange(len(strikes)) + bar_width, pint_values, width=bar_width, label='PINT')

plt.xlabel('Strike')
plt.ylabel('CINP and PINT')
plt.title('Strike vs CINP and PINT')


plt.xticks(rotation=90)
plt.xticks(np.arange(len(strikes)), strikes)

plt.legend()

plt.show()
