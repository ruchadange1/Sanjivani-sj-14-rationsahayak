import re
import json
from pathlib import Path
from bs4 import BeautifulSoup

from app.models import Record


sources = [
    {
        "file": "dfpd_faq.html",
        "authority": "DFPD",
        "url": "https://dfpd.gov.in/faqs/en"
    },
    {
        "file": "nfsa_features.html",
        "authority": "NFSA",
        "url": "https://nfsa.gov.in/portal/Salient_Features_NFSA_AA"
    },
    {
        "file": "mahafood_nfsa.html",
        "authority": "MahaFood",
        "url": "https://mahafood.gov.in/en/national-food-security-act-2013/"
    }
]


def clean_text(text):
    return " ".join(text.split())


def get_card_type(text):

    text = text.lower()

    has_aay = "aay" in text or "antyodaya" in text
    has_phh = "phh" in text or "priority household" in text

    if has_aay and has_phh:
        return "AAY and PHH"

    elif has_aay:
        return "AAY"

    elif has_phh:
        return "PHH"

    return "Not specified"


def get_topic(text):

    text = text.lower()

    if "portability" in text or "onorc" in text:
        return "ONORC"

    elif "income" in text:
        return "Income Limit"

    elif "grievance" in text or "complaint" in text:
        return "Grievance"

    elif "helpline" in text or "toll-free" in text:
        return "Helpline"

    elif "pregnant" in text or "children" in text or "woman" in text:
        return "Women and Children"

    elif "free of cost" in text:
        return "Free Ration"

    elif "35 kg" in text or "5 kg" in text or "foodgrain" in text:
        return "Ration Entitlement"

    return "General Information"


def get_quantity(text):

    quantities = []

    amounts = re.findall(r"₹\s?\d[\d,]*", text)
    quantities.extend(amounts)

    weights = re.findall(r"\d+\s*(?:kg|kgs)", text, re.IGNORECASE)
    quantities.extend(weights)

    dates = re.findall(
        r"\d+\s*(?:st|nd|rd|th)?\s+\w+\s*,?\s*\d{4}",
        text
    )
    quantities.extend(dates)

    if quantities:
        return ", ".join(dict.fromkeys(quantities))

    return "Not specified"


def is_relevant(text):

    keywords = [
        "ration", "foodgrain", "food grain",
        "aay", "phh", "antyodaya",
        "priority household", "nfsa",
        "onorc", "portability", "income",
        "grievance", "helpline", "pregnant",
        "children", "entitlement"
    ]

    text = text.lower()

    for word in keywords:
        if word in text:
            return True

    return False


def ingest_data():

    records = []

    for source in sources:

        file_path = Path("data/raw") / source["file"]

        print("\nReading:", source["file"])

        try:

            with open(file_path, "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file.read(), "html.parser")

            texts = []

            if source["authority"] == "DFPD":

                for item in soup.select(".accordion-item"):

                    question = item.select_one(".accordion-button")
                    answer = item.select_one(".accordion-body")

                    if question and answer:
                        text = question.get_text(" ", strip=True)
                        text += " " + answer.get_text(" ", strip=True)
                        texts.append(clean_text(text))

            elif source["authority"] == "NFSA":

                for item in soup.select("section.content .box-body li"):
                    texts.append(clean_text(item.get_text(" ", strip=True)))

            else:

                for item in soup.select("main p"):
                    texts.append(clean_text(item.get_text(" ", strip=True)))

            print("Extracted:", len(texts))

            for text in texts:

                if is_relevant(text):

                    record = Record(
                        topic=get_topic(text),
                        rule=text,
                        card_type=get_card_type(text),
                        quantity_or_limit=get_quantity(text),
                        authority=source["authority"],
                        source_url=source["url"]
                    )

                    records.append(record.__dict__)

        except Exception as e:
            print("Error:", e)

    # Remove duplicate records
    unique_records = []

    for record in records:
        if record not in unique_records:
            unique_records.append(record)

    with open("data/records.json", "w", encoding="utf-8") as file:
        json.dump(unique_records, file, indent=4, ensure_ascii=False)

    print("\nTotal records:", len(unique_records))
    print("Records saved successfully!")


if __name__ == "__main__":
    ingest_data()