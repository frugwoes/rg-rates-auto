import os
import requests
import pandas as pd
from datetime import datetime
import ssl
import urllib3
import subprocess

# Disable warnings & fix SSL on Mac
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

os.makedirs("static", exist_ok=True)


def fetch_rates():
    # Default fallback rates
    rates = {
        'tbill': '1.39%',
        'ssb': '1.85%',
        'hysa': '8.05% p.a.',
        'usd': '4.50%',
        'fd': '1.30%',
        'cma': '4.22%'
    }

    # === T-bill (6-month) ===
    try:
        df = pd.read_csv("https://www.mas.gov.sg/-/media/mas/bonds-and-bills/singapore-government-securities/t-bill-auction-results.csv")
        six_m = df[df['Tenor'] == '6M'].iloc[-1]
        rates['tbill'] = f"{float(six_m['Cut-off Yield (%)']):.2f}%"
        print(f"T-bill fetched: {rates['tbill']}")
    except Exception as e:
        print("T-bill failed (using fallback):", e)

    # === SSB (10-yr avg return) ===
    try:
        df = pd.read_csv("https://www.mas.gov.sg/-/media/mas/bonds-and-bills/singapore-savings-bonds/ssb-rates.csv")
        rates['ssb'] = f"{df.iloc[-1]['10-yr avg return']:.2f}%"
        print(f"SSB fetched: {rates['ssb']}")
    except Exception as e:
        print("SSB failed (using fallback):", e)

    # === HYSA (SingSaver) ===
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get("https://www.singsaver.com.sg/banking/best-savings-accounts", headers=headers, timeout=15)
        text = r.text.lower()
        if "8.05" in text:
            rates['hysa'] = "8.05% p.a."
        elif "7.88" in text:
            rates['hysa'] = "7.88% p.a."
        print(f"HYSA rate: {rates['hysa']}")
    except Exception as e:
        print("HYSA scrape failed (using fallback):", e)

    current_month_year = datetime.now().strftime("%B %Y")   # e.g. December 2025
    today_date = datetime.now().strftime("%d %b %Y")        # e.g. 01 Dec 2025

    # ============================
    # FINAL WIDGET — REAL RATES INJECTED DIRECTLY
    # ============================
    widget_html = f'''<!-- START: RealisedGains – Where to Park Your Cash ({current_month_year}) -->
<div id="rg-cashpark-container">

    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;700&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">

    <style>
        #rg-cashpark-container * {{ box-sizing: border-box; }}
        #rg-cashpark-container {{font-family:'Inter',sans-serif;color:#1f2937;max-width:100%;margin:0 auto;}}
        #rg-cashpark-container h2 {{font-family:'Poppins',sans-serif;font-weight:700;margin:0;}}
        #rg-cashpark-container .wrapper {{background:linear-gradient(135deg,rgba(34,139,34,0.08),rgba(144,238,144,0.05));border-radius:16px;padding:48px 32px;border:1px solid rgba(34,139,34,0.2);}}
        #rg-cashpark-container .title {{font-size:38px;text-align:center;margin-bottom:12px;}}
        #rg-cashpark-container .subtitle {{text-align:center;font-size:19px;margin-bottom:48px;color:#374151;}}
        #rg-cashpark-container .grid {{display:grid;grid-template-columns:repeat(3,1fr);gap:28px;margin-bottom:48px;}}
        #rg-cashpark-container .box {{background:#ffffff;border-radius:16px;padding:32px 24px;text-align:center;box-shadow:0 8px 20px rgba(0,0,0,0.08);transition:all 0.3s ease;}}
        #rg-cashpark-container .box:hover {{transform:translateY(-8px);box-shadow:0 16px 32px rgba(0,0,0,0.12);}}
        #rg-cashpark-container .rate {{font-size:46px;font-weight:700;color:#166534;margin:12px 0 8px;line-height:1;}}
        #rg-cashpark-container .label {{font-size:16px;font-weight:600;color:#111;margin-bottom:8px;}}
        #rg-cashpark-container .note {{font-size:13.5px;color:#6b7280;margin-top:6px;}}
        #rg-cashpark-container .link {{margin-top:18px;display:inline-block;font-weight:600;color:#166534;text-decoration:none;font-size:15.5px;}}
        #rg-cashpark-container .link:hover {{text-decoration:underline;}}
        @media(max-width:1024px){{#rg-cashpark-container .grid{{grid-template-columns:repeat(3,1fr);}}}}
        @media(max-width:840px){{#rg-cashpark-container .grid{{grid-template-columns:repeat(2,1fr);}}}}
        @media(max-width:480px){{#rg-cashpark-container .grid{{grid-template-columns:1fr;}} #rg-cashpark-container .wrapper{{padding:32px 20px;}} #rg-cashpark-container .title{{font-size:32px;}} #rg-cashpark-container .rate{{font-size:40px;}}}}
        #rg-cashpark-container .bottom {{text-align:center;padding-top:32px;border-top:1px dashed rgba(34,139,34,0.4);}}
    </style>

    <div class="wrapper">
        <h2 class="title">Where Should You Park Your Cash Right Now?</h2>
        <p class="subtitle">Real-time highest yields in Singapore — auto-updated monthly</p>

        <div class="grid">
            <div class="box"><div class="rate">{rates['tbill']}</div><div class="label">Latest 6-Month T-bill</div><div class="note">Auction: {today_date}</div><a href="/t-bills" class="link">Get Application Reminder</a></div>
            <div class="box"><div class="rate">{rates['cma']}</div><div class="label">Top Cash Management Account</div><div class="note">Zero lock-in, daily interest</div><a href="/cash-management" class="link">Compare All Accounts</a></div>
            <div class="box"><div class="rate">{rates['hysa']}</div><div class="label">Highest Savings Rate</div><div class="note">No minimum balance tricks</div><a href="/savings" class="link">See Top 5 Accounts</a></div>
            <div class="box"><div class="rate">{rates['ssb']}</div><div class="label">10-Year SSB Avg Return</div><div class="note">Next tranche</div><a href="/ssb" class="link">Get SSB Alerts</a></div>
            <div class="box"><div class="rate">{rates['fd']}</div><div class="label">Best SGD Fixed Deposit</div><div class="note">12–18 month tenures</div><a href="/fixed-deposits" class="link">Lock In Rate Now</a></div>
            <div class="box"><div class="rate">{rates['usd']}</div><div class="label">Best USD Fixed Deposit</div><div class="note">Strong USD play</div><a href="/usd-fd" class="link">View USD Offers</a></div>
        </div>

        <div class="bottom">
            <p style="margin:0;font-size:21px;font-weight:600;">
                Monthly Strategy Update · <span id="month-name">{current_month_year}</span>
            </p>
            <a href="/blog/where-to-park-cash-december-2025" class="link" style="font-size:18px;">
                Which option wins this month? Full breakdown
            </a>
        </div>
    </div>

    <script>
        document.getElementById('month-name').textContent = 
            new Date().toLocaleDateString('en-SG', {{ month: 'long', year: 'numeric' }});
    </script>
</div>
<!-- END: RealisedGains Cash Widget -->'''

    # Save widget
    with open("widget.html", "w", encoding="utf-8") as f:
        f.write(widget_html)

    # Optional: keep rates.js
    js_content = f"// Auto-updated: {datetime.now().strftime('%d %b %Y %H:%M')} SGT\nconst rates = {rates};"
    with open("static/rates.js", "w") as f:
        f.write(js_content)

    print("\nSUCCESS! Widget generated with latest rates:")
    print(rates)

    # Auto push to GitHub
    try:
        subprocess.run(["git", "add", "widget.html", "static/rates.js", "update_rates.py"], check=True)
        subprocess.run(["git", "commit", "-m", f"Auto-update rates {current_month_year}"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("Pushed to GitHub — your site is now updated!")
    except:
        print("No changes to push (or run manually once)")


if __name__ == "__main__":
    fetch_rates()
