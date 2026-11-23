
import json
from pathlib import Path

# Project data folder
base_path = Path(__file__).resolve().parent.parent

# Existing sample dataset (19 records)
sample_file_path = base_path / "data" / "sample_records.json"

# Newly extracted policy dataset (75 records)
policy_file_path = base_path / "data" / "records.json"


def load_records():
    """Load the existing sample records."""
    with open(sample_file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_policy_records():
    """Load the extracted policy records."""
    with open(policy_file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def search(records, keyword):
    """Search records using a keyword."""
    keyword = keyword.lower()
    result = []

    for record in records:
        if (
            keyword in record.get("topic", "").lower()
            or keyword in record.get("rule", "").lower()
            or keyword in record.get("card_type", "").lower()
            or keyword in record.get("authority", "").lower()
        ):
            result.append(record)

    return result


def count_by(records, category="topic"):
    """Count records by a selected category."""
    count = {}

    for record in records:
        value = record.get(category, "Unknown")
        count[value] = count.get(value, 0) + 1

    return count


def get_by_id(records, record_id):
    """Get a record using its ID."""
    for record in records:
        if record.get("id") == record_id:
            return record

    return None