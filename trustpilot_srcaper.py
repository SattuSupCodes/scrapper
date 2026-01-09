from playwright.sync_api import sync_playwright

def scrape_trustpilot(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url, timeout=60000)

        page.wait_for_selector("span[data-rating-component='rating']", timeout=60000)

        rating = page.locator(
            "span[data-rating-component='rating']"
        ).inner_text()

        review_count = page.locator(
            "span[data-reviews-count-typography]"
        ).inner_text()

        print("Rating:", rating)
        print("Review count:", review_count)

        browser.close()


if __name__ == "__main__":
    scrape_trustpilot(
        "https://www.trustpilot.com/review/www.tripadvisor.com"
    )
