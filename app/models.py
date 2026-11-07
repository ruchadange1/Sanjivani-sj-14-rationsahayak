from dataclasses import dataclass


@dataclass
class Record:
    topic: str
    rule: str
    card_type: str
    quantity_or_limit: str
    authority: str
    source_url: str