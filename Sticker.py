import json
import requests
import time
import http.client, urllib

vinChanging = int(input('Enter last 6 numbers of the VIN to start at: \n'))
endVIN = int(input('Enter last 6 numbers of the VIN to stop at:\n'))

# Working Check Digit Calculator
# Step 1: Assign values to letters
alpha_numeric_conversion = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'P': 7, 'R': 9, 'S': 2,
    'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9
}

# Step 2: Position and Weight Factor
weight_factors = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]

# Function to calculate check digit
def calculate_check_digit(matchedVIN):
    total = 0
    for i, char in enumerate(matchedVIN):
        if char.isdigit():
            total += int(char) * weight_factors[i]
        elif char in alpha_numeric_conversion:
            total += alpha_numeric_conversion[char] * weight_factors[i]
        else:
            raise ValueError(f"Invalid character in VIN: {char}")
    
    # Step 3: Divide the total by 11 and find the remainder
    remainder = total % 11
    
    # Step 4: Calculate the check digit or use 'X' if remainder is 10
    check_digit = str(remainder) if remainder < 10 else 'X'
    
    # Insert the check digit at the ninth position and return the updated VIN
    updated_vin = matchedVIN[:8] + check_digit + matchedVIN[9:]
    return updated_vin

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

def processVin(urlIdent, vinChanging, endVIN):
    urlFirst = "https://cws.gm.com/vs-cws/vehshop/v2/vehicle/windowsticker?vin=1G1F"
    urlSecond = "R0"

    # Read last recorded VIN checked from lastVin.txt
    #with open("lastVin.txt", "r") as f:
    #    vinChanging = int(f.readline())

    # What incrementing VIN to start at
    #vinChanging = 106900
    #print("Testing with check digit: " + str(checkDig))

    # Keep going until a specific stopping point
    while vinChanging <= endVIN:
        try:
            # Build the URL (first half + identify trim/gear + check digit + second half + incrementing VIN)
            matchedVIN = "1G1F" + urlIdent + "XR0" + str(vinChanging)
            updated_vin = calculate_check_digit(matchedVIN)
            newUrl = urlFirst + urlIdent + updated_vin[8:11] + str(vinChanging)

            max_retries = 3
            retries = 0

            while retries < max_retries:
                try:
                    # Get Request
                    contents = requests.get(newUrl, headers = {'User-Agent': 'camaro ce finder version 0.08 probably', 'Accept-Language': 'en-US'}, timeout=120)
                    contents = contents.text
                    time.sleep(1)

                    # Check if request returns errorMessage or actual content (meaning a window sticker was found)
                    try:
                        # If json content found = no window sticker
                        jsonCont = json.loads(contents)
                        print(jsonCont["errorMessage"])
                    # If request returns not a json content = window sticker found
                    except json.decoder.JSONDecodeError:
                        # Write VIN to ceVin.txt file
                        with open("ceVin.txt", "a") as f:
                            f.write(str("\n" + updated_vin))
                        # Inform console
                        print("Match Found For VIN: [" + updated_vin + "].")
                        # Send notification to phone
                        sendNotif(updated_vin)

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
#checkDig_list = ["X"] + list(range(10))

# Process request through all variations of trim/gears
for urlIdent in urlIdent_list:
#    for checkDig in checkDig_list:
    print("Testing configuration: " + urlIdent)
    processVin(urlIdent, vinChanging, endVIN)
    print("")

t = time.localtime()
currentTime = time.strftime("%H:%M:%S", t)
print("Ended:", currentTime)
# https://www.camaro6.com/forums/showthread.php?t=426194 - VIN Breakdown
# 2024 model year = R

# Unchanged VIN Variants
# 1G1FJ1R60R0 - Done (105000 - 108519) - In Progress (108520 - 111000) - 108520 Stopped (-raised sleep to 5)
# 1G1FJ3D64R0

# 1G1FK1R60R0
# 1G1FK3D6XR0


# 1G1FJ - Manual
#   1G1FJ1R6XR0 - Coupe - X = check digit (0~9, X)
#   1G1FJ3D6XR0 - Conv.
# 1G1FK - Auto
#   1G1FK1R6XR0 - Coupe
#   1G1FK3D6XR0 - Conv.