import requests


# for auth
# url = "http://127.0.0.1:8000/api/users/login/"
# phone_number = "+8801234567891"
# pin = "00000"
#
# response = requests.post(url, data={"phone_number": phone_number, "pin":pin})
# token=response.json().get("data")["access"] # Replace with your actual token
# print(token)
# headers = {
#     "Authorization": "Bearer " + token  # Prefix with "Bearer" for common token types
# }
#
# response = requests.get("http://127.0.0.1:8000/api/sockets/send-channels/", headers=headers)
# print(response.json())


# for sms
import requests
#
url = "https://gateway.sms77.io/api/sms"
key = "191b46dc1f96a04F760aB932F9942936751CB62375c14e2Ab2b87e9b6F48882D"
querystring = {"p":key ,"to":"+8801754612819","text":"helo world"}

headers = {
	"X-RapidAPI-Key": "191b46dc1f96a04F760aB932F9942936751CB62375c14e2Ab2b87e9b6F48882D",
	"X-RapidAPI-Host": "sms77io.p.rapidapi.com"
}

response = requests.get(url,  params=querystring)

print(response.json())

