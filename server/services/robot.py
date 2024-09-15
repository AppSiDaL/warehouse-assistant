import requests
ITEM_DESCRIPTION_URL = "http://localhost:8000/api/robot/1"

def update_robot(robot):
    try:
        response = requests.put(f"{ITEM_DESCRIPTION_URL}", json=robot)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"Error updating robot: {e}")
        return "Erorr updating robot"                        
