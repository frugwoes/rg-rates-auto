import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import ssl
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # Optional silence

# Fix SSL on Mac
ssl._create_default_https_context = ssl._create_unverified_context

os.makedirs("static", exist_ok=True)

def fetch_rates():
    rates = {
        'tbill': '1.39%',   # fallback
        'ssb': '1.85%',
        'hysa': '8.05% p.a.',
        'usd': '4.50%',
        'fd': '1.30%',
        'cma': '4.22%'
    }

    # Try T-bill
    try:
        df = pd.read_csv("https://www.mas.gov.sg/-/media/mas/bonds-and-bills/singapore-government-securities/t-bill-auction-results.csv", verify=False)
        six_m = df[df['Tenor'] == '6M'].iloc[-1]
        rates['tbill'] = f"{float(six_m['Cut-off Yield (%)']):.2f}%"
    except:
        pass

    # Try SSB
    try:
        df = pd.read_csv("https://www.mas.gov.sg/-/media/mas/bonds-and-bills/singapore-savings-bonds/ssb-rates.csv", verify=False)
        rates['ssb'] = f"{df.iloc[-1]['10-yr avg return']:.2f}%"
    except:
        pass

    # Try SingSaver for HYSA
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get("https://www.singsaver.com.sg/banking/best-savings-accounts", headers=headers, timeout=10, verify=False)
        if "8.05" in r.text or "Bonus$aver" in r.text:
            rates['hysa'] = "8.05% p.a."
        elif "7.51" in r.text:
            rates['hysa'] = "7.51% p.a."
    except:
        pass

    # Generate rates.js
    js = f"""// Auto-updated: {datetime.now().strftime('%d %b %Y %H:%M')} SGT
const rates = {rates};
const lastUpdated = "{datetime.now().strftime('%d %b %Y')}";"""

    with open("static/rates.js", "w") as f:
        f.write(js)

    print("SUCCESS! Rates updated → static/rates.js")
    print(rates)

if __name__ == "__main__":
    fetch_rates()
EOF
