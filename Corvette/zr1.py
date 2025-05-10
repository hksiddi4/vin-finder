import itertools
import json
import requests
import time
import sys
from variables import *

def processVin(vin):
    global foundVIN
    urlFirst = "https://cws.gm.com/vs-cws/vehshop/v2/vehicle/windowsticker?vin="
    vin = calculate_check_digit(vin)

    try:
        newUrl = urlFirst + vin

        max_retries = 3
        retries = 0

        while retries < max_retries:
            try:
                # Get Request
                contentsGet = requests.get(newUrl, headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36', 'Accept-Language': 'en-US'}, timeout=60)
                contents = contentsGet.text
                time.sleep(1)

                # Retry if contents is empty
                if contents == "":
                    print("Empty content received. Retrying...")
                    time.sleep(3)
                    continue

                # Check if request returns errorMessage or actual content (meaning a window sticker was found)
                try:
                    # If json content found = no window sticker
                    jsonCont = json.loads(contents)
                    print("\033[30m" + jsonCont["errorMessage"] + "\033[0m")
                # If request returns not a json content = window sticker found
                except json.decoder.JSONDecodeError:
                    # Inform console
                    print("\033[33mMatch Found For VIN: [" + vin + "].\033[0m")
                    with open('ZR1.txt', 'a') as file:
                        file.write(f"{vin}\n")
                    foundVIN += 1
                break

            except requests.exceptions.ReadTimeout:
                # Retry request
                print("Timed out, retrying...")
                retries += 1
                time.sleep(120)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        if isinstance(e, requests.exceptions.ConnectionError) and isinstance(e.__cause__, ConnectionResetError):
            print("ConnectionResetError occurred. Retrying...")
            return
        else:
            print("Unknown error occurred. Skipping this VIN.")
            # Write VIN to RETRY.txt file
            with open(f"2025/RETRY.txt", "a") as f:
                f.write(f"{vin}\n")
            return

    except KeyboardInterrupt:
        sys.exit(0)

# Defining the ranges and parts
part1 = ["1G1Y"]
equipment = ["G", "J"]
body = ["2", "3"]
safety = ["D"]
engine = ["7"]
check_digit = ["X"]
modelYear = ["S"]
assembly_plant = ["5"]
#sequence = ["200001", "300001", "400001", "700001", "800001", "900001"]
sequence = ["800001"]

# Generating all combinations
combinations = list(itertools.product(part1, equipment, body, safety, engine, check_digit, modelYear, assembly_plant, sequence))

# Formatting combinations into VIN strings
vin_combinations = [''.join(combination) for combination in combinations]

# Total number of combinations
total_combinations = len(vin_combinations)
print(f"Total possible combinations: {total_combinations}")

foundVIN = 0
i = 0

startTime = time.time()

# Process each line
for vin in vin_combinations:
    vin = vin.strip()
    processVin(vin)
    i += 1
print("")

endTime = time.time()
elapsedTime = endTime - startTime

hours = int(elapsedTime // 3600)
remainder = elapsedTime % 3600
minutes = int(remainder // 60)
seconds = int(remainder  % 60)

time_parts = []
if hours == 1:
    time_parts.append(f"{hours} hour")
elif hours > 1:
    time_parts.append(f"{hours} hours")
if minutes == 1:
    time_parts.append(f"{minutes} minute")
elif minutes > 1:
    time_parts.append(f"{minutes} minute(s)")

time_str = ", ".join(time_parts) + f", {seconds} second" if time_parts else f"{seconds} seconds"

t = time.localtime()
currentTime = time.strftime("%H:%M:%S", t)
print("Ended:", currentTime, " - Elapsed time:", time_str)
print("Tested {}/{} VIN(s) - Found {} match(es)".format(i, total_combinations, foundVIN))
