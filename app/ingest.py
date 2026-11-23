
import json
import re
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

from app.models import Record

# ==========================================
# 1. PROJECT PATH AND SOURCE DOCUMENTS
# ==========================================

BASE_PATH = Path(__file__).resolve().parent.parent

sources = [
    {
        "file": "dfpd_faq.html",
        "authority": "DFPD",
        "authority_level": "Central",
        "url": "https://dfpd.gov.in/faqs/en",
    },
    {
        "file": "nfsa_features.html",
        "authority": "NFSA",
        "authority_level": "Central",
        "url": "https://nfsa.gov.in/portal/Salient_Features_NFSA_AA",
    },
    {
        "file": "mahafood_nfsa.html",
        "authority": "MahaFood",
        "authority_level": "Maharashtra State",
        "url": "https://mahafood.gov.in/en/national-food-security-act-2013/",
    },
]


# ==========================================
# 2. TEXT CLEANING
# ==========================================

def clean_text(text):
    return " ".join(text.split())


# ==========================================
# 3. DATE NORMALIZATION
# ==========================================

DATE_PATTERN = (
    r"\d{1,2}"
    r"(?:\s*(?:st|nd|rd|th))?"
    r"(?:\s+of)?\s+"
    r"[A-Za-z]+\s*,?\s*\d{4}"
    r"|"
    r"\d{1,2}[./-]\d{1,2}[./-]\d{4}"
)


def normalize_date(date_text):
    date_text = date_text.strip()

    date_text = re.sub(
        r"(\d)\s+(st|nd|rd|th)\b",
        r"\1\2",
        date_text,
        flags=re.IGNORECASE,
    )

    date_text = re.sub(
        r"(?<=\d)(st|nd|rd|th)\b",
        "",
        date_text,
        flags=re.IGNORECASE,
    )

    date_text = re.sub(
        r"^(\d+)\s+of\s+",
        r"\1 ",
        date_text,
        flags=re.IGNORECASE,
    )

    date_text = re.sub(r"\s+", " ", date_text)
    date_text = date_text.replace(",", "").strip()

    formats = [
        "%d %B %Y",
        "%d %b %Y",
        "%d.%m.%Y",
        "%d/%m/%Y",
        "%d-%m-%Y",
    ]

    for date_format in formats:
        try:
            return datetime.strptime(
                date_text,
                date_format,
            ).strftime("%Y-%m-%d")
        except ValueError:
            continue

    return "Not available"


# ==========================================
# 4. NOTIFICATION DATE EXTRACTION
# ==========================================

def extract_notification_date(text):
    pattern = (
        rf"(?:government\s+of\s+india\s+)?"
        rf"(?:notification|government notification|"
        rf"government resolution|G\.?\s*R\.?)"
        rf"\s*(?:dated|date of)\s+"
        rf"({DATE_PATTERN})"
    )

    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return normalize_date(match.group(1))

    return "Not available"


# ==========================================
# 5. EFFECTIVE DATE EXTRACTION
# ==========================================

def extract_effective_dates(text):
    effective_from = "Not available"
    effective_until = "Not available"

    # Explicit period: from DATE to DATE
    period_pattern = (
        rf"\bfrom\s+({DATE_PATTERN})"
        rf"\s+to\s+({DATE_PATTERN})"
    )

    match = re.search(
        period_pattern,
        text,
        re.IGNORECASE,
    )

    if match:
        return (
            normalize_date(match.group(1)),
            normalize_date(match.group(2)),
        )

    # Period expressed as:
    # for the period of DATE to next five years
    # (i.e. Dt. DATE)

    start_pattern = (
        rf"for the period of\s+({DATE_PATTERN})"
    )

    start_match = re.search(
        start_pattern,
        text,
        re.IGNORECASE,
    )

    if start_match:
        effective_from = normalize_date(
            start_match.group(1)
        )

        remaining_text = text[start_match.end():]

        end_pattern = (
            rf"(?:i\.e\.|that is)\s*"
            rf"(?:Dt\.?\s*)?"
            rf"({DATE_PATTERN})"
        )

        end_match = re.search(
            end_pattern,
            remaining_text,
            re.IGNORECASE,
        )

        if end_match:
            effective_until = normalize_date(
                end_match.group(1)
            )

        return effective_from, effective_until

    # Explicit commencement: since DATE

    since_pattern = rf"\bsince\s+({DATE_PATTERN})"

    since_match = re.search(
        since_pattern,
        text,
        re.IGNORECASE,
    )

    if since_match:
        effective_from = normalize_date(
            since_match.group(1)
        )

    return effective_from, effective_until


# ==========================================
# 6. ISSUING AUTHORITY DETECTION
# ==========================================

def detect_issuing_authority(text, source):
    """
    Identify the authority that issued the policy.

    The source portal and issuing authority are
    different concepts.

    If the text does not identify the issuer,
    do not invent one.
    """

    lower_text = text.lower()

    # Explicit Central Government references

    central_patterns = [
        r"\bgovernment of india\b",
        r"\bgovt\.?\s+of india\b",
        r"\bgoi\b",
        r"\bcentral government\b",
        r"\bdepartment of food and public distribution\b",
        r"\bministry of consumer affairs\b",
        r"\bdfpd\b",
    ]

    if any(
        re.search(pattern, lower_text)
        for pattern in central_patterns
    ):
        return "Government of India", "Central"

    # Explicit Maharashtra Government references

    maharashtra_patterns = [
        r"\bgovernment of maharashtra\b",
        r"\bmaharashtra government\b",
        r"\bgovernment of the state of maharashtra\b",
    ]

    if any(
        re.search(pattern, lower_text)
        for pattern in maharashtra_patterns
    ):
        return "Government of Maharashtra", "Maharashtra State"

    # A Government Resolution on the Maharashtra
    # MahaFood source page is treated as a Maharashtra
    # resolution. This is a source-context inference.

    has_resolution_reference = bool(
        re.search(
            r"\bgovernment resolution\b|\bG\.?\s*R\.?\s+dated\b",
            text,
            re.IGNORECASE,
        )
    )

    if (
        source["authority"] == "MahaFood"
        and has_resolution_reference
    ):
        return "Government of Maharashtra", "Maharashtra State"

    # Do not assume the issuer merely from the source portal.

    return "Not specified", "Unknown"


# ==========================================
# 7. CARD TYPE DETECTION
# ==========================================

def get_card_type(text):
    text = text.lower()

    # PHH eligibility rule explicitly identifies PHH.
    # AAY is mentioned as an excluded group.

    if (
        "included in phh" in text
        or "included under phh" in text
        or "priority household beneficiaries" in text
    ):
        return "PHH"

    if (
        "identification of antyodaya" in text
        or "identification criteria" in text
    ):
        return "AAY"

    has_aay = bool(
        re.search(r"\baay\b|antyodaya", text)
    )

    has_phh = bool(
        re.search(
            r"\bphh\b|priority household",
            text,
        )
    )

    if has_aay and has_phh:
        return "AAY and PHH"

    if has_aay:
        return "AAY"

    if has_phh:
        return "PHH"

    return "Not specified"


# ==========================================
# 8. TOPIC DETECTION
# ==========================================

def get_topic(text):
    text = text.lower()

    if "portability" in text or "onorc" in text:
        return "ONORC"

    if "income" in text:
        return "Income Limit"

    if "grievance" in text or "complaint" in text:
        return "Grievance"

    if "helpline" in text or "toll-free" in text:
        return "Helpline"

    if (
        "pregnant" in text
        or "children" in text
        or "woman" in text
    ):
        return "Women and Children"

    if (
        "free of cost" in text
        or "free-of-cost" in text
    ):
        return "Free Ration"

    if (
        "35 kg" in text
        or "35kg" in text
        or "5 kg" in text
        or "5kg" in text
        or "foodgrain" in text
        or "food grain" in text
    ):
        return "Ration Entitlement"

    return "General Information"


# ==========================================
# 9. POLICY CATEGORY
# ==========================================

def get_policy_category(text):
    text = text.lower()

    if (
        "income" in text
        or "eligibility" in text
        or "identification of" in text
        or "identification criteria" in text
    ):
        return "Eligibility"

    if (
        "free of cost" in text
        or "free-of-cost" in text
    ):
        return "Free Ration"

    if (
        "historical" in text
        or "rs." in text
        or "₹" in text
        or "per kg" in text
        or "per kilogram" in text
        or "subsidized prices" in text
    ):
        return "Pricing"

    if (
        "35 kg" in text
        or "35kg" in text
        or "5 kg" in text
        or "5kg" in text
        or "entitlement" in text
        or "are entitled" in text
    ):
        return "Entitlement"

    if "grievance" in text or "complaint" in text:
        return "Grievance"

    if (
        "notification dated" in text
        or "government resolution" in text
        or re.search(r"\bG\.?\s*R\.?\s+dated\b", text)
    ):
        return "Government Notification"

    return "General"


# ==========================================
# 10. QUANTITY EXTRACTION
# ==========================================

def get_quantity(text):
    quantities = []

    amounts = re.findall(
        r"(?:₹\s*|Rs\.?\s*)\d[\d,]*(?:\.\d+)?",
        text,
        re.IGNORECASE,
    )

    quantities.extend(amounts)

    weights = re.findall(
        r"\d+\s*(?:kg|kgs|kilograms?)",
        text,
        re.IGNORECASE,
    )

    quantities.extend(weights)

    dates = re.findall(
        DATE_PATTERN,
        text,
        re.IGNORECASE,
    )

    quantities.extend(dates)

    if quantities:
        return ", ".join(dict.fromkeys(quantities))

    return "Not specified"


# ==========================================
# 11. RELEVANT RECORD FILTER
# ==========================================

def is_relevant(text):
    keywords = [
        "ration",
        "foodgrain",
        "food grain",
        "aay",
        "phh",
        "antyodaya",
        "priority household",
        "nfsa",
        "onorc",
        "portability",
        "income",
        "grievance",
        "helpline",
        "pregnant",
        "children",
        "entitlement",
        "food security",
    ]

    text = text.lower()

    return any(
        word in text
        for word in keywords
    )


# ==========================================
# 12. MAHARASHTRA POLICY SPLITTING
# ==========================================

def split_policy_statements(text):
    protected_text = re.sub(
        r"\bi\.e\.",
        "ie<ABBR_PERIOD>",
        text,
        flags=re.IGNORECASE,
    )

    statements = re.split(
        r"(?<=[.!?])\s+(?=[A-Z₹])|;\s*",
        protected_text,
    )

    results = []

    for statement in statements:
        statement = statement.replace(
            "ie<ABBR_PERIOD>",
            "i.e.",
        )

        statement = clean_text(statement)

        if statement and is_relevant(statement):
            results.append(statement)

    contextual_results = []

    for statement in results:
        lower_statement = statement.lower()

        # Preserve the AAY/PHH context for the
        # free-grain statement.

        if (
            "free of cost" in lower_statement
            or "free-of-cost" in lower_statement
        ):
            statement = (
                "Free-of-cost provision for NFSA AAY and PHH "
                "beneficiaries, referring to the foodgrains "
                "described in the source: "
                + statement
            )

        # Historical prices must not be treated as
        # proof of current payable prices.

        if (
            "subsidized prices" in lower_statement
            or (
                "per kg" in lower_statement
                and "rice" in lower_statement
                and "wheat" in lower_statement
            )
        ):
            statement = (
                "Historical subsidized price information "
                "stated on the source page: "
                + statement
            )

        contextual_results.append(statement)

    return contextual_results


# ==========================================
# 13. SOURCE DOCUMENT EXTRACTION
# ==========================================

def extract_source_text(soup, authority):
    texts = []

    # DFPD FAQ

    if authority == "DFPD":
        for item in soup.select(".accordion-item"):
            question = item.select_one(".accordion-button")
            answer = item.select_one(".accordion-body")

            if question and answer:
                text = question.get_text(
                    " ",
                    strip=True,
                )

                text += " " + answer.get_text(
                    " ",
                    strip=True,
                )

                text = clean_text(text)

                if text:
                    texts.append(text)

    # NFSA

    elif authority == "NFSA":
        for item in soup.select(
            "section.content .box-body li"
        ):
            text = clean_text(
                item.get_text(" ", strip=True)
            )

            if text:
                texts.append(text)

    # Maharashtra MahaFood

    elif authority == "MahaFood":
        for item in soup.select("main p"):
            paragraph = clean_text(
                item.get_text(" ", strip=True)
            )

            if paragraph:
                texts.extend(
                    split_policy_statements(paragraph)
                )

    return texts


# ==========================================
# 14. CREATE STRUCTURED RECORD
# ==========================================

def create_record(text, source):
    effective_from, effective_until = (
        extract_effective_dates(text)
    )

    issuing_authority, authority_level = (
        detect_issuing_authority(text, source)
    )

    record = Record(
        topic=get_topic(text),
        rule=text,
        card_type=get_card_type(text),
        quantity_or_limit=get_quantity(text),
        authority=source["authority"],
        source_url=source["url"],
        authority_level=authority_level,
        notification_date=extract_notification_date(text),
        effective_from=effective_from,
        effective_until=effective_until,
        source_document=source["file"],
        policy_category=get_policy_category(text),
        source_authority_level=source["authority_level"],
        issuing_authority=issuing_authority,
    )

    return record.__dict__


# ==========================================
# 15. MAIN INGESTION
# ==========================================

def ingest_data():
    records = []

    for source in sources:
        file_path = (
            BASE_PATH / "data" / "raw" / source["file"]
        )

        print("\nReading:", source["file"])

        try:
            with open(
                file_path,
                "r",
                encoding="utf-8",
            ) as file:
                soup = BeautifulSoup(
                    file.read(),
                    "html.parser",
                )

            texts = extract_source_text(
                soup,
                source["authority"],
            )

            print("Extracted statements:", len(texts))

            for text in texts:
                if not is_relevant(text):
                    continue

                records.append(
                    create_record(text, source)
                )

        except (
            OSError,
            KeyError,
            AttributeError,
            TypeError,
        ) as error:
            print(
                "Error reading",
                source["file"],
                ":",
                error,
            )

    # ======================================
    # 16. REMOVE DUPLICATES
    # ======================================

    unique_records = []
    seen_records = set()

    for record in records:
        record_key = (
            record["authority"],
            record["rule"],
            record["source_url"],
        )

        if record_key not in seen_records:
            seen_records.add(record_key)
            unique_records.append(record)

    # ======================================
    # 17. SAVE RECORDS
    # ======================================

    output_path = BASE_PATH / "data" / "records.json"

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            unique_records,
            file,
            indent=4,
            ensure_ascii=False,
        )

    # ======================================
    # 18. INGESTION SUMMARY
    # ======================================

    print("\n========== INGESTION SUMMARY ==========")

    print("Total unique records:", len(unique_records))

    print("\nIssuing authority distribution:")

    for authority in sorted(
        {record["authority_level"] for record in unique_records}
    ):
        count = sum(
            record["authority_level"] == authority
            for record in unique_records
        )

        print(authority, ":", count)

    print("\nSource authority distribution:")

    for authority in sorted(
        {
            record["source_authority_level"]
            for record in unique_records
        }
    ):
        count = sum(
            record["source_authority_level"] == authority
            for record in unique_records
        )

        print(authority, ":", count)

    print("\nPolicy category distribution:")

    for category in sorted(
        {record["policy_category"] for record in unique_records}
    ):
        count = sum(
            record["policy_category"] == category
            for record in unique_records
        )

        print(category, ":", count)

    print("\nRecords saved successfully!")
    print("=======================================")


# ==========================================
# 19. RUN SCRIPT
# ==========================================

if __name__ == "__main__":
    ingest_data()