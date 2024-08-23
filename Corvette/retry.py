import fitz
import csv
import json
import requests
import time
import http.client, urllib
import sys
from variables import *

def extractPDF(contentsByte, vin):
    try:
        with open(f"{year}/temp.pdf", "wb") as f:
            f.write(contentsByte)
        doc = fitz.open(f"{year}/temp.pdf")
        text = ""
        if len(doc) > 0:
            if len(doc) > 1:
                with open(f"{year}/notes.txt", "a") as nf:
                    nf.write(f"{vin} - Multiple Pages\n")
            page = doc.load_page(0)
            text = page.get_text()
        doc.close()
        return text
    except Exception as e:
        with open(f"{year}/RETRY1.txt", "a") as f:
            f.write(f"{vin}\n")
        return None

def extractInfo(text, vin):
    global year
    global foundVIN

    if text is None:
        print("Received None text. Skipping this VIN.")
        with open(f"{year}/RETRY1.txt", "a") as f:
            f.write(f"{vin}\n")
        return None

    foundVIN += 1
    # Append only the last 6 digits of the VIN to the list and file
    skip_corvette.append(int(vin[-6:]))
    with open(f"{year}/skip_corvette.txt", "a") as file:
        file.write(f"{vin[-6:]}\n")

    lines = text.split('\n')

    field_order = ["vin", "year", "model", "body", "trim", "engine", "transmission", "drivetrain",
                   "exterior_color", "msrp", "dealer", "location", "ordernum", "json", "all_rpos"]
    
    info = {
        "vin": vin,
        "model": "CORVETTE",
        "drivetrain": "RWD",
        "body": "COUPE"
    }

    for i, line in enumerate(lines):
        if "PRICE*" in line:
            info["msrp"] = lines[i + 1].strip().replace("$","").replace(",","").replace(" ","").replace(".00","")
        if "DELIVERED" in line:
            json_data = ' '.join(lines[i + 7:i + 11])
            all_json = json.loads(json_data)
            all_json["Options"] = [option for option in all_json["Options"] if option]
            info.update({
                "dealer": lines[i + 1].strip().replace("\u2013", "-"),
                "location": lines[i + 3].strip(),
                "json": all_json,
                "all_rpos": all_json["Options"],
                "ordernum": all_json["order_number"],
                "year": all_json["model_year"]
            })
            mmc_code = all_json["mmc_code"].replace(' ','')
            all_json["sitedealer_code"] = all_json["sitedealer_code"].replace(' ','')

            for item in info["all_rpos"]:
                if item in body_dict:
                    info["body"] = body_dict[item]
                if item in colors_dict:
                    info["exterior_color"] = colors_dict[item]
                if item in engines_dict:
                    info["engine"] = engines_dict[item]
                if item in trans_dict:
                    info["transmission"] = trans_dict[item]
                if item in trim_dict:
                    info["trim"] = trim_dict[item]
                if item == "HP1":
                    info["drivetrain"] = "AWD"
            if mmc_code in mmc:
                info["model"] = mmc[mmc_code]
                if mmc_code == "1YG07" or mmc_code == "1YG67":
                    info["drivetrain"] = "AWD"
    
    # Reorder the fields
    info_ordered = {field: info.get(field, None) for field in field_order}

    # Check for missing fields
    missing_fields = [field for field, value in info_ordered.items() if value is None]
    if missing_fields:
        with open(f'{year}/missing_info.txt', "a") as f:
            f.write(f"{vin} - {','.join(missing_fields)}\n")
    
    return info_ordered

def writeCSV(pdf_info):
    global year
    if pdf_info is None:
        return
    # Define the field names based on the keys of pdf_info
    fieldnames = pdf_info.keys()
    
    # Open the CSV file in append mode with newline='' to avoid extra newline characters
    with open(f"{year}/{year}_corvette.csv", "a", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write the pdf_info to the CSV file
        writer.writerow(pdf_info)

def processVin(vin):
    global testedVIN
    lastSix = int(vin[-6:])
    urlFirst = "https://cws.gm.com/vs-cws/vehshop/v2/vehicle/windowsticker?vin="
    try:
        newUrl = urlFirst + vin

        max_retries = 3
        retries = 0

        while retries < max_retries:
            try:
                # Get Request
                contentsGet = requests.get(newUrl, headers = {'User-Agent': 'corvette count finder', 'Accept-Language': 'en-US'}, timeout=120)
                contentsByte = contentsGet.content
                contents = contentsGet.text
                time.sleep(1)

                # Check if request returns errorMessage or actual content (meaning a window sticker was found)
                try:
                    # If json content found = no window sticker
                    jsonCont = json.loads(contents)
                    print("\033[30m" + jsonCont["errorMessage"] + "\033[0m")
                # If request returns not a json content = window sticker found
                except json.decoder.JSONDecodeError:
                    with open(f"{year}/corvette_{year}.txt", "a") as f:
                        f.write(f"{vin}\n")
                    print("\033[33mMatch Found For VIN: [" + vin + "].\033[0m")
                    pdf_text = extractPDF(contentsByte, vin)
                    pdf_info = extractInfo(pdf_text, vin)
                    writeCSV(pdf_info)
                break

            except requests.exceptions.ReadTimeout:
                print("Timed out, retrying...")
                retries += 1
                time.sleep(120)
        testedVIN += 1

    except requests.exceptions.RequestException as e:
        if isinstance(e.__cause__, ConnectionResetError):
            print(f"ConnectionResetError: {e}.")
            with open(f'{year}/RETRY1.txt', "a") as f:
                f.write(f"{vin}\n")
            time.sleep(10)
            return
        else:
            print(f"Error: {e}")
            print("Skipping this VIN.")
            with open(f'{year}/RETRY1.txt', "a") as f:
                f.write(f"{vin}\n")
            return

    except KeyboardInterrupt:
        sys.exit(0)

def format_time(seconds):
    hours = int(seconds // 3600)
    remainder = seconds % 3600
    minutes = int(remainder // 60)
    seconds = int(remainder % 60)

    if seconds >= 30:
        minutes += 1
    
    time_parts = []
    if hours == 1:
        time_parts.append(f"{hours} hour")
    elif hours > 1:
        time_parts.append(f"{hours} hours")
    
    if minutes == 1:
        time_parts.append(f"{minutes} minute")
    elif minutes > 1:
        time_parts.append(f"{minutes} minutes")
    
    return ", ".join(time_parts) if time_parts else "< 1 minute"

with open(f"{year}/RETRY1.txt", 'r') as file:
    lines = file.readlines()

totalVIN = len(lines)
foundVIN = 0
testedVIN = 0

estTime = totalVIN * 2
time_str = format_time(estTime)
print(f"ETA: {time_str}")

startTime = time.time()

for vin in lines:
    vin = vin.strip()
    processVin(vin)
print("")

endTime = time.time()
elapsedTime = endTime - startTime
time_str = format_time(elapsedTime)
currentTime = time.strftime("%H:%M:%S", time.localtime())

print(f"Ended: {currentTime} - Elapsed time: {time_str}")
print(f"Tested {testedVIN}/{totalVIN} VIN(s) - Found {foundVIN} match(es)")
