import json
from datetime import datetime

# ---- MOCK INPUT (matches their data folder screenshots) ----
yellowpages_sample = {
    "name": "Evergreen Cleaning Systems",
    "phone": "(213) 375-1597",
    "address": "3325 Wilshire Blvd Ste 622, Los Angeles, CA",
    "website": "https://www.evergreencleaningsystems.com/",
    "categories": "House Cleaning, Building Cleaners-Interior, Janitorial Service",
    "hours": ""
}

# ---- OPTIONAL: mocked Trustpilot signal ----
trustpilot_sample = {
    "exists": True,
    "rating": 4.1,
    "review_count": 3749
}


def compute_review_volume(total_reviews):
    if total_reviews < 20:
        return "low"
    if total_reviews <= 100:
        return "medium"
    return "high"


def compute_online_visibility(website_present, platform_coverage):
    if website_present and platform_coverage >= 2:
        return "high"
    if website_present and platform_coverage == 1:
        return "medium"
    return "low"


def build_company_record(yp, tp=None):
    categories = [c.strip() for c in yp["categories"].split(",")]

    platform_coverage = 0
    total_reviews = 0

    platform_presence = {
        "yelp": {
            "exists": False,
            "rating": None,
            "review_count": None
        },
        "trustpilot": {
            "exists": False,
            "rating": None,
            "review_count": None
        }
    }

    if tp:
        platform_presence["trustpilot"] = tp
        platform_coverage += 1
        total_reviews += tp["review_count"]

    website_present = yp["website"] is not None

    return {
        "company_id": yp["name"].lower().replace(" ", "-"),

        "company_profile": {
            "name": yp["name"],
            "phone": yp["phone"],
            "address": yp["address"],
            "website": yp["website"]
        },

        "industry": {
            "primary": categories[0],
            "secondary": categories[1:]
        },

        "platform_presence": platform_presence,

        "derived_signals": {
            "platform_coverage": platform_coverage,
            "review_volume_level": compute_review_volume(total_reviews),
            "online_visibility": compute_online_visibility(
                website_present,
                platform_coverage
            ),
            "address_present": True,
            "website_present": website_present
        },

        "metadata": {
            "scraped_at": datetime.utcnow().isoformat(),
            "note": "demo using standardized schema"
        }
    }


if __name__ == "__main__":
    record = build_company_record(yellowpages_sample, trustpilot_sample)
    print(json.dumps(record, indent=2))
