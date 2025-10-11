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
# async def _scrape_price_async(url):
#     domain = urlparse(url).netloc
#     try:
#         # --- Manny's ---
#         if "mannys.com.au" in domain:
#             r = await asession.get(url)
#             await r.html.arender(timeout=20, sleep=2)
#             tag = r.html.find("div.product-meta-container div.price-wrap p.selling-price", first=True)
#             if tag: 
#                 return float(re.sub(r"[^\d.]", "", tag.text)) 
#             return None

#         # --- Derringers ---
#         elif "derringers.com.au" in domain:
#             r = await asession.get(url)
#             await r.html.arender(timeout=20, sleep=2)
#             tag = r.html.find("p.selling-price", first=True)
#             if tag: 
#                 return float(re.sub(r"[^\d.]", "", tag.text))
#             return None

#         # --- Angkor Music ---
#         elif "angkormusic.com.au" in domain:
#             r = await asession.get(url)
#             await r.html.arender(timeout=20, sleep=2)
#             tag = r.html.find("div.productpromo[itemprop='price']", first=True)
#             if tag and tag.attrs.get("content"):
#                 return float(tag.attrs["content"])
#             return None

#         # --- Musos Corner ---
#         elif "musoscorner.com.au" in domain:
#             r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#             soup = BeautifulSoup(r.text, "html.parser")
#             tag = soup.find("meta", {"property": "product:price:amount"})
#             if tag and tag.get("content"):
#                 return float(tag["content"])
#             return None

#         # --- Better Music ---
#         elif "bettermusic.com.au" in domain:
#             r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#             soup = BeautifulSoup(r.text, "html.parser")
#             tag = soup.find("meta", {"property": "product:price:amount"})
#             if tag and tag.get("content"):
#                 return float(tag["content"])
#             return None

#         # --- World of Music ---
#         elif "worldofmusic.com.au" in domain:
#             r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#             soup = BeautifulSoup(r.text, "html.parser")
#             tag = soup.find("meta", {"property": "product:price:amount"})
#             if tag and tag.get("content"):
#                 return float(tag["content"])
#             return None

#         # --- Mega Music ---
#         elif "megamusic.com.au" in domain or "megamusiconline.com.au" in domain:
#             r = await asession.get(url)
#             await r.html.arender(timeout=20, sleep=2)
#             # Grab the number following the currency symbol
#             tag = r.html.find(".woocommerce-Price-currencySymbol", first=True)
#             if tag and tag.element.tail:
#                 text = tag.element.tail.strip().replace(",", "")
#                 if text:
#                     return float(text)
#             return None

#         # --- Carlingford Music ---
#         elif "carlingfordmusic.com.au" in domain:
#             r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#             soup = BeautifulSoup(r.text, "html.parser")
#             tag = soup.find("input", {"name": "gtm4wp_product_data"})
#             if tag and tag.get("value"):
#                 try:
#                     data = json.loads(tag["value"].replace("&quot;", '"'))
#                     return float(data.get("price"))
#                 except:
#                     return None
#             return None

#         # --- Australian Piano World ---
#         elif "australiapianoworld.com.au" in domain:
#             r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#             soup = BeautifulSoup(r.text, "html.parser")

#             # Meta tag first
#             tag = soup.find("meta", {"property": "product:price:amount"})
#             if tag and tag.get("content"):
#                 return float(tag["content"])

#             # Visible WooCommerce price span
#             tag = soup.select_one(".woocommerce-Price-amount bdi")
#             if tag:
#                 return float(re.sub(r"[^\d.]", "", tag.get_text(strip=True)))

#             return None

#         # --- Amazon Australia ---
#         elif "amazon.com.au" in domain:
#             r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#             soup = BeautifulSoup(r.text, "html.parser")

#             # Try meta itemprop
#             tag = soup.find("meta", {"itemprop": "price"})
#             if tag and tag.get("content"):
#                 return float(tag["content"])

#             # Try visible price spans
#             whole = soup.find("span", class_="a-price-whole")
#             frac = soup.find("span", class_="a-price-fraction")
#             if whole:
#                 price_text = whole.text.replace(",", "")
#                 if frac:
#                     price_text += "." + frac.text
#                 try:
#                     return float(price_text)
#                 except:
#                     pass

#             return None

#         # --- Scarlett Music ---
#         elif "scarlettmusic.com.au" in domain:
#             r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#             soup = BeautifulSoup(r.text, "html.parser")
#             tag = soup.find("meta", {"property": "og:price:amount"})
#             if tag and tag.get("content"):
#                 return float(tag["content"])
#             tag = soup.select_one(".money")
#             if tag:
#                 return float(re.sub(r"[^\d.]", "", tag.text))
#             return None

#         # --- House of Pianos ---
#         elif "houseofpianos.com.au" in domain:
#             r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#             soup = BeautifulSoup(r.text, "html.parser")
#             tag = soup.find("meta", {"property": "og:price:amount"})
#             if tag and tag.get("content"):
#                 return float(tag["content"])
#             tag = soup.select_one(".price-item--regular")
#             if tag:
#                 return float(re.sub(r"[^\d.]", "", tag.text))
#             return None

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
#         print("⚠️ Error scraping", url, ":", e)
#     return None


async def _scrape_price_async(url, debug=False):
    """
    Robust price extractor:
      - Uses asession.get(...) and attempts r.html.arender(...)
      - Checks meta tags, itemprop, JSON-LD, common price selectors
      - Looks for hidden inputs and Amazon price spans
      - Falls back to regex scanning of $ amounts with heuristics
    Set debug=True to print candidates and save debug_<domain>.html for inspection.
    """
    from bs4 import BeautifulSoup
    import json, re, os

    domain = urlparse(url).netloc
    try:
        # fetch + try to render (render may fail silently in some envs)
        r = await asession.get(url)
        try:
            await r.html.arender(timeout=30, sleep=2)
        except Exception as e:
            if debug:
                print(f"[debug] render failed for {domain}: {e}")

        html = r.html.html if getattr(r, "html", None) and r.html.html else (r.text if hasattr(r, "text") else "")
        soup = BeautifulSoup(html, "html.parser")

        # 1) common meta tags
        for prop in ("product:price:amount", "og:price:amount"):
            tag = soup.find("meta", {"property": prop})
            if tag and tag.get("content"):
                try:
                    return float(str(tag["content"]).replace(",", ""))
                except:
                    pass

        tag = soup.find("meta", {"itemprop": "price"})
        if tag and tag.get("content"):
            try:
                return float(str(tag["content"]).replace(",", ""))
            except:
                pass

        # 2) application/ld+json (JSON-LD) - many sites put offers.price here
        for script in soup.find_all("script", type="application/ld+json"):
            text = script.string or script.get_text() or ""
            try:
                data = json.loads(text)
            except Exception:
                continue

            def find_price(obj):
                # Look for offers.price, price, priceSpecification.price
                if isinstance(obj, dict):
                    if "offers" in obj:
                        offers = obj["offers"]
                        if isinstance(offers, dict) and offers.get("price"):
                            return offers.get("price")
                        if isinstance(offers, list):
                            for o in offers:
                                if isinstance(o, dict) and o.get("price"):
                                    return o.get("price")
                    # some schemas use priceSpecification
                    if "priceSpecification" in obj:
                        ps = obj["priceSpecification"]
                        if isinstance(ps, dict) and ps.get("price"):
                            return ps.get("price")
                    if obj.get("price"):
                        return obj.get("price")
                elif isinstance(obj, list):
                    for it in obj:
                        val = find_price(it)
                        if val:
                            return val
                return None

            price_val = find_price(data)
            if price_val:
                try:
                    return float(str(price_val).replace(",", ""))
                except:
                    pass

        # 3) Amazon hidden inputs (legacy) and other hidden price inputs
        # try both rendered html selectors (requests_html) and BeautifulSoup
        # input#twister-plus-price-data-price
        try:
            inp = r.html.find("input#twister-plus-price-data-price", first=True)
            if inp and inp.attrs.get("value"):
                return float(inp.attrs["value"])
        except Exception:
            pass

        try:
            inp2 = r.html.find("input[name*='customerVisiblePrice']", first=True)
            if inp2 and inp2.attrs.get("value"):
                return float(inp2.attrs["value"])
        except Exception:
            pass

        # 4) Amazon visible price parts
        whole = soup.find("span", class_="a-price-whole")
        frac = soup.find("span", class_="a-price-fraction")
        if whole:
            price_text = whole.get_text(strip=True).replace(",", "")
            if frac:
                price_text += "." + frac.get_text(strip=True)
            try:
                return float(price_text)
            except:
                pass

        # 5) common visible selectors (Shopify/WooCommerce/etc)
        common_selectors = [
            "meta[property='product:price:amount']",
            "meta[property='og:price:amount']",
            "meta[itemprop='price']",
            ".woocommerce-Price-amount bdi",
            ".woocommerce-Price-amount",
            ".price-item--regular",
            ".money",
            ".price",
            ".selling-price",
            ".price .amount",
            ".price .woocommerce-Price-amount",
            ".price .amount bdi",
            ".price .amount",
            ".product-price",
            ".product-meta .price",
            ".productpromo[itemprop='price']",
        ]
        for sel in common_selectors:
            try:
                tag = soup.select_one(sel)
                if tag:
                    text = tag.get_text(strip=True) if hasattr(tag, "get_text") else (tag.attrs.get("content") if tag.attrs.get("content") else "")
                    m = re.search(r"(\d[\d,]*(?:\.\d+)?)", text)
                    if m:
                        return float(m.group(1).replace(",", ""))
            except Exception:
                continue

        # 6) Look inside scripts for JSON-like price fields: "price": "1234.00" or "price": 1234.00
        m = re.search(r'"price"\s*:\s*"([\d,]+(?:\.\d+)?)"', html)
        if m:
            return float(m.group(1).replace(",", ""))
        m = re.search(r'"price"\s*:\s*([0-9]+(?:\.[0-9]+)?)', html)
        if m:
            return float(m.group(1))

        # 7) Generic currency scan fallback: find all $ amounts and choose a reasonable candidate
        amounts = re.findall(r"\$\s?([\d,]+(?:\.\d{2})?)", html)
        candidates = [float(a.replace(",", "")) for a in amounts]
        # Filter to sensible product-price range, then choose median as heuristic
        candidates = [c for c in candidates if 10 <= c <= 20000]
        if candidates:
            candidates.sort()
            mid = candidates[len(candidates)//2]
            return float(mid)

        # nothing found
        if debug:
            # Save debug HTML and some quick information
            try:
                fname = f"debug_{domain.replace('.', '_')}.html"
                with open(fname, "w", encoding="utf-8") as fh:
                    fh.write(html)
                print(f"[debug] saved HTML to {fname}")
            except Exception as e:
                print(f"[debug] couldn't save HTML: {e}")
            print(f"[debug] total $-like candidates found on page: {len(amounts)} -> {amounts[:10]}")
            # show short snippet around first price-like match
            m2 = re.search(r"(.{0,120}\$\s?[\d,]+(?:\.\d{2})?.{0,120})", html)
            if m2:
                print("[debug] snippet:", m2.group(1))
        return None

    except Exception as e:
        if debug:
            print("⚠️ Exception in robust scraper for", url, ":", e)
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
# if __name__ == "__main__":
    # main()
    # Temporary debug-run (remove after)
if __name__ == "__main__":
    import asyncio
    test_urls = [
        "https://www.scarlettmusic.com.au/kawai-es120sb-portable-digital-piano-bundle-with-s",
        "https://www.scarlettmusic.com.au/kawai-es120b-portable-digital-piano-black",
        "https://australiapianoworld.com.au/product/pianos/kawai/kawai-es120/",
        "https://houseofpianos.com.au/products/kawai-es120-digital-piano",
        "https://www.amazon.com.au/Kawai-Weighted-Portable-Digital-Including/dp/B0CXPZLZS1",
        "https://www.amazon.com.au/Kawai-ES120-Weighted-Portable-Digital/dp/B0BMZ4PZHP"
    ]
    async def run_tests():
        for u in test_urls:
            print("\n--- TEST:", u)
            price = await _scrape_price_async(u, debug=True)
            print("-> price:", price)
    asyncio.get_event_loop().run_until_complete(run_tests())

