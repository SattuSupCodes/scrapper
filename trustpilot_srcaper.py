from playwright.sync_api import sync_playwright
import json
import time


def scrape_category_companies(page, category_url, max_pages=5):
    companies = []
    seen = set()

    for page_num in range(1, max_pages + 1):
        url = f"{category_url}?page={page_num}"
        print(f"\n🔍 Scraping category page {page_num}")
        page.goto(url, timeout=60000)

        # accept cookies
        try:
            page.locator("button:has-text('Accept')").click(timeout=5000)
            page.wait_for_timeout(2000)
        except:
            pass

        # FORCE RENDER
        for _ in range(6):
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(1000)

        try:
            page.wait_for_selector("a[href^='/review/']", timeout=15000)
        except:
            print("❌ Still no business cards after scroll")
            break

        cards = page.locator("a[href^='/review/']")
        count = cards.count()
        print("Found cards:", count)

        if count == 0:
            break

        for i in range(count):
            card = cards.nth(i)
            href = card.get_attribute("href")
            name = card.get_attribute("data-business-unit-name")

            if not href:
                continue

            if not href.startswith("/review/") or href.count("/") < 2:
                continue

            full_url = "https://www.trustpilot.com" + href

            if full_url in seen:
                continue

            seen.add(full_url)

            companies.append({
                "name": name or full_url.split("/")[-1],
                "url": full_url
            })

    return companies



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


def scrape_company_rating(page, url):
    page.goto(url, timeout=60000)
    page.wait_for_timeout(3000)

    try:
        page.locator("button:has-text('Accept')").click(timeout=3000)
    except:
        pass

    rating = None

    scripts = page.locator("script[type='application/ld+json']").all()
    for script in scripts:
        try:
            data = json.loads(script.inner_text())
            rating = find_rating(data)
            if rating:
                break
        except:
            continue

    try:
        review_count = page.locator(
            "[data-reviews-count-typography]"
        ).inner_text()
    except:
        review_count = ""

    return rating, review_count


def main():
    category_url = "https://www.trustpilot.com/categories/furniture_store"
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=250
        )
        page = browser.new_page()

        companies = scrape_category_companies(
            page,
            category_url,
            max_pages=5
        )

        print(f"\n✅ Found {len(companies)} companies")

        for idx, company in enumerate(companies, start=1):
            print(f"[{idx}/{len(companies)}] {company['name']}")

            try:
                rating, review_count = scrape_company_rating(
                    page,
                    company["url"]
                )
            except Exception as e:
                print("⚠️ Failed:", e)
                rating, review_count = None, ""

            results.append({
                "name": company["name"],
                "url": company["url"],
                "rating": rating,
                "review_count": review_count
            })

            # throttle (VERY important for Trustpilot)
            time.sleep(2)

        browser.close()

    with open("trustpilot_furniture_ratings.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n💾 Done. Data saved.")


if __name__ == "__main__":
    main()
