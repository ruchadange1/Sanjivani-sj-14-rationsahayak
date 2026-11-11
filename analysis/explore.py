import pandas as pd
import json

# Loading records
with open("data/records.json", "r", encoding="utf-8") as file:
    records = json.load(file)

# Creating DataFrame
df = pd.DataFrame(records)


# Fact 1: Total records
print("Total Records:", len(df))


# Fact 2: Records by authority
print("\nRecords by Authority:")
print(df["authority"].value_counts())


# Fact 3: Records by topic
print("\nRecords by Topic:")
print(df["topic"].value_counts())