import json
import re
from pathlib import Path


# Load Maharashtra income limits from records.json
def get_income_limits():
    file_path = Path(__file__).resolve().parent.parent / "data" / "records.json"

    with open(file_path, "r", encoding="utf-8") as file:
        records = json.load(file)

    for record in records:
        if record.get("topic") == "Income Limit":
            rule = record["rule"]

            rural = re.search(
                r"upto\s*₹\s*([\d,]+)\s*/?-?\s*in rural areas",
                rule,
                re.IGNORECASE
            )

            urban = re.search(
                r"upto\s*₹\s*([\d,]+)\s*/?-?\s*in urban areas",
                rule,
                re.IGNORECASE
            )

            if rural and urban:
                return {
                    "rural": int(rural.group(1).replace(",", "")),
                    "urban": int(urban.group(1).replace(",", ""))
                }

    raise ValueError("Income limits not found in records.json")


# Calculate monthly ration entitlement
def ration_entitlement(card_type, family_size, annual_income=None, area=None):

    card_type = card_type.upper()

    if family_size <= 0:
        raise ValueError("Family size must be greater than zero")

    if card_type == "AAY":
        return {
            "card_type": "AAY",
            "monthly_entitlement": 35,
            "unit": "kg per household",
            "message": "AAY household receives 35 kg per month."
        }

    elif card_type == "PHH":

        entitlement = 5 * family_size

        result = {
            "card_type": "PHH",
            "family_size": family_size,
            "monthly_entitlement": entitlement,
            "unit": "kg per month"
        }

        if annual_income is not None and area is not None:

            limits = get_income_limits()
            area = area.lower()

            if area not in limits:
                raise ValueError("Area must be rural or urban")

            income_limit = limits[area]

            result["annual_income"] = annual_income
            result["income_limit"] = income_limit
            result["income_eligible"] = annual_income <= income_limit

        else:
            result["income_eligible"] = None
            result["message"] = "Income eligibility not checked."

        return result

    else:
        raise ValueError("Card type must be AAY or PHH")