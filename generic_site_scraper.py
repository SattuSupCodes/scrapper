from playwright.sync_api import sync_playwright
import re
from urllib.parse import urlparse, urljoin
import json
from datetime import datetime
import os


INTERNAL_KEYWORDS = ["about", "contact", "company", "products", "services"]
MAX_INTERNAL_PAGES = 5
MAX_IMAGES = 20


def scrape_page_basic(page, url):
    """Scrape basic content from a single page"""
    page.goto(url, timeout=60000)
    page.wait_for_timeout(2000)

    return {
        "url": url,
        "title": page.title(),
        "meta_description": page.locator(
            "meta[name='description']"
        ).get_attribute("content"),
        "headings": {
            "h1": page.locator("h1").all_inner_texts(),
            "h2": page.locator("h2").all_inner_texts(),
            "h3": page.locator("h3").all_inner_texts()
        },
        "text_sample": page.locator("body").inner_text()[:3000]
    }


def scrape_company_site(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(3000)

        parsed = urlparse(url)
        base_domain = parsed.netloc

        data = {}

        # ---- Core metadata ----
        data["domain"] = base_domain
        data["source_url"] = url
        data["scraped_at"] = datetime.utcnow().isoformat()

        data["title"] = page.title()
        data["meta_description"] = page.locator(
            "meta[name='description']"
        ).get_attribute("content")

        # ---- Emails ----
        html = page.content()
        data["emails"] = list(set(re.findall(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            html
        )))

        # ---- Social links ----
        data["socials"] = {
            "linkedin": None,
            "twitter": None,
            "instagram": None
        }

        all_links = page.locator("a[href]").all()
        hrefs = []

        for link in all_links:
            href = link.get_attribute("href")
            if not href:
                continue

            full_url = urljoin(url, href)
            hrefs.append(full_url)

            if "linkedin.com" in href:
                data["socials"]["linkedin"] = href
            elif "twitter.com" in href or "x.com" in href:
                data["socials"]["twitter"] = href
            elif "instagram.com" in href:
                data["socials"]["instagram"] = href

        # ---- Images ----
        images = page.locator("img[src]").evaluate_all(
            """imgs => imgs.map(img => img.src).filter(src => src).slice(0, %d)""" % MAX_IMAGES
        )
        data["images"] = images

        # ---- Internal pages ----
        internal_pages = []
        visited = set()

        for link in hrefs:
            if len(internal_pages) >= MAX_INTERNAL_PAGES:
                break

            parsed_link = urlparse(link)

            if parsed_link.netloc != base_domain:
                continue

            if any(k in parsed_link.path.lower() for k in INTERNAL_KEYWORDS):
                if link in visited:
                    continue

                visited.add(link)

                try:
                    internal_pages.append(
                        scrape_page_basic(page, link)
                    )
                except:
                    continue

        data["internal_pages"] = internal_pages

        # ---- Save JSON ----
        os.makedirs("data", exist_ok=True)
        file_name = base_domain.replace(".", "_") + ".json"
        file_path = os.path.join("data", file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\nSaved enriched data → {file_path}")
        browser.close()


if __name__ == "__main__":
    scrape_company_site("https://www.meta.com/")
