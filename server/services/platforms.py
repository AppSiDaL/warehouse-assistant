import requests

ITEM_DESCRIPTION_URL = "http://localhost:8000/api/platforms"


def get_platform(platform_code):
    try:
        response = requests.get(f"{ITEM_DESCRIPTION_URL}/{platform_code}")
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"Error fetching item description: {e}")
        return "No description available"

def update_platform(platform_code, items_count, items_type):
    try:
        response = requests.put(
            f"{ITEM_DESCRIPTION_URL}/{platform_code}",
            json={"items_count": items_count, "items_type": items_type},
        )
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"Error fetching item description: {e}")
        return "No description available"
