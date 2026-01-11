from playwright.sync_api import sync_playwright
import json

def find_rating(obj):
    if isinstance(obj, dict):
        if "aggregateRating" in obj:
            ar = obj["aggregateRating"]
            if isinstance(ar, dict):
                return ar.get("ratingValue")
        for v in obj.values():
            result = find_rating(v)
            if result:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = find_rating(item)
            if result:
                return result
    return None


def scrape_trustpilot(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=300
        )
        page = browser.new_page()
        page.goto(url, timeout=60000)

        page.wait_for_timeout(3000)

        try:
            page.locator("button:has-text('Accept')").click(timeout=5000)
            print("Cookies accepted")
        except:
            print("No cookie popup")

        
        rating = None
        scripts = page.locator("script[type='application/ld+json']").all()

        for script in scripts:
            try:
                data = json.loads(script.inner_text())
                rating = find_rating(data)
                if rating:
                    break
            except json.JSONDecodeError:
                continue

       
        review_count = page.locator(
            "[data-reviews-count-typography]"
        ).inner_text()

        print("Rating:", rating)
        print("Review count:", review_count)

        browser.close()


if __name__ == "__main__":
    scrape_trustpilot(
        "https://www.trustpilot.com/review/pepperfry.com"
    )
