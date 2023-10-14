import json
import requests
import time
import http.client, urllib

vinChanging = int(input('Enter last 6 numbers of the VIN to start at: \n'))
endVIN = int(input('Enter last 6 numbers of the VIN to stop at:\n'))

def sendNotif(matchedVIN):
    url = "https://cws.gm.com/vs-cws/vehshop/v2/vehicle/windowsticker?vin=" + matchedVIN

    # https://pushover.net/api#urls    
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
        urllib.parse.urlencode({
            "token": "as9s2tyvtphyu6ucgdhxuxsjcy46b1",
            "user": "u6yo6avbcsh5y2boszyodgk3kjxen4",
            "title": "Matched VIN",
            "message": matchedVIN,
            "url": url,
            "url_title": "Window Sticker",
        }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()

def processVin(urlIdent, checkDig, vinChanging, endVIN):
    urlFirst = "https://cws.gm.com/vs-cws/vehshop/v2/vehicle/windowsticker?vin=1G1F"
    urlSecond = "R0"

    # Read last recorded VIN checked from lastVin.txt
    #with open("lastVin.txt", "r") as f:
    #    vinChanging = int(f.readline())

    # What incrementing VIN to start at
    #vinChanging = 106900
    print("Testing with check digit: " + str(checkDig))

    # Keep going until a specific stopping point
    while vinChanging <= endVIN:
        try:
            # Wait 5 seconds then build the URL (first half + identify trim/gear + check digit + second half + incrementing VIN)
            time.sleep(1)
            newUrl = urlFirst + urlIdent + str(checkDig) + urlSecond + str(vinChanging)

            # GET request
            max_retries = 3
            retries = 0

            while retries < max_retries:
                try:
                    contents = requests.get(newUrl, headers = {'User-Agent': 'camaro ce finder version 0.08 probably', 'Accept-Language': 'en-US'})
                    contents = contents.text

                    # Check if request returns errorMessage or actual content (meaning a window sticker was found)
                    try:
                        # If json content found = no window sticker
                        jsonCont = json.loads(contents)
                        #print(jsonCont["errorMessage"])
                        print(jsonCont)
                    # If request returns not a json content = window sticker found
                    except json.decoder.JSONDecodeError as e:
                        # Write VIN to ceVin.txt file
                        matchedVIN = newUrl[-17:]
                        #with open("ceVin.txt", "a") as f:
                        #    f.write(str("\n" + matchedVIN))
                        # Inform console
                        print("Match Found For VIN: [" + matchedVIN + "].")
                        # Send notification to phone
                        #sendNotif(matchedVIN)

                    # Increment VIN by 1
                    vinChanging += 1
                    break

                except requests.exceptions.ReadTimeout:
                    # Retry request
                    print("Timed out, retrying...")
                    retries += 1
                    time.sleep(120)
            
        # When canceled in console, record last checked VIN to lastVin.txt
        except KeyboardInterrupt:
            #with open("lastVin.txt", "w") as f:
            #    f.write(str(vinChanging))
                break

#with open("lastVin.txt", "w") as f:
#        f.write(str(vinChanging))
# Manual/Auto/Coupe/Conv. Differentiations
urlIdent_list = [
    "J1R6", # Manual Coupe
    "J3D6", # Manual Conv.
    "K1R6", # Auto Coupe
    "K3D6"  # Auto Conv.
]

# List of "X" and 0-9 for check digit
checkDig_list = ["X"] + list(range(10))

# Process request through all variations of trim/gears
for urlIdent in urlIdent_list:
    for checkDig in checkDig_list:
        processVin(urlIdent, checkDig, vinChanging, endVIN)
