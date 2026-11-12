import json

from app.smart_search import smart_search

# Loading records
with open("data/records.json", "r", encoding="utf-8") as file:
    records = json.load(file)

# Searching records
result = smart_search(
    records,
    "How much ration does a PHH beneficiary receive?"
)

# Displaying top 5 results
for record in result[:5]:

    print("ID:", record["id"])
    print("Topic:", record["topic"])
    print("Rule:", record["rule"])
    print("Score:", record["score"])
    print("--------------------------")