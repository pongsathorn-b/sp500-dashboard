#!/usr/bin/env python3
"""Pre-fetch top 10 S&P 500 stocks by ticker symbol (alphabetical) and save to JSON."""

import json
import urllib.request
import time

TOP10 = ['AAPL', 'AMZN', 'AVGO', 'BRK-B', 'GOOGL', 'JPM', 'LLY', 'META', 'MSFT', 'NVDA']

COMPANY_NAMES = {
    'AAPL': 'Apple Inc.',
    'AMZN': 'Amazon.com, Inc.',
    'AVGO': 'Broadcom Inc.',
    'BRK-B': 'Berkshire Hathaway Inc.',
    'GOOGL': 'Alphabet Inc.',
    'JPM': 'JPMorgan Chase & Co.',
    'LLY': 'Eli Lilly and Company',
    'META': 'Meta Platforms, Inc.',
    'MSFT': 'Microsoft Corporation',
    'NVDA': 'NVIDIA Corporation',
}

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
                'name': COMPANY_NAMES.get(ticker, ticker),
                'price': round(price, 2),
                'prevClose': round(prev, 2),
                'change': round(change, 2),
                'changePct': round(change_pct, 2)
            }
    except Exception as e:
        print(f'  Failed {ticker}: {e}')
        return {'ticker': ticker, 'name': COMPANY_NAMES.get(ticker, ticker),
                'price': None, 'change': None, 'changePct': None}

def main():
    print('Fetching top 10 S&P 500 stock prices from Yahoo Finance...')
    prices = {}
    for i, ticker in enumerate(TOP10):
        print(f'  [{i+1:2d}/10] {ticker}...', end='', flush=True)
        data = fetch_price(ticker)
        prices[ticker] = data
        if data['price'] is not None:
            print(f' ${data["price"]} ({data["changePct"]:+.2f}%)')
        else:
            print(' FAILED')
        time.sleep(0.15)

    output = {
        'generated_at': time.strftime('%Y-%m-%dT%H:%M:%S') + '+00:00Z',
        'prices': prices
    }
    out_path = 'data/top10-prices.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    success = sum(1 for v in prices.values() if v['price'] is not None)
    print(f'\nDone: {success}/10 prices fetched. Saved to {out_path}')

if __name__ == '__main__':
    main()
