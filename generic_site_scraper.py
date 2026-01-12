from playwright.sync_api import sync_playwright
import re
from urllib.parse import urlparse
import json
from datetime import datetime
import os


def scrape_company_site(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(3000)

        data = {}

        # ---- Domain ----
        parsed = urlparse(url)
        data["domain"] = parsed.netloc

        # ---- Title ----
        try:
            data["title"] = page.title()
        except:
            data["title"] = None

        # ---- Meta description ----
        try:
            desc = page.locator("meta[name='description']").get_attribute("content")
            data["meta_description"] = desc
        except:
            data["meta_description"] = None

        # ---- Emails ----
        html = page.content()
        emails = list(set(re.findall(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            html
        )))
        data["emails"] = emails

        # ---- Social links ----
        socials = {
            "linkedin": None,
            "twitter": None,
            "instagram": None
        }

        links = page.locator("a[href]").all()
        for link in links:
            href = link.get_attribute("href")
            if not href:
                continue
            if "linkedin.com" in href:
                socials["linkedin"] = href
            elif "twitter.com" in href or "x.com" in href:
                socials["twitter"] = href
            elif "instagram.com" in href:
                socials["instagram"] = href

        data["socials"] = socials

        # ---- Metadata ----
        data["scraped_at"] = datetime.utcnow().isoformat()
        data["source_url"] = url

        # ---- Save to JSON file ----
        os.makedirs("data", exist_ok=True)

        file_name = parsed.netloc.replace(".", "_") + ".json"
        file_path = os.path.join("data", file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print("\nSCRAPED WEBSITE DATA\n")
        print(json.dumps(data, indent=2))
        print(f"\nSaved to {file_path}")

        browser.close()


if __name__ == "__main__":
    scrape_company_site("https://copic.jp/en/")
