import requests

url = "http://127.0.0.1:8000/api/users/login/"
phone_number = "+8801234567891"
pin = "00000"

response = requests.post(url, data={"phone_number": phone_number, "pin":pin})
token=response.json().get("data")["access"] # Replace with your actual token
print(token)
headers = {
    "Authorization": "Bearer " + token  # Prefix with "Bearer" for common token types
}

response = requests.get("http://127.0.0.1:8000/api/sockets/send-channels/", headers=headers)
print(response.json())