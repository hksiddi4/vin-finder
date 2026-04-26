import json
import requests
import time
import os
import sys
from variables.universal import *

# Main vin processing ---------------------------------------------------------------------------
def processVin(vin):
    global testedVIN, foundVIN
    sticker_folder = os.path.join(path, "Window Stickers")
    pdf_filename = os.path.join(sticker_folder, f"{vin}.pdf")

    urlFirst = f"https://cws.gm.com/vs-cws/vehshop/v2/vehicle/windowsticker?vin="
    try:
        newUrl = urlFirst + vin
        max_retries = 3
        retries = 0

        while retries < max_retries:
            try:
                # Get Request
                contentsGet = requests.get(newUrl, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36', 'Accept-Language': 'en-US'}, timeout=120)
                contentsByte = contentsGet.content
                contents = contentsGet.text
                time.sleep(1)

                if contents == "":
                    time.sleep(3)
                    continue

                try:
                    # JSON found = No sticker
                    json.loads(contents)
                except json.decoder.JSONDecodeError:
                    # Match found
                    os.makedirs(sticker_folder, exist_ok=True)
                    with open(pdf_filename, "wb") as f:
                        f.write(contentsByte)
                    foundVIN += 1
                break

            except requests.exceptions.ReadTimeout:
                retries += 1
                time.sleep(120)
        testedVIN += 1

    except Exception as e:
        with open(f'{path}/RETRY.txt', "a") as f:
            f.write(f"{vin}\n")
        return

# Model Selection Logic (Kept as is)
model_map = {
    "CT4": "CT4", "CT5": "CT5", "CT6": "CT6",
    "CAMARO": "CAMARO",
    "HUMMER EV": "HUMMER EV",
    "SILVERADO EV": "SILVERADO EV",
    "SIERRA EV": "SIERRA EV",
    "ESCALADE IQ": "ESCALADE IQ",
    "ESCALADE": "ESCALADE", "ESCALADE ESV": "ESCALADE ESV",
}

while True:
    model = input('Enter model to use:\n').upper()
    if model == "CORVETTE":
        mmc = mmc_2019 if int(year) == 2019 else mmc_2020
        break
    elif model in model_map:
        model = model_map[model]
        break
    else:
        print("\033[91mPlease enter a valid model or check the year.\033[0m\n")

path = f"{model}/{year}"
if model in ("CT4", "CT5"):
    path = f"CT4-CT5/{year}"
elif model == "ESCALADE ESV":
    path = f"ESCALADE/{year}"

with open(f"{path}/RETRY.txt", 'r') as file:
    lines = [line.strip() for line in file.readlines()]

# --- PRE-PROCESSING & PROGRESS BAR LOGIC ---
totalVIN = len(lines)
foundVIN = 0
testedVIN = 0

# 1. Filter existing PDFs
sticker_folder = os.path.join(path, "Window Stickers")
to_process = []
skipped_count = 0

for vin in lines:
    if os.path.exists(os.path.join(sticker_folder, f"{vin}.pdf")):
        skipped_count += 1
    else:
        to_process.append(vin)

# 2. Inform user of skips
if skipped_count > 0:
    print(f"\033[33mSkipping {skipped_count} VIN(s) (Already downloaded).\033[0m")
    foundVIN += skipped_count
    testedVIN += skipped_count

# 3. Process remaining with progress bar
active_total = len(to_process)
if active_total > 0:
    estTime = active_total * 2
    print(f"\033[31mETA for {active_total} new VINs: {format_time(estTime)}\033[0m")
    
    startTime = time.time()
    
    for i, vin in enumerate(to_process):
        # Update progress bar
        percent = (i + 1) / active_total
        bar_length = 20
        filled = int(bar_length * percent)
        bar = "█" * filled + "-" * (bar_length - filled)
        
        # \r brings the cursor to the start of the line, allowing us to overwrite it
        sys.stdout.write(f"\rProgress: |{bar}| {i+1}/{active_total} Processing: {vin}")
        sys.stdout.flush()
        
        processVin(vin)

    print("\n\033[32mDownload complete.\033[0m")
else:
    print("\033[32mAll VINs are already up to date.\033[0m")
    startTime = time.time()

endTime = time.time()
elapsedTime = endTime - startTime
time_str = format_time(elapsedTime)
currentTime = time.strftime("%H:%M:%S", time.localtime())

print(f"\nEnded: {currentTime} - Elapsed time: {time_str}")
print(f"Tested {testedVIN}/{totalVIN} VIN(s) - Found \033[93m{foundVIN}\033[0m match(es)")
