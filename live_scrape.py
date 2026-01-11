from playwright.sync_api import sync_playwright

URL = "http://yellowpages.in/b/white-house-apparels-pvt-ltd-himayat-nagar-hyderabad/869060096"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(URL, timeout=60000)

    page.wait_for_timeout(3000)

    data = {}

    # ---- Company name ----
    try:
        data["name"] = page.locator("h1").inner_text()
    except:
        data["name"] = None

    # ---- Phone ----
    try:
        data["phone"] = page.locator("a.phone").inner_text()
    except:
        data["phone"] = None

    # ---- Address ----
    try:
        data["address"] = page.locator("p.address").inner_text()
    except:
        data["address"] = None

    # ---- Website ----
    try:
        data["website"] = page.locator("a.website-link").get_attribute("href")
    except:
        data["website"] = None

    # ---- Categories ----
    try:
        cats = page.locator("div.categories a").all_inner_texts()
        data["categories"] = cats
    except:
        data["categories"] = []

    print("\nSCRAPED DATA ↓↓↓\n")
    print(data)

    browser.close()
