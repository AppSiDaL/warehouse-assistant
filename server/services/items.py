import requests
ITEM_DESCRIPTION_URL = "http://localhost:8000/api/items"

def create_or_update_item(item_id, total_boxes):
    try:
        response = requests.put(
            f"{ITEM_DESCRIPTION_URL}/add/{item_id}?total_boxes={total_boxes}",
        )
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"Error fetching item description: {e}")
        return "No description available"


def create(item_id):
    try:
        response = requests.get(f"{ITEM_DESCRIPTION_URL}/{item_id}")
        response.raise_for_status()
        data = response.json()
        return data.get("description", "No description available")
    except requests.RequestException as e:
        print(f"Error fetching item description: {e}")
        return "No description available"