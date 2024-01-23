import requests
from io import BytesIO

# for auth
url = "http://127.0.0.1:8000/api/users/login/"
phone_number = "+8801234567892"
pin = "12345"

response = requests.post(url, data={"phone_number": phone_number, "pin":pin})
token=response.json().get("data")["access"] # Replace with your actual token
print(token)
headers = {
    "Authorization": "Bearer " + token  # Prefix with "Bearer" for common token types
}
image_url = "https://media.istockphoto.com/id/1455658894/photo/system-hacked-warning-alert-on-notebook-cyber-attack-on-computer-network-virus-spyware.jpg?s=612x612&w=is&k=20&c=e254EEMWIBpco8NFwo9dumITm5lM9HIgrXU5oPSA-hY="
# stream = None
with open("media/qr_e8wy4HI.png", "rb") as image_file:
    stream = BytesIO(image_file.read())

data = {
    "nid_front": stream.getvalue()
}
print("asdas", stream.getvalue())
# response = requests.patch(
#     "http://127.0.0.1:8000/api/users/nid-front-add/",
#     headers=headers, data=data)
# try:
#     print("Status code: ", response.status_code)
#     print(response.json())
# except:
#     # print(response.text)
#     pass
# @extend_schema(
#         responses={
#             200: OpenApiResponse(
#                 response=WidgetSerializer,
#                 examples=[
#                     OpenApiExample(
#                         "Undamaged Widget",
#                         value={
#                             "is_damaged": False,
#                             "damage_reason": "",
#                         },
#                     ),
#                     OpenApiExample(
#                         "Damaged Widget",
#                         value={
#                             "is_damaged": True,
#                             "damage_reason": "Someone broke it.",
#                         },
#                     ),
#                 ],
#             )
#         }
#     )
