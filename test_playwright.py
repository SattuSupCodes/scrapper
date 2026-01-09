from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # headless=False so you SEE it
    page = browser.new_page()
    page.goto("https://studiorenaissance.org/")
    print(page.title())
    browser.close()
