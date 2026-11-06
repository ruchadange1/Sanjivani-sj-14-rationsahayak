import json
from pathlib import Path

# getting the location of the project folder
base_path = Path(__file__).resolve().parent.parent
file_path = base_path / "data" / "sample_records.json"


# function to load all records
def load_records():
    file = open(file_path, "r", encoding="utf-8")
    records = json.load(file)
    file.close()

    return records


# function to search records using a keyword
def search(records, keyword):
    result = []

    for record in records:
        if (keyword.lower() in record["topic"].lower() or
            keyword.lower() in record["rule"].lower() or
            keyword.lower() in record["card_type"].lower() or
            keyword.lower() in record["authority"].lower()):

            result.append(record)

    return result


# function to count records by category
def count_by(records, category="topic"):
    count = {}

    for record in records:
        value = record.get(category, "Unknown")

        if value in count:
            count[value] += 1
        else:
            count[value] = 1

    return count


# function to get a record using its id
def get_by_id(records, record_id):
    for record in records:
        if record["id"] == record_id:
            return record

    return None