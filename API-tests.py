from main import app
import requests

url = "http://127.0.0.1:8009"

def test_get_root():
    response = requests.get(url)
    if response.status_code == 200:
        print("GET / - SUCCESS")
    else:
        print("GET / - FAILED")


if __name__ == "__main__":
    test_get_root()

def test_post_creation():
    payload = {
        "title": "title",
        "content": "content",
        "category": "category",
        "tags": ["tag1", "tag2"]
    }
    response = requests.post(f"{url}/create", json=payload)
    if response.status_code == 200:
        print("POST /create - SUCCESS")
    else:       
        print("POST /create - FAILED")
    



