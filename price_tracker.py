import re, requests, datetime, smtplib, nest_asyncio, json
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import gspread
from requests_html import AsyncHTMLSession
from oauth2client.service_account import ServiceAccountCredentials
from email.mime.text import MIMEText

# --------------------------------------------------------------------------
EMAIL_TO   = "shannonjryan@gmail.com"
EMAIL_FROM = "shannonjryan@gmail.com"
EMAIL_PASS = "kekt ympv fqgy trih"  # Gmail app password

# --------------------------------------------------------------------------
nest_asyncio.apply()
asession = AsyncHTMLSession()

# --------------------------------------------------------------------------
async def _scrape_price_async(url):
    domain = urlparse(url).netloc
    try:
        # --- Manny's ---
        if "mannys.com.au" in domain:
            r = await asession.get(url)
            await r.html.arender(timeout=20, sleep=2)
            tag = r.html.find("div.product-meta-container div.price-wrap p.selling-price", first=True)
            if tag: 
                return float(re.sub(r"[^\d.]", "", tag.text)) 
            return None

        # --- Derringers ---
        elif "derringers.com.au" in domain:
            r = await asession.get(url)
            await r.html.arender(timeout=20, sleep=2)
            tag = r.html.find("p.selling-price", first=True)
            if tag: 
                return float(re.sub(r"[^\d.]", "", tag.text))
            return None

        # --- Angkor Music ---
        elif "angkormusic.com.au" in domain:
            r = await asession.get(url)
            await r.html.arender(timeout=20, sleep=2)
            tag = r.html.find("div.productpromo[itemprop='price']", first=True)
            if tag and tag.attrs.get("content"):
                return float(tag.attrs["content"])
            return None

        # --- Musos Corner ---
        elif "musoscorner.com.au" in domain:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "html.parser")
            tag = soup.find("meta", {"property": "product:price:amount"})
            if tag and tag.get("content"):
                return float(tag["content"])
            return None

        # --- Better Music ---
        elif "bettermusic.com.au" in domain:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "html.parser")
            tag = soup.find("meta", {"property": "product:price:amount"})
            if tag and tag.get("content"):
                return float(tag["content"])
            return None

        # --- World of Music ---
        elif "worldofmusic.com.au" in domain:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "html.parser")
            tag = soup.find("meta", {"property": "product:price:amount"})
            if tag and tag.get("content"):
                return float(tag["content"])
            return None

        # --- Mega Music ---
        elif "megamusic.com.au" in domain or "megamusiconline.com.au" in domain:
            r = await asession.get(url)
            await r.html.arender(timeout=20, sleep=2)
            # Grab the number following the currency symbol
            tag = r.html.find(".woocommerce-Price-currencySymbol", first=True)
            if tag and tag.element.tail:
                text = tag.element.tail.strip().replace(",", "")
                if text:
                    return float(text)
            return None

        # elif "carlingfordmusic.com.au" in domain:
        #     r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        #     soup = BeautifulSoup(r.text, "html.parser")
        #     # Look for screen-reader text fallback
        #     tag = soup.find("span", class_="screen-reader-text")
        #     if tag:
        #         m = re.search(r"\$(\d[\d,.]*)", tag.text)
        #         if m:
        #             return float(m.group(1).replace(",", ""))
        #     return None

        # elif "australiapianoworld.com.au" in domain or "houseofpianos.com.au" in domain:
        #     r = await asession.get(url)
        #     await r.html.arender(timeout=20, sleep=2)
        #     tag = r.html.find(".woocommerce-variation-price .woocommerce-Price-amount", first=True)
        #     if tag:
        #         return float(re.sub(r"[^\d.]", "", tag.text))
        #     return None

        elif "houseofpianos.com.au" in domain or "australiapianoworld.com.au" in domain or "carlingfordmusic.com.au" in domain:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "html.parser")
            # Look for the script with data-events containing productVariant
            script_tag = soup.find("script", attrs={"data-events": True})
            if script_tag:
                try:
                    data_events = json.loads(script_tag["data-events"].replace("&quot;", '"'))
                    for event in data_events:
                        if isinstance(event, list) and event[0] == "product_viewed":
                            price = event[1]["productVariant"]["price"]["amount"]
                            return float(price)
                except Exception:
                    pass
            return None        

        elif "amazon.com.au" in domain:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "html.parser")
            
            # Try first input by name
            tag = soup.find("input", {"name": "items[0.base][customerVisiblePrice][amount]"})
            if tag and tag.get("value"):
                return float(tag["value"])
            
            # Try second input by id
            tag = soup.find("input", {"id": "twister-plus-price-data-price"})
            if tag and tag.get("value"):
                return float(tag["value"])
            
            return None

        # --- Generic --- 
        else: 
            r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}) 
            soup = BeautifulSoup(r.text, "html.parser") 
            # Meta tags 
            tag = soup.find("meta", {"property": "product:price:amount"}) 
            if tag and tag.get("content"): return float(tag["content"]) 
            tag = soup.find("meta", {"itemprop": "price"}) 
            if tag and tag.get("content"): return float(tag["content"]) 
            # JSON-LD 
            for script in soup.find_all("script", type="application/ld+json"): 
                try: 
                    data = json.loads(script.string) 
                    if isinstance(data, list): 
                        for item in data: 
                            if "offers" in item and "price" in item["offers"]: 
                                return float(item["offers"]["price"]) 
                    elif isinstance(data, dict): 
                        if "offers" in data and "price" in data["offers"]: 
                            return float(data["offers"]["price"]) 
                except Exception: 
                    continue 
            # Last-resort 
            tag = soup.select_one(".price, .selling-price") 
            if tag: return float(re.sub(r"[^\d.]", "", tag.get_text(strip=True))) 

    except Exception as e:
        print("⚠️ Error scraping", url, ":", e)
    return None



# --------------------------------------------------------------------------
def scrape_price(url):
    """Synchronous wrapper for async scraper."""
    try:
        # Run the async scraper
        result = asession.run(lambda: _scrape_price_async(url))[0]
        # Return "N/A" if None
        return result if result is not None else "N/A"
    except Exception as e:
        print("⚠️ Error in scrape_price for", url, ":", e)
        return "N/A"


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
def send_email_if_new_low(sheet):
    all_values = sheet.get_all_values()
    alerts = []

    # skip header row
    for row in all_values[1:]:
        retailer_name = row[0]
        price_history = []
        for val in row[2:]:
            try:
                price_history.append(float(val.replace(",", "")))
            except:
                continue

        if len(price_history) < 2:
            continue

        previous_min = min(price_history[:-1])
        latest_price = price_history[-1]

        if latest_price < previous_min:
            alerts.append(
                f"{retailer_name} has a new low price: ${latest_price:.2f} "
                f"(previous low: ${previous_min:.2f})"
            )

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
        sheet.update(
            f"{gspread.utils.rowcol_to_a1(2, next_col)}:"
            f"{gspread.utils.rowcol_to_a1(1 + len(values), next_col)}",
            values,
        )

        # Check for new lows
        send_email_if_new_low(sheet)


# --------------------------------------------------------------------------
if __name__ == "__main__":
    main()
