
from dataclasses import dataclass


@dataclass
class Record:
    # Original fields
    topic: str
    rule: str
    card_type: str
    quantity_or_limit: str
    authority: str
    source_url: str

    # Policy metadata
    authority_level: str = "Unknown"
    notification_date: str = "Not available"
    effective_from: str = "Not available"
    effective_until: str = "Not available"
    source_document: str = "Not available"
    policy_category: str = "General"

    # New: distinguish source portal from policy issuer
    source_authority_level: str = "Unknown"
    issuing_authority: str = "Not specified"
