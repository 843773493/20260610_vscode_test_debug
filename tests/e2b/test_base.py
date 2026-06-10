import requests
import os

def test_hello_endpoint() -> None:
    launch_debug = os.getenv("LAUNCH_DEBUG")
    response = requests.get("http://127.0.0.1:8000/hello", timeout=2 if not launch_debug else 10000)

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, world!"}
