
from app.smart_search import smart_search


def make_record(
    rule,
    category,
    effective_from="Not available",
    effective_until="Not available",
    authority_level="Central",
    issuer="Government of India",
    source_authority_level="Central",
):
    return {
        "topic": category,
        "rule": rule,
        "card_type": "AAY and PHH",
        "quantity_or_limit": "Foodgrains",
        "authority": "DFPD",
        "authority_level": authority_level,
        "issuing_authority": issuer,
        "source_authority_level": source_authority_level,
        "policy_category": category,
        "notification_date": "Not available",
        "effective_from": effective_from,
        "effective_until": effective_until,
        "source_document": "test_document.html",
    }


def test_latest_applicable_free_ration_policy_ranks_first():
    old_policy = make_record(
        rule="Free foodgrains for AAY and PHH beneficiaries.",
        category="Free Ration",
        effective_from="2023-01-01",
    )

    newer_policy = make_record(
        rule="Free foodgrains for AAY and PHH beneficiaries.",
        category="Free Ration",
        effective_from="2024-01-01",
        effective_until="2028-12-31",
    )

    results = smart_search(
        [old_policy, newer_policy],
        "free ration for AAY beneficiaries in 2025",
    )

    assert len(results) == 2
    assert results[0]["effective_from"] == "2024-01-01"


def test_expired_policy_ranks_below_applicable_policy():
    expired_policy = make_record(
        rule="Rice price was Rs 3 per kg.",
        category="Pricing",
        effective_from="2013-01-01",
        effective_until="2016-12-31",
    )

    applicable_policy = make_record(
        rule="Rice is provided free of cost to NFSA beneficiaries.",
        category="Free Ration",
        effective_from="2024-01-01",
        effective_until="2028-12-31",
    )

    results = smart_search(
        [expired_policy, applicable_policy],
        "free ration rice in 2025",
    )

    assert results[0]["effective_from"] == "2024-01-01"


def test_historical_question_preserves_historical_record():
    historical_policy = make_record(
        rule="Historical rice price was Rs 3 per kg.",
        category="Pricing",
    )

    results = smart_search(
        [historical_policy],
        "historical rice price",
    )

    assert len(results) == 1
    assert "historical" in results[0]["rule"].lower()


def test_maharashtra_question_prefers_maharashtra_issuer():
    central_record = make_record(
        rule="Central ration eligibility rules.",
        category="Eligibility",
        issuer="Government of India",
        authority_level="Central",
    )

    state_record = make_record(
        rule="Maharashtra PHH eligibility income criteria.",
        category="Eligibility",
        issuer="Government of Maharashtra",
        authority_level="Maharashtra State",
        source_authority_level="Maharashtra State",
    )

    results = smart_search(
        [central_record, state_record],
        "Maharashtra PHH eligibility criteria",
    )

    assert results[0]["issuing_authority"] == (
        "Government of Maharashtra"
    )


def test_central_question_prefers_central_issuer():
    state_record = make_record(
        rule="Maharashtra ration policy.",
        category="Free Ration",
        effective_from="2024-01-01",
        effective_until="2028-12-31",
        issuer="Government of Maharashtra",
        authority_level="Maharashtra State",
    )

    central_record = make_record(
        rule="Central Government free foodgrain policy.",
        category="Free Ration",
        effective_from="2024-01-01",
        effective_until="2028-12-31",
        issuer="Government of India",
        authority_level="Central",
    )

    results = smart_search(
        [state_record, central_record],
        "Central Government free ration policy in 2025",
    )

    assert results[0]["issuing_authority"] == (
        "Government of India"
    )


def test_future_policy_is_not_treated_as_current():
    future_policy = make_record(
        rule="Free ration starts in the future.",
        category="Free Ration",
        effective_from="2030-01-01",
        effective_until="2035-12-31",
    )

    results = smart_search(
        [future_policy],
        "free ration",
    )

    assert len(results) == 1
    assert results[0]["effective_from"] == "2030-01-01"


def test_empty_query_returns_empty_list():
    record = make_record(
        rule="Free ration information.",
        category="Free Ration",
    )

    assert smart_search([], "free ration") == []
    assert smart_search([record], "") == []


def test_invalid_date_does_not_crash_search():
    record = make_record(
        rule="Free ration information.",
        category="Free Ration",
        effective_from="invalid-date",
    )

    results = smart_search(
        [record],
        "free ration",
    )

    assert isinstance(results, list)
