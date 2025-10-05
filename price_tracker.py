import nest_asyncio
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import json
from requests_html import AsyncHTMLSession

# --------------------------------------------------------------------------
nest_asyncio.apply()
asession = AsyncHTMLSession()

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

        # --- Mega Music ---
        elif "megamusic.com.au" in domain or "megamusiconline.com.au" in domain:
            r = await asession.get(url)
            await r.html.arender(timeout=20, sleep=2)
            tag = r.html.find(".product-info-price .price", first=True)
            if tag:
                return float(re.sub(r"[^\d.]", "", tag.text))
            return None

        # --- Musos Corner ---
        elif "musoscorner.com.au" in domain:
            r = await asession.get(url)
            await r.html.arender(timeout=20, sleep=2)
            tag = r.html.find(".price .amount", first=True)
            if tag:
                return float(re.sub(r"[^\d.]", "", tag.text))
            return None

        # --- Guitar World ---
        elif "guitarworld.com.au" in domain:
            r = await asession.get(url)
            await r.html.arender(timeout=20, sleep=2)
            tag = r.html.find(".price-new, .woocommerce-Price-amount", first=True)
            if tag:
                return float(re.sub(r"[^\d.]", "", tag.text))
            return None

        # --- World of Music ---
        elif "worldofmusic.com.au" in domain:
            r = await asession.get(url)
            await r.html.arender(timeout=20, sleep=2)
            tag = r.html.find("span.price .amount", first=True)
            if tag:
                return float(re.sub(r"[^\d.]", "", tag.text))
            return None

        # --- Better Music ---
        elif "bettermusic.com.au" in domain:
            r = await asession.get(url)
            await r.html.arender(timeout=20, sleep=2)
            tag = r.html.find("div.price span.woocommerce-Price-amount", first=True)
            if tag:
                return float(re.sub(r"[^\d.]", "", tag.text))
            return None

        # --- Generic Fallback ---
        else:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "html.parser")

            # Meta tags
            tag = soup.find("meta", {"property": "product:price:amount"})
            if tag and tag.get("content"):
                return float(tag["content"])
            tag = soup.find("meta", {"itemprop": "price"})
            if tag and tag.get("content"):
                return float(tag["content"])

            # JSON-LD structured data
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    data = json.loads(script.string)
                    if isinstance(data, list):
                        for item in data:
                            if "offers" in item and "price" in item["offers"]:
                                return float(item["offers"]["price"])
                    elif isinstance(data, dict):
                        if "offers" in data and "price" in data["offers"]:
