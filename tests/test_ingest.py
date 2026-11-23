
from app.ingest import detect_issuing_authority

MAHAFOOD_SOURCE = {
    "authority": "MahaFood",
    "authority_level": "Maharashtra State",
    "file": "mahafood_nfsa.html",
}


def test_government_of_india_notification():
    text = (
        "As per Government of India Notification "
        "dated 04.12.2023 free ration is provided."
    )

    issuer, level = detect_issuing_authority(
        text,
        MAHAFOOD_SOURCE,
    )

    assert issuer == "Government of India"
    assert level == "Central"


def test_maharashtra_government_resolution():
    text = (
        "Eligibility criteria prescribed vide "
        "Government Resolution dated 17.12.2013."
    )

    issuer, level = detect_issuing_authority(
        text,
        MAHAFOOD_SOURCE,
    )

    assert issuer == "Government of Maharashtra"
    assert level == "Maharashtra State"


def test_unknown_issuer_is_not_guessed():
    text = (
        "AAY households receive 35 kg of foodgrains "
        "per ration card per month."
    )

    issuer, level = detect_issuing_authority(
        text,
        MAHAFOOD_SOURCE,
    )

    assert issuer == "Not specified"
    assert level == "Unknown"
