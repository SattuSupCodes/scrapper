import requests
from bs4 import BeautifulSoup

url = "https://studiorenaissance.org/"
response = requests.get(url, timeout=10)
response.encoding = response.apparent_encoding


soup = BeautifulSoup(response.text, "html.parser")

def get_meta(property_name):
    tag = soup.find("meta", property=property_name)
    return tag["content"].strip() if tag else None

def extract_company_name(soup):
    # 1. OpenGraph site name
    tag = soup.find("meta", property="og:site_name")
    if tag:
        return tag["content"].strip()

    # 2. OpenGraph title (cleaned)
    tag = soup.find("meta", property="og:title")
    if tag:
        return tag["content"].split("|")[0].strip()

    # 3. Header / logo text
    header = soup.find(["h1", "h2"])
    if header:
        return header.text.strip()

    # 4. Fallback to <title>
    return soup.title.text.split("|")[0].strip()
company_name = extract_company_name(soup)
print(company_name)

description_tag = soup.find("meta", attrs={"name": "description"})
description = description_tag["content"].strip() if description_tag else None
print(description)

social_links = {"instagram": None, "twitter": None, "linkedin": None}

for link in soup.find_all("a", href=True):
    href = link["href"]
    if "instagram.com" in href:
        social_links["instagram"] = href
    elif "twitter.com" in href or "x.com" in href:
        social_links["twitter"] = href
    elif "linkedin.com" in href:
        social_links["linkedin"] = href



