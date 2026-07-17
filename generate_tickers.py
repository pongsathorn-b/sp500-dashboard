#!/usr/bin/env python3
"""
Fetch live S&P 500 top-10 prices from Yahoo Finance and generate tickers.html
with real data baked in.  Run this before deploying to GitHub Pages.
"""
import urllib.request
import json
import urllib.parse
import sys
from datetime import datetime, timezone

# BRK-B uses hyphen in Yahoo Finance URL, but displays as BRK.B
TICKERS = ['AAPL', 'AMZN', 'AVGO', 'BRK-B', 'GOOGL', 'JPM', 'LLY', 'META', 'MSFT', 'NVDA']

def fetch_quote(ticker):
    target = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1d"
    req = urllib.request.Request(target, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        d = json.loads(resp.read())
        r = d['chart']['result'][0]
        m = r['meta']
        return {
            'symbol': ticker,
            'name':    m.get('longName', m.get('symbol', ticker)),
            'price':   m['regularMarketPrice'],
            'change':  m.get('regularMarketChange'),
            'changePct': m.get('regularMarketChangePercent'),
        }

def build_html(stocks, fetched_at):
    rows = ''
    for s in stocks:
        chg   = s['change']
        pct   = s['changePct']
        is_up = chg >= 0 if chg is not None else True
        cls   = 'change-positive' if is_up else 'change-negative'
        sign  = '+' if is_up else ''
        chg_txt = f"{sign}{chg:.2f} ({sign}{pct:.2f}%)" if chg is not None else '—'

        rows += f"""        <tr>
          <td>
            <div class="ticker-cell">
              <span class="ticker-symbol">{s['symbol']}</span>
              <span class="ticker-name">{s['name']}</span>
            </div>
          </td>
          <td class="price-cell">${s['price']:.2f}</td>
          <td class="change-cell {cls}">{chg_txt}</td>
        </tr>
"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>S&P 500 Top 10 Tickers</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --bg-base: #060b14;
      --bg-surface: #0c1524;
      --bg-card: #111e30;
      --bg-card-hover: #162436;
      --border: rgba(255,255,255,0.07);
      --accent: #00d4aa;
      --accent-dim: rgba(0,212,170,0.12);
      --up: #00d4aa;
      --down: #ff4757;
      --text-primary: #e8edf5;
      --text-secondary: #7a8ba0;
      --text-muted: #4a5a70;
      --font-display: 'Syne', system-ui, sans-serif;
      --font-body: 'DM Sans', system-ui, sans-serif;
      --font-mono: 'JetBrains Mono', ui-monospace, monospace;
    }}

    body {{
      font-family: var(--font-body);
      background: var(--bg-base);
      color: var(--text-primary);
      min-height: 100vh;
      -webkit-font-smoothing: antialiased;
    }}

    .header {{
      border-bottom: 1px solid var(--border);
      padding: 0 24px;
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .header-title {{
      font-family: var(--font-display);
      font-size: 1.1rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      color: var(--text-primary);
    }}

    .header-title span {{ color: var(--accent); }}

    .live-badge {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.7rem;
      font-weight: 600;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--accent);
      background: var(--accent-dim);
      border: 1px solid rgba(0,212,170,0.2);
      padding: 4px 10px;
      border-radius: 20px;
    }}

    .live-dot {{
      width: 6px;
      height: 6px;
      background: var(--accent);
      border-radius: 50%;
      animation: pulse 2s ease-in-out infinite;
    }}

    @keyframes pulse {{
      0%, 100% {{ opacity: 1; transform: scale(1); }}
      50% {{ opacity: 0.5; transform: scale(0.8); }}
    }}

    .main {{
      max-width: 720px;
      margin: 0 auto;
      padding: 24px 16px 60px;
    }}

    .page-intro {{ margin-bottom: 28px; }}

    .page-intro h1 {{
      font-family: var(--font-display);
      font-size: clamp(1.6rem, 5vw, 2.2rem);
      font-weight: 800;
      letter-spacing: -0.03em;
      line-height: 1.1;
      margin-bottom: 8px;
    }}

    .page-intro h1 em {{
      font-style: normal;
      color: var(--accent);
    }}

    .page-intro p {{
      font-size: 0.9rem;
      color: var(--text-secondary);
      line-height: 1.5;
    }}

    .updated {{
      font-size: 0.72rem;
      color: var(--text-muted);
      margin-top: 4px;
    }}

    .stocks-table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      overflow: hidden;
    }}

    .stocks-table thead th {{
      font-size: 0.65rem;
      font-weight: 600;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--text-muted);
      padding: 12px 16px;
      text-align: left;
      border-bottom: 1px solid var(--border);
      background: var(--bg-card);
    }}

    .stocks-table thead th:last-child,
    .stocks-table thead th:nth-last-child(2) {{ text-align: right; }}

    .stocks-table tbody tr {{
      border-bottom: 1px solid var(--border);
      transition: background 0.15s;
    }}

    .stocks-table tbody tr:last-child {{ border-bottom: none; }}
    .stocks-table tbody tr:hover {{ background: var(--bg-card-hover); }}
    .stocks-table tbody td {{ padding: 14px 16px; vertical-align: middle; }}

    .ticker-cell {{
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}

    .ticker-symbol {{
      font-family: var(--font-mono);
      font-size: 0.95rem;
      font-weight: 500;
      color: var(--text-primary);
      letter-spacing: 0.02em;
    }}

    .ticker-name {{
      font-size: 0.72rem;
      color: var(--text-muted);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 180px;
    }}

    .price-cell {{
      font-family: var(--font-mono);
      font-size: 0.95rem;
      font-weight: 500;
      color: var(--text-primary);
      text-align: right;
      white-space: nowrap;
    }}

    .change-cell {{
      font-family: var(--font-mono);
      font-size: 0.8rem;
      font-weight: 500;
      text-align: right;
      white-space: nowrap;
    }}

    .change-positive {{ color: var(--up); }}
    .change-negative {{ color: var(--down); }}

    .footer {{
      text-align: center;
      padding: 24px;
      font-size: 0.72rem;
      color: var(--text-muted);
      border-top: 1px solid var(--border);
      margin-top: 40px;
    }}

    .footer a {{ color: var(--text-muted); text-decoration: none; }}
    .footer a:hover {{ color: var(--accent); }}

    @media (max-width: 480px) {{
      .ticker-name {{ display: none; }}
      .stocks-table thead th {{ padding: 10px 12px; font-size: 0.6rem; }}
      .stocks-table tbody td {{ padding: 12px 12px; }}
      .price-cell {{ font-size: 0.85rem; }}
      .change-cell {{ font-size: 0.72rem; }}
    }}
  </style>
</head>
<body>

  <header class="header">
    <div class="header-title">S&amp;P&nbsp;500 <span>Tickers</span></div>
    <div class="live-badge">
      <div class="live-dot"></div>
      Live
    </div>
  </header>

  <main class="main">
    <div class="page-intro">
      <h1>Top 10 <em>S&amp;P 500</em><br>Stocks by Symbol</h1>
      <p>Real-time prices sourced from Yahoo Finance. Sorted alphabetically by ticker symbol.</p>
      <p class="updated">Prices as of {fetched_at}</p>
    </div>

    <table class="stocks-table">
      <thead>
        <tr>
          <th>Ticker</th>
          <th>Price</th>
          <th>Day Change</th>
        </tr>
      </thead>
      <tbody>
{rows}
      </tbody>
    </table>

    <footer class="footer">
      Data from <a href="https://finance.yahoo.com" target="_blank" rel="noopener">Yahoo Finance</a> &mdash; no API key required
    </footer>
  </main>

</body>
</html>
"""


if __name__ == '__main__':
    stocks = []
    for t in TICKERS:
        try:
            s = fetch_quote(t)
            stocks.append(s)
            print(f"  OK  {t}: ${s['price']:.2f}", file=sys.stderr)
        except Exception as e:
            print(f"  ERR {t}: {e}", file=sys.stderr)

    if len(stocks) != len(TICKERS):
        print("ERROR: some tickers failed to fetch", file=sys.stderr)
        sys.exit(1)

    now_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    html = build_html(stocks, now_utc)

    out_path = sys.argv[1] if len(sys.argv) > 1 else 'tickers.html'
    with open(out_path, 'w') as f:
        f.write(html)

    print(f"Written: {out_path}", file=sys.stderr)
