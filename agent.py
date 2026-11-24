import os
import json
import requests
from dotenv import load_dotenv
from validation import (
    validate_recommendation,
    fallback_recommendation
)

load_dotenv()

API_KEY = os.getenv("NEBIUS_API_KEY")
MODEL = os.getenv("NEBIUS_MODEL")
API_URL = os.getenv("NEBIUS_API_URL")


def generate_recommendation(appointment, candidates):

    if not candidates:
        return None

    prompt = f"""
    You are SlotRescue AI, an intelligent appointment
    recovery agent for a beauty and wellness business.

    Cancelled appointment:
    {json.dumps(appointment)}

    Eligible customers:
    {json.dumps(candidates)}

    Your objectives:
    1. Maximise recovered revenue.
    2. Minimise unnecessary discounts.
    3. Prioritise longer waiting customers when revenue is equal.
    4. Only select an eligible customer.
    5. Use the candidate's calculated discount and revenue.
    6. Generate a friendly personalised appointment offer.

    Return only a valid JSON object with these fields:

    {{
        "customer_id": 0,
        "customer_name": "",
        "discount": 0,
        "recovered_revenue": 0,
        "reasoning": "",
        "offer_message": ""
    }}

    Do not include markdown or additional text.
    """

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are an appointment recovery agent. Return valid JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2,
        "max_tokens": 800
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=60
    )

    response.raise_for_status()

    content = response.json()["choices"][0]["message"]["content"]

    return json.loads(content)


def safe_recommendation(appointment, candidates):

    if not candidates:
        return None

    try:
        result = generate_recommendation(
            appointment, candidates
        )

        if validate_recommendation(result, candidates):
            result["source"] = "Nebius AI"
            return result

    except (
        requests.RequestException,
        ValueError,
        KeyError,
        IndexError,
        TypeError
    ):
        pass

    result = fallback_recommendation(
        appointment, candidates
    )

    result["source"] = "Rule-based fallback"

    return result


if __name__ == "__main__":
    from data import appointments, customers
    from matching import rank_customers

    appointment = appointments[1]

    candidates = rank_customers(
        appointment, customers
    )

    recommendation = safe_recommendation(
        appointment, candidates
    )

    print(json.dumps(recommendation, indent=4))