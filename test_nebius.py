import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("NEBIUS_API_KEY")

if not api_key:
    print("API key not found.")
    exit()

url = "https://api.tokenfactory.nebius.com/v1/models"

headers = {
    "Authorization": f"Bearer {api_key}"
}

response = requests.get(url, headers=headers, timeout=30)

print("Status code:", response.status_code)

if response.status_code == 200:
    print("Nebius API connected successfully!")

    for model in response.json()["data"]:
        print(model["id"])
else:
    print("Connection failed.")
    