import re
from datetime import date

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SEARCH_FIELDS = (
    "topic",
    "rule",
    "card_type",
    "quantity_or_limit",
    "authority",
    "authority_level",
    "issuing_authority",
    "source_authority_level",
    "policy_category",
    "source_document",
)


def normalize_text(value):
    """Convert a value into lowercase searchable text."""
    return str(value or "").lower()


def parse_date(value):
    """Convert an ISO date string into a date object."""
    value = normalize_text(value).strip()

    if not value or value in (
        "not available",
        "unknown",
        "none",
        "null",
    ):
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def extract_query_date(query):
    """
    Extract a date or year explicitly mentioned in a question.

    Supported formats:
    - 2025
    - 2025-01-01
    - 17.12.2013
    - 17/12/2013
    """
    query = normalize_text(query)

    # YYYY-MM-DD
    match = re.search(
        r"\b(20\d{2})-(\d{1,2})-(\d{1,2})\b",
        query,
    )

    if match:
        try:
            return date(
                int(match.group(1)),
                int(match.group(2)),
                int(match.group(3)),
            )
        except ValueError:
            return None

    # DD.MM.YYYY or DD/MM/YYYY
    match = re.search(
        r"\b(\d{1,2})[./](\d{1,2})[./](20\d{2})\b",
        query,
    )

    if match:
        try:
            return date(
                int(match.group(3)),
                int(match.group(2)),
                int(match.group(1)),
            )
        except ValueError:
            return None

    # Year only
    match = re.search(r"\b(20\d{2})\b", query)

    if match:
        return date(int(match.group(1)), 1, 1)

    return None


def get_query_intent(query):
    """Identify the card type, policy purpose and requested authority."""
    query = normalize_text(query)

    historical = any(
        term in query
        for term in (
            "historical",
            "history",
            "old rule",
            "old price",
            "previous rule",
            "previous price",
            "earlier rule",
            "earlier price",
            "past policy",
            "historical price",
        )
    )

    return {
        "card_type": (
            "PHH"
            if re.search(
                r"\bphh\b|priority households?",
                query,
            )
            else "AAY"
            if re.search(
                r"\baay\b|antyodaya",
                query,
            )
            else None
        ),

        "entitlement": any(
            term in query
            for term in (
                "entitlement",
                "ration",
                "quantity",
                "how much",
                "food grain",
                "foodgrain",
                "monthly",
                "per person",
            )
        ),

        "eligibility": any(
            term in query
            for term in (
                "eligibility",
                "eligible",
                "qualify",
                "criteria",
            )
        ),

        "pricing": any(
            term in query
            for term in (
                "price",
                "cost",
                "rate",
                "rupees",
                "how much does",
            )
        ),

        "free_ration": any(
            term in query
            for term in (
                "free",
                "free ration",
                "free of cost",
                "pmgkay",
            )
        ),

        "monthly": any(
            term in query
            for term in (
                "monthly",
                "per month",
                "every month",
            )
        ),

        "historical": historical,

        "target_date": extract_query_date(query),

        "maharashtra": "maharashtra" in query,

        "central": any(
            term in query
            for term in (
                "central government",
                "central rule",
                "centre",
                "central",
            )
        ),
    }


def calculate_metadata_score(record, intent):
    """Calculate additional relevance points from policy metadata."""
    score = 0.0

    card_type = normalize_text(record.get("card_type"))
    rule = normalize_text(record.get("rule"))
    topic = normalize_text(record.get("topic"))
    category = normalize_text(record.get("policy_category"))
    quantity = normalize_text(record.get("quantity_or_limit"))

    searchable_text = (
        f"{topic} {rule} {card_type} {quantity}"
    )

    # Card type relevance
    selected_card = intent["card_type"]

    if selected_card:
        if selected_card.lower() in card_type:
            score += 0.30
        elif selected_card.lower() in searchable_text:
            score += 0.15

    # Entitlement relevance
    if intent["entitlement"]:
        if category == "entitlement":
            score += 0.25

        if "entitl" in rule or "entitl" in topic:
            score += 0.15

        if any(
            term in rule
            for term in (
                "kg per person",
                "kg per household",
                "foodgrains per",
            )
        ):
            score += 0.12

    # Monthly quantity relevance
    if intent["monthly"]:
        if "per month" in rule or "monthly" in rule:
            score += 0.12

        if "per month" in quantity or "monthly" in quantity:
            score += 0.10

    # Eligibility relevance
    if intent["eligibility"] and category == "eligibility":
        score += 0.30

    # Pricing relevance
    if intent["pricing"] and category == "pricing":
        score += 0.30

    # Free-ration relevance
    if intent["free_ration"] and category == "free ration":
        score += 0.30

    # Authority relevance.
    # The source portal and issuing authority are different concepts.
    issuer = normalize_text(
        record.get("issuing_authority")
    )

    authority = normalize_text(
        record.get("authority_level")
    )

    if intent["maharashtra"]:
        if "government of maharashtra" in issuer:
            score += 0.25
        elif authority == "maharashtra state":
            score += 0.15

    if intent["central"]:
        if "government of india" in issuer:
            score += 0.25
        elif authority == "central":
            score += 0.15

    return score


def calculate_date_score(record, intent):
    """
    Rank policy records using their effective dates.

    This function helps rank applicable records. It does not establish
    legal supersession or prove that one notification cancels another.
    """

    category = normalize_text(
        record.get("policy_category")
    )

    # Date ranking applies to price and free-ration questions.
    if category not in ("pricing", "free ration"):
        return 0.0

    if not (
        intent["pricing"] or intent["free_ration"]
    ):
        return 0.0

    target_date = intent["target_date"]

    # Historical questions without a requested year/date should not
    # automatically use today's policy.
    if intent["historical"] and target_date is None:
        return 0.0

    # If no date is specified, use today's date.
    if target_date is None:
        target_date = date.today()

    effective_from = parse_date(
        record.get("effective_from")
    )

    effective_until = parse_date(
        record.get("effective_until")
    )

    # A record without an effective start date cannot be confirmed
    # as applicable to the requested date.
    if effective_from is None:
        return -0.15

    # The policy has not started yet.
    if effective_from > target_date:
        return -0.30

    # The policy has already expired.
    if (
        effective_until is not None
        and effective_until < target_date
    ):
        return -0.30

    # The policy is within its stated effective period.
    score = 0.40

    # Prefer the later effective start among applicable records.
    # This is a small ranking preference, not legal conflict resolution.
    score += (effective_from.year - 2000) * 0.01

    return score


def smart_search(records, query):
    """
    Search policy records using TF-IDF and metadata ranking.

    Existing API endpoints can continue using this function.
    """

    if (
        not records
        or not isinstance(query, str)
        or not query.strip()
    ):
        return []

    documents = [
        " ".join(
            normalize_text(record.get(field))
            for field in SEARCH_FIELDS
        )
        for record in records
    ]

    if not any(
        document.strip()
        for document in documents
    ):
        return []

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        sublinear_tf=True,
    )

    try:
        record_vectors = vectorizer.fit_transform(
            documents
        )

        query_vector = vectorizer.transform(
            [query]
        )

    except ValueError:
        return []

    similarities = cosine_similarity(
        query_vector,
        record_vectors,
    )[0]

    intent = get_query_intent(query)

    results = []

    for index, record in enumerate(records):

        score = float(similarities[index])

        score += calculate_metadata_score(
            record,
            intent,
        )

        score += calculate_date_score(
            record,
            intent,
        )

        if score <= 0:
            continue

        result = record.copy()

        result["id"] = record.get(
            "id",
            index + 1,
        )

        # Preserve the full score internally for sorting.
        result["_ranking_score"] = score

        result["score"] = round(
            score,
            3,
        )

        results.append(result)

    # Sort using the unrounded score.
    results.sort(
        key=lambda item: item["_ranking_score"],
        reverse=True,
    )

    # Do not expose the internal ranking field in API responses.
    for result in results:
        result.pop("_ranking_score", None)

    return results