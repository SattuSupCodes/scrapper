# from playwright.sync_api import sync_playwright
# import re
# from urllib.parse import urlparse, urljoin
# import json
# from datetime import datetime
# import os
# import random
# import time

# def human_delay(min_s=5, max_s=15):
#     delay = random.uniform(min_s,max_s)
#     time.sleep(delay)
# def long_delay():
#     delay = random.uniform(20,40)
#     time.sleep(delay)
# def human_scroll(page):
#     try:
#         for _ in range(random.randint(2,5)):
#             page.mouse.wheel(0, random.randint(300,800))
#             time.sleep(random.uniform(1.5,3.5))
#     except:
#         pass

# INTERNAL_KEYWORDS = ["about", "contact", "company", "products", "services"]
# MAX_INTERNAL_PAGES = 5
# MAX_IMAGES = 20


# def scrape_page_basic(page, url):
#     """Scrape basic content from a single page"""
#     page.goto(url, timeout=60000)
#     human_delay(6, 12)
#     human_scroll(page)
#     page.wait_for_timeout(2000)

#     return {
#         "url": url,
#         "title": page.title(),
#         "meta_description": page.locator(
#             "meta[name='description']"
#         ).get_attribute("content"),
#         "headings": {
#             "h1": page.locator("h1").all_inner_texts(),
#             "h2": page.locator("h2").all_inner_texts(),
#             "h3": page.locator("h3").all_inner_texts()
#         },
#         "text_sample": page.locator("body").inner_text()[:3000]
#     }

# # REVIEW_PLATFORMS = {
# #     "trustpilot": "https://www.trustpilot.com/search?query="
# #     # "yelp": "https://www.yelp.com/search?find_desc="
# # }

# # def discover_review_pages(page,company_name):
# #     found = {}
# #     for platform, base_url in REVIEW_PLATFORMS.items():
# #         try:
# #             long_delay()
# #             search_url = base_url + company_name
# #             page.goto(search_url, timeout = 60000)
# #             human_delay(8,15)
# #             human_scroll(page)
            
# #             for link in page.locator("a[href]").all():
# #                 href = link.get_attribute("href") or ""
# #                 if "/review/" in href:
# #                     found[platform]="https://www.trustpilot.com"+href
# #                     break
# #         except:
# #             continue
# #     return found
# # def find_rating(obj):
# #     if isinstance(obj, dict):
# #         if "aggregateRating" in obj:
# #             ar = obj["aggregateRating"]
# #             if isinstance(ar, dict):
# #                 return {"rating":ar.get("ratingValue"),
# #                         "review_count":ar.get("reviewCount")}
                
# #         for v in obj.values():
# #             result = find_rating(v)
# #             if result:
# #                 return result
# #     elif isinstance(obj, list):
# #         for item in obj:
# #             result = find_rating(item)
# #             if result:
# #                 return result
# #     return None

# # def scrape_trustpilot(page, url):
# #     page.goto(url, timeout=60000)
# #     human_delay(10, 20)
# #     human_scroll(page)

# #     try:
# #         page.locator("button:has-text('Accept')").click(timeout=5000)
# #     except:
# #         pass

# #     scripts = page.locator("script[type='application/ld+json']").all()

# #     for script in scripts:
# #         try:
# #             data = json.loads(script.inner_text())
# #             result = find_rating(data)
# #             if result:
# #                 return {
# #                     "source": "trustpilot",
# #                     "url": url,
# #                     "rating": result.get("rating"),
# #                     "review_count": result.get("review_count")
# #                 }
# #         except:
# #             continue
# # integration causes breakage of code. Hence commenting it out.
# #     return None

# def safe_meta_description(page):
#     try:
#         locator = page.locator("meta[name='description']")
#         if locator.count() > 0:
#             return locator.first.get_attribute("content")
#     except:
#         pass
#     return None
# def scrape_company_site(url):
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)
#         page = browser.new_page()
#         page.goto(url, timeout=60000)
#         human_delay(6, 12)
#         human_scroll(page)
#         page.wait_for_timeout(3000)

#         parsed = urlparse(url)
#         base_domain = parsed.netloc

#         data = {}

#         # ---- Core metadata ----
#         data["domain"] = base_domain
#         data["source_url"] = url
#         data["scraped_at"] = datetime.utcnow().isoformat()

#         data["title"] = page.title()
#         company_name = base_domain.replace("www.", "")if data["title"] else ""
#         data["review_pages"] = discover_review_pages(page, company_name)
#         data["reviews"]={}
#         data["meta_description"] = safe_meta_description(page)


#         # ---- Emails ----
#         html = page.content()
#         data["emails"] = list(set(re.findall(
#             r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
#             html
#         )))

#         # ---- Social links ----
#         data["socials"] = {
#             "linkedin": None,
#             "twitter": None,
#             "instagram": None
#         }

#         all_links = page.locator("a[href]").all()
#         hrefs = []

#         for link in all_links:
#             href = link.get_attribute("href")
#             if not href:
#                 continue

#             full_url = urljoin(url, href)
#             hrefs.append(full_url)

#             if "linkedin.com" in href:
#                 data["socials"]["linkedin"] = href
#             elif "twitter.com" in href or "x.com" in href:
#                 data["socials"]["twitter"] = href
#             elif "instagram.com" in href:
#                 data["socials"]["instagram"] = href

#         # ---- Images ----
#         images = page.locator("img[src]").evaluate_all(
#             """imgs => imgs.map(img => img.src).filter(src => src).slice(0, %d)""" % MAX_IMAGES
#         )
#         data["images"] = images

#         # ---- Internal pages ----
#         internal_pages = []
#         visited = set()

#         for link in hrefs:
#             if len(internal_pages) >= MAX_INTERNAL_PAGES:
#                 break

#             parsed_link = urlparse(link)

#             if parsed_link.netloc != base_domain:
#                 continue

#             if any(k in parsed_link.path.lower() for k in INTERNAL_KEYWORDS):
#                 if link in visited:
#                     continue

#                 visited.add(link)

#                 try:
#                     internal_pages.append(
#                         scrape_page_basic(page, link)
#                     )
#                 except:
#                     continue

#         data["internal_pages"] = internal_pages
#         if "trustpilot" in data["review_pages"]:
#             try:
#                data["reviews"]["trustpilot"] = scrape_trustpilot(
#                page,
#                data["review_pages"]["trustpilot"]
# )

#             except:
#                 data["reviews"]["trustpilot"] = None

#         # ---- Save JSON ----
#         os.makedirs("data", exist_ok=True)
#         file_name = base_domain.replace(".", "_") + ".json"
#         file_path = os.path.join("data", file_name)

#         with open(file_path, "w", encoding="utf-8") as f:
#             json.dump(data, f, indent=2, ensure_ascii=False)

#         print(f"\nSaved enriched data → {file_path}")
#         browser.close()


# if __name__ == "__main__":
#     website = input("Enter company url: ").strip()
#     scrape_company_site(website)
   
from playwright.sync_api import sync_playwright
import re
from urllib.parse import urlparse, urljoin
import json
from datetime import datetime
import os
import time, random

def human_delay(min_s=5, max_s=15):
    delay = random.uniform(min_s,max_s)
    time.sleep(delay)
def long_delay():
    delay = random.uniform(20,40)
    time.sleep(delay)
def human_scroll(page):
    try:
        for _ in range(random.randint(2,5)):
            page.mouse.wheel(0, random.randint(300,800))
            time.sleep(random.uniform(1.5,3.5))
    except:
        pass
INTERNAL_KEYWORDS = ["about", "contact", "company", "products", "services"]
MAX_INTERNAL_PAGES = 5
MAX_IMAGES = 20


def scrape_page_basic(page, url):
    """Scrape basic content from a single page"""
    page.goto(url, timeout=60000)
    human_delay(6, 12)
    human_scroll(page)
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
        human_delay(6, 12)
        human_scroll(page)
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
    website = input("Enter company url: ").strip()
    scrape_company_site(website)
