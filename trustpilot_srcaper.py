from playwright.sync_api import sync_playwright

def scrape_trustpilot(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)

        page.wait_for_selector("body")
        print("Page loaded:", page.title())

        # TODO: extract rating
        # TODO: extract review count

        browser.close()

if __name__ == "__main__":
    scrape_trustpilot("https://www.trustpilot.com/review/www.tripadvisor.com")
