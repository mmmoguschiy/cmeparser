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

data = {
    'strike': strikes,
    'cset': cinp_values,
    'pset': pint_values
}

put_payouts = []
call_payouts = []

for current_strike in data['strike']:
    put_payout = 0
    call_payout = 0

    for i in range(len(data['strike'])):
        strike_price = data['strike'][i]
        cset_price = data['cset'][i]
        pset_price = data['pset'][i]

        put_intrinsic_value = 0 if strike_price <= current_strike else (strike_price - current_strike)

        call_intrinsic_value = 0 if strike_price >= current_strike else (current_strike - strike_price)

        put_payout += put_intrinsic_value * pset_price

        call_payout += call_intrinsic_value * cset_price

    put_payouts.append(put_payout)
    call_payouts.append(call_payout)
    
total_payouts = [put + call for put, call in zip(put_payouts, call_payouts)]

min_index = total_payouts.index(min(total_payouts))

fig, ax = plt.subplots()
bar_width = 0.55
opacity = 0.85

index = range(len(data['strike']))
rects1 = ax.bar(index, put_payouts, bar_width, alpha=opacity, color='orange', label='Put Payout')
rects2 = ax.bar(index, call_payouts, bar_width, alpha=opacity, color='b', label='Call Payout', bottom=put_payouts)
rects3 = ax.bar(min_index, total_payouts[min_index], bar_width, alpha=opacity, color='r', label='Maxpain')

ax.set_xlabel('Strike')
ax.set_ylabel('Payout')
ax.set_title('Maxpain')
ax.set_xticks(index)
ax.set_xticklabels(data['strike'])
ax.legend()

plt.xticks(rotation=90)
plt.tight_layout()
plt.show()
