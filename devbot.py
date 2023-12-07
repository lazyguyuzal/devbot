###############################################################
# CET1112 - Devbot.py Student Assessment Script
# Professor: Jeff Caldwell
# Year: 2023-09
###############################################################

# 1. Import libraries for API requests, JSON formatting, and epoch time conversion.

import requests
import json
import time

# 2. Complete the if statement to ask the user for the Webex access token.
choice = input("Do you wish to use the hard-coded Webex token? (y/n) ")

if choice.lower() == "n":
    token = None
    while not token:
        token = input("Please enter your Webex token: ")
        if not token:
            print("Invalid token. Try again!")
    accessToken = f"Bearer {token}"
else:
    accessToken = "Bearer MzI4ZGU0NzctNjg0Zi00ZmVlLTgwZDEtOTg1YzBkNTA0YWQzZjhhNzFlZWMtZmI1_PC75_f1a9c66d-3eff-454d-9c51-a4e0afcd770b"

# 3. Provide the URL to the Webex Teams room API.
r = requests.get(
    "https://webexapis.com/v1/rooms", headers={"Authorization": accessToken}
)

#####################################################################################
# DO NOT EDIT ANY BLOCKS WITH r.status_code
if not r.status_code == 200:
    raise Exception(
        "Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(
            r.status_code, r.text
        )
    )
######################################################################################

# 4. Create a loop to print the type and title of each room.
print("List of rooms:")
rooms = r.json()["items"]
for room in rooms:
    print(f"Room name: {room['title']}")
#######################################################################################
# SEARCH FOR WEBEX TEAMS ROOM TO MONITOR
#  - Searches for user-supplied room name.
#  - If found, print "found" message, else prints error.
#  - Stores values for later use by bot.
# DO NOT EDIT CODE IN THIS BLOCK
#######################################################################################

while True:
    roomNameToSearch = input("Which room should be monitored for /location messages? ")
    roomIdToGetMessages = None

    for room in rooms:
        if room["title"].find(roomNameToSearch) != -1:
            print("Found rooms with the word " + roomNameToSearch)
            print(room["title"])
            roomIdToGetMessages = room["id"]
            roomTitleToGetMessages = room["title"]
            print("Found room : " + roomTitleToGetMessages)
            break

    if roomIdToGetMessages == None:
        print("Sorry, I didn't find any room with " + roomNameToSearch + " in it.")
        print("Please try again...")
    else:
        break

######################################################################################
# WEBEX TEAMS BOT CODE
#  Starts Webex bot to listen for and respond to /location messages.
######################################################################################

while True:
    time.sleep(1)
    GetParameters = {"roomId": roomIdToGetMessages, "max": 1}
    # 5. Provide the URL to the Webex Teams messages API.
    r = requests.get(
        "https://webexapis.com/v1/messages",
        params=GetParameters,
        headers={"Authorization": accessToken},
    )

    if not r.status_code == 200:
        raise Exception(
            "Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(
                r.status_code, r.text
            )
        )

    json_data = r.json()
    if len(json_data["items"]) == 0:
        raise Exception("There are no messages in the room.")

    messages = json_data["items"]
    message = messages[0]["text"]
    print("Received message: " + message)

    if message.find("/") == 0:
        location = message[1:]
        # 6. Provide your MapQuest API consumer key.
        mapsAPIGetParameters = {
            "location": location,
            "key": "tCEHxqknRHIJBgY44snePgi8ilkwzj88",
        }
        # 7. Provide the URL to the MapQuest GeoCode API.
        r = requests.get(
            "https://www.mapquestapi.com/geocoding/v1/address",
            params=mapsAPIGetParameters,
        )
        json_data = r.json()

        if not json_data["info"]["statuscode"] == 0:
            raise Exception(
                "Incorrect reply from MapQuest API. Status code: {}".format(
                    r.statuscode
                )
            )

        locationResults = json_data["results"][0]["providedLocation"]["location"]
        print("Location: " + locationResults)

        # 8. Provide the MapQuest key values for latitude and longitude.
        locationLat = json_data["results"][0]["locations"][0]["displayLatLng"]["lat"]
        locationLng = json_data["results"][0]["locations"][0]["displayLatLng"]["lng"]
        print("Location GPS coordinates: " + str(locationLat) + ", " + str(locationLng))

        ssAPIGetParameters = {"lat": locationLat, "lon": locationLng}
        # 9. Provide the URL to the Sunrise/Sunset API.
        r = requests.get(
            "https://api.sunrise-sunset.org/json?", params=ssAPIGetParameters
        )

        json_data = r.json()

        if not "results" in json_data:
            raise Exception(
                "Incorrect reply from sunrise-sunset.org API. Status code: {}. Text: {}".format(
                    r.status_code, r.text
                )
            )

        print(json_data)

        # 10. Provide the Sunrise/Sunset key value for day_length.
        dayLengthSeconds = json_data["results"]["day_length"]
        sunriseTime = json_data["results"]["sunrise"]
        sunsetTime = json_data["results"]["sunset"]

        # 11. Complete the code to format the response message.
        responseMessage = "In {} the sun will rise at {} and will set at {} . The day will last {} seconds.".format(
            locationResults, sunriseTime, sunsetTime, dayLengthSeconds
        )

        print("Sending to Webex Teams: " + responseMessage)

        # 12. Complete the code to post the message to the Webex Teams room.
        HTTPHeaders = {"Authorization": accessToken, "Content-Type": "application/json"}
        PostData = {"roomId": roomIdToGetMessages, "text": responseMessage}

        r = requests.post(
            "https://webexapis.com/v1/messages",
            data=json.dumps(PostData),
            headers=HTTPHeaders,
        )
        if not r.status_code == 200:
            raise Exception(
                "Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(
                    r.status_code, r.text
                )
            )
