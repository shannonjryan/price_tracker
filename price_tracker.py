import re, requests, datetime, smtplib, nest_asyncio, json
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import gspread
from requests_html import AsyncHTMLSession
from oauth2client.service_account import ServiceAccountCredentials
from email.mime.text import MIMEText


# -------- CONFIG --------
# PRODUCTS = [
#     {"name": "Mannys", "url": "https://www.mannys.com.au/products/roland-td-17kv-2-v-drums-drum-kit"},
#     {"name": "Musos Corner", "url": "https://www.musoscorner.com.au/roland-td-17kv2-v-drums-electric-drum-kit"},
#     {"name": "Angkor Music", "url": "https://www.angkormusic.com.au/roland-td-17kv2s-v-drums-series-2-electronic-drum"},
#     {"name": "Guitar World", "url": "https://guitar.com.au/roland-td17kv2s-v-drums-electronic-drumkit"},
#     {"name": "Better Music", "url": "https://www.bettermusic.com.au/roland-td-17kv2s-v-drums-electronic-drum-kit"},
#     {"name": "Mega Music", "url": "https://www.megamusiconline.com.au/product/roland-td-17kv2-v-drums-electronic-drum-kit-td17kv2"},
#     {"name": "World of Music", "url": "https://www.worldofmusic.com.au/drums/electronic-drum-kits/roland-td-17kv2-v-drums-electronic-drum-kit"},
#     {"name": "Derringers Music", "url": "https://www.derringers.com.au/products/roland-td-17kv2-v-drums-series-2-electric-drum-kit"}
# ]

# SPREADSHEET_NAME = "Price Tracker"
# SHEET_NAME = "TD-17KV2"

EMAIL_TO   = "shannonjryan@gmail.com"
EMAIL_FROM = "shannonjryan@gmail.com"
EMAIL_PASS = "kekt ympv fqgy trih"  # Gmail app password

# --------------------------------------------------------------------------
# nest_asyncio.apply()
# asession = AsyncHTMLSession()

# async def _scrape_price_async(url):
#     domain = urlparse(url).netloc
#     try:
#         # --- Manny's ---
#         if "mannys.com.au" in domain:
#             r = await asession.get(url)
#             await r.html.arender(timeout=20, sleep=2)
#             tag = r.html.find("div.product-meta-container div.price-wrap p.selling-price", first=True)
#             if tag: return float(re.sub(r"[^\d.]", "", tag.text))
#             return None

#         # --- Angkor Music ---
#         elif "angkormusic.com.au" in domain:
#             r = await asession.get(url)
#             await r.html.arender(timeout=20, sleep=2)
#             tag = r.html.find("div.productpromo[itemprop='price']", first=True)
#             if tag and tag.attrs.get("content"):
#                 return float(tag.attrs["content"])
#             return None

#         # --- Derringers ---
#         elif "derringers.com.au" in domain:
#             r = await asession.get(url)
#             await r.html.arender(timeout=20, sleep=2)
#             tag = r.html.find("p.selling-price", first=True)
#             if tag: return float(re.sub(r"[^\d.]", "", tag.text))

#         # --- Generic ---
#         else:
#             r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
#             soup = BeautifulSoup(r.text, "html.parser")
#             # Meta tags
#             tag = soup.find("meta", {"property": "product:price:amount"})
#             if tag and tag.get("content"): return float(tag["content"])
#             tag = soup.find("meta", {"itemprop": "price"})
#             if tag and tag.get("content"): return float(tag["content"])
#             # JSON-LD
#             for script in soup.find_all("script", type="application/ld+json"):
#                 try:
#                     data = json.loads(script.string)
#                     if isinstance(data, list):
#                         for item in data:
#                             if "offers" in item and "price" in item["offers"]:
#                                 return float(item["offers"]["price"])
#                     elif isinstance(data, dict):
#                         if "offers" in data and "price" in data["offers"]:
#                             return float(data["offers"]["price"])
#                 except Exception:
#                     continue
#             # Last-resort
#             tag = soup.select_one(".price, .selling-price")
#             if tag: return float(re.sub(r"[^\d.]", "", tag.get_text(strip=True)))
#     except Exception as e:
#         print("Error scraping", url, e)
#     return None

# --------------------------------------------------------------------------
# def scrape_price(url):
#     return asession.run(lambda: _scrape_price_async(url))[0]

# --------------------------------------------------------------------------
def extract_price(text):
    """Try to pull a numeric price (float) from text like '$2,149.00'."""
    if not text:
        return None
    match = re.search(r"(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", text)
    if match:
        try:
            return float(match.group(1).replace(",", ""))
        except ValueError:
            return None
    return None

# --------------------------------------------------------------------------
def scrape_price(url):
    """Scrape product price with site-specific selectors and sale-price preference."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        domain = urlparse(url).netloc

        def get_price_from_el(el):
            if not el: return None
            text = el.get("content") or el.get_text(strip=True)
            return extract_price(text)

        # --- Site-specific selectors ---
        if "mannys.com.au" in domain:
            el = soup.select_one("div.price-wrap p.selling-price")
            price = get_price_from_el(el)

        elif "derringers.com.au" in domain:
            el = soup.select_one("p.selling-price")
            price = get_price_from_el(el)

        elif "angkormusic.com.au" in domain:
            # There are both .productpromo (old) and .productpromo.sale (current)
            sale = soup.select_one("div.productpromo.sale[itemprop='price']")
            if sale:
                price = get_price_from_el(sale)
            else:
                el = soup.select_one("div.productpromo[itemprop='price']")
                price = get_price_from_el(el)

        elif "guitar.com.au" in domain:
            # Prefer sale span over RRP
            sale = soup.select_one("span.woocommerce-Price-amount.amount ins bdi")
            if not sale:
                sale = soup.select_one("ins .woocommerce-Price-amount")
            if sale:
                price = get_price_from_el(sale)
            else:
                el = soup.select_one(".woocommerce-Price-amount bdi")
                price = get_price_from_el(el)

        elif "musoscorner.com.au" in domain:
            # Sometimes hidden in script tag; extract from "price":"###"
            m = re.search(r'"price"\s*:\s*"(\d{1,4}(?:\.\d{2})?)"', r.text)
            price = float(m.group(1)) if m else None

        elif "megamusiconline.com.au" in domain:
            # Usually inside div.product-price > span.woocommerce-Price-amount
            sale = soup.select_one("p.price ins .woocommerce-Price-amount bdi")
            if sale:
                price = get_price_from_el(sale)
            else:
                el = soup.select_one("p.price .woocommerce-Price-amount bdi")
                price = get_price_from_el(el)

        else:
            price = None

        # --- Generic fallback if none of the above worked ---
        if not price:
            for sel in [
                "meta[property='product:price:amount']",
                "meta[itemprop='price'][content]",
                "div[itemprop='offers'] meta[itemprop='price']",
                ".price ins",
                ".price .amount",
                ".selling-price",
                ".product-price",
            ]:
                el = soup.select_one(sel)
                price = get_price_from_el(el)
                if price and 100 < price < 10000:
                    break

        # Regex fallback
        if not price:
            m = re.search(r"\$\s?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", soup.get_text())
            if m:
                price = float(m.group(1).replace(",", ""))

        if price and 100 < price < 10000:
            return price

    except Exception as e:
        print(f"Error scraping {url}: {e}")
    return None



# --------------------------------------------------------------------------
def log_to_sheet(rows, creds_json_path="price-tracker-credentials.json"):
    scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_json_path, scope)
    gc = gspread.authorize(creds)
    sheet = gc.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)

    # Determine next empty column
    header = sheet.row_values(1)
    next_col = len(header) + 1

    # Add date as column header
    timestamp = datetime.date.today().isoformat()
    sheet.update_cell(1, next_col, timestamp)

    # Write prices
    for i, row in enumerate(rows):
        sheet.update_cell(i + 2, next_col, row[2] or "N/A")  # row[2] is price

    return sheet

# --------------------------------------------------------------------------
def send_email(message):
    msg = MIMEText(message)
    msg["Subject"] = "Daily Price Alert - Roland TD17KV2"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, EMAIL_PASS)
        server.send_message(msg)

# --------------------------------------------------------------------------
def send_email_if_new_low(sheet, products):
    all_values = sheet.get_all_values()
    alerts = []

    for i, p in enumerate(products):
        row_idx = i + 2
        retailer_name = all_values[row_idx - 1][0]  # Column A
        prices = []
        for val in all_values[row_idx - 1][2:]:
            try: prices.append(float(val.replace(",", "")))
            except: continue
        if not prices: continue
        previous_min = min(prices[:-1]) if len(prices) > 1 else None
        latest_price = prices[-1]
        if previous_min is None or latest_price < previous_min:
            alerts.append(f"{retailer_name} has a new low price: ${latest_price} "
                          f"(previous low: ${previous_min if previous_min else 'N/A'})")
    if alerts:
        email_body = "⚡ New Lowest Price Detected! ⚡\n\n" + "\n".join(alerts)
        send_email(email_body)

# --------------------------------------------------------------------------
def main():
    # Load product definitions
    with open("config/products.json", "r") as f:
        products_list = json.load(f)

    # Authenticate once
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("price-tracker-credentials.json", scope)
    gc = gspread.authorize(creds)
    spreadsheet = gc.open("Price Tracker")

    for product in products_list:
        name = product["name"]
        sheet_name = product["sheet_name"]
        retailers = product["retailers"]

        print(f"\n🛒 Checking prices for: {name}")

        rows = []
        for r in retailers:
            price = scrape_price(r["url"])
            print(f"  {r['name']}: {price}")
            rows.append([r["name"], r["url"], price or "N/A"])

        # Log results to sheet
        try:
            sheet = spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            sheet = spreadsheet.add_worksheet(title=sheet_name, rows="100", cols="50")
            sheet.update("A1:C1", [["Retailer", "URL", "Price"]])

        # Determine next empty column
        header = sheet.row_values(1)
        next_col = len(header) + 1
        date_label = datetime.date.today().isoformat()
        sheet.update_cell(1, next_col, date_label)

        # Write prices
        values = [[r[2] or "N/A"] for r in rows]
        sheet.update(f"{gspread.utils.rowcol_to_a1(2, next_col)}:{gspread.utils.rowcol_to_a1(1 + len(values), next_col)}", values)


        # Check for new lows
        send_email_if_new_low(sheet, retailers)


# --------------------------------------------------------------------------
if __name__ == "__main__":
    main()
