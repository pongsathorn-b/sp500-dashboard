#!/usr/bin/env python3
"""Pre-fetch top 50 S&P 500 stock prices and save to JSON for the dashboard."""

import json
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

def iso_now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')

TOP50 = [
    'AAPL','MSFT','NVDA','AMZN','META','GOOGL','GOOG','BRK.B','LLY','AVGO',
    'JPM','V','XOM','MA','UNH','JNJ','PG','HD','ABBV','MRK',
    'CVX','COST','PEP','ADBE','KO','CRM','WMT','BAC','TMO','MCD',
    'CSCO','ABT','DHR','ACN','NKE','TXN','PM','NEE','UPS','RTX',
    'ORCL','HON','AMGN','IBM','CAT','BA','GE','SBUX','INTC'
]

def fetch_price(ticker):
    url = f'https://query2.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=2d'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
            result = d.get('chart', {}).get('result', [{}])[0]
            meta = result.get('meta', {})
            price = meta.get('regularMarketPrice', 0)
            prev = meta.get('previousClose') or meta.get('chartPreviousClose', 0)
            change = price - prev
            change_pct = (change / prev * 100) if prev > 0 else 0
            return {
                'ticker': ticker,
                'price': round(price, 2),
                'prevClose': round(prev, 2),
                'change': round(change, 2),
                'changePct': round(change_pct, 2)
            }
    except Exception as e:
        print(f'  Failed {ticker}: {e}')
        return {'ticker': ticker, 'price': None, 'change': None, 'changePct': None}

def main():
    print('Fetching top 50 stock prices from Yahoo Finance...')
    prices = {}
    for i, ticker in enumerate(TOP50):
        print(f'  [{i+1:2d}/50] {ticker}...', end='', flush=True)
        data = fetch_price(ticker)
        prices[ticker] = data
        if data['price']:
            print(f' ${data["price"]} ({data["changePct"]:+.2f}%)')
        else:
            print(' FAILED')
        time.sleep(0.1)  # be gentle

    # Save to data/live-prices.json
    output = {
        'generated_at': iso_now(),
        'prices': prices
    }
    out_path = 'data/live-prices.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    success = sum(1 for v in prices.values() if v['price'] is not None)
    print(f'\nDone: {success}/50 prices fetched. Saved to {out_path}')

if __name__ == '__main__':
    main()
