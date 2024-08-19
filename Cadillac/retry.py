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
    except fitz.FileDataError as e:
        return None

def extractInfo(text, vin):
    global year
    global foundVIN

    if text is None:
        print("Received None text. Skipping this VIN.")
        # Write VIN to RETRY.txt file
        with open(f"{year}/RETRY.txt", "a") as f:
            f.write(f"{vin}\n")
        return None
    
    foundVIN += 1
    # Append only the last 6 digits of the VIN to the list and file
    skip_cadillac.append(int(vin[-6:]))
    with open(f"{year}/skip_cadillac.txt", "a") as file:
        file.write(f"{vin[-6:]}\n")

    lines = text.split('\n')
    info = {}
    
    # Define the order of fields
    field_order = ["vin", "year", "model", "body", "trim", "engine", "transmission", "drivetrain",
                   "exterior_color", "msrp", "dealer", "location", "ordernum", "json", "all_rpos"]
    
    info = {
        "vin": vin,
        "body": "SEDAN"
    }
    
    for i, line in enumerate(lines):
        if any(f"{year} {suffix}" in line for suffix in ["CT4 ", "CT5 "]):
            model_info = ' '.join(line.strip().split())
            model_info = model_info.replace("LUX HAUT DE GAMME", "PREMIUM LUXURY").replace("LUXE HAUT DE GAMME", "PREMIUM LUXURY").replace("LUXE", "LUXURY").replace("SERIE V", "V-SERIES").replace("SERIE-V", "V-SERIES")
            modeltrim = model_info[4:].strip().split()
            info["model"] = modeltrim[0]
            info["trim"] = ' '.join(modeltrim[1:])
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
            all_json["mmc_code"] = all_json["mmc_code"].replace(' ','')
            all_json["sitedealer_code"] = all_json["sitedealer_code"].replace(' ','')

            for item in info["all_rpos"]:
                if item in colors_dict:
                    info["exterior_color"] = colors_dict[item]
                if item in engines_dict:
                    info["engine"] = engines_dict[item]
                if item in trans_dict:
                    info["transmission"] = trans_dict[item]
                if item in ext_dict:
                    info["drivetrain"] = ext_dict[item]
    
    # Reorder the fields
    info_ordered = {field: info.get(field, None) for field in field_order}

    # Check for missing fields
    missing_fields = [field for field, value in info_ordered.items() if value is None]
    if missing_fields:
        with open(f'{year}/missing_info.txt', "a") as f:
            f.write(f"{updated_vin} - {','.join(missing_fields)}\n")
    
    return info_ordered

def writeCSV(pdf_info):
    global year
    if pdf_info is None:
        return
    # Define the field names based on the keys of pdf_info
    fieldnames = pdf_info.keys()
    
    # Open the CSV file in append mode with newline='' to avoid extra newline characters
    with open(f"{year}/{year}_cadillac.csv", "a", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write the pdf_info to the CSV file
        writer.writerow(pdf_info)

def processVin(vin):
    global i
    lastSix = int(vin[-6:])
    urlFirst = "https://cws.gm.com/vs-cws/vehshop/v2/vehicle/windowsticker?vin="
    try:
        newUrl = urlFirst + vin

        max_retries = 3
        retries = 0

        while retries < max_retries:
            try:
                # Get Request
                contentsGet = requests.get(newUrl, headers = {'User-Agent': 'caddy count finder', 'Accept-Language': 'en-US'}, timeout=120)
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
                    # Write VIN to txt file
                    with open(f"{year}/caddy_{year}.txt", "a") as f:
                        f.write(f"{updated_vin}\n")
                    # Inform console
                    print("\033[33mMatch Found For VIN: [" + vin + "].\033[0m")
                    pdf_text = extractPDF(contentsByte, vin)
                    pdf_info = extractInfo(pdf_text, vin)
                    writeCSV(pdf_info)
                    testedVIN += 1
                break

            except requests.exceptions.ReadTimeout:
                # Retry request
                print("Timed out, retrying...")
                retries += 1
                time.sleep(120)

    except requests.exceptions.RequestException as e:
        if isinstance(e.__cause__, ConnectionResetError):
            print(f"ConnectionResetError: {e}.")
            # Write VIN to RETRY.txt file
            with open(f'{year}/RETRY.txt', "a") as f:
                f.write(f"{vin}\n")
            vinChanging += 1
            time.sleep(10)
            continue
        else:
            print(f"Error: {e}")
            print("Skipping this VIN.")
            # Write VIN to RETRY.txt file
            with open(f'{year}/RETRY.txt', "a") as f:
                f.write(f"{vin}\n")
            vinChanging += 1  # Move to the next VIN
            continue  # Continue with the next VIN

    except KeyboardInterrupt:
        sys.exit(0)

# Open the file RETRY.txt and read lines
with open(f"{year}/RETRY.txt", 'r') as file:
    lines = file.readlines()

totalVIN = range(lines)
foundVIN = 0
testedVIN = 0

startTime = time.time()

# Process each line
for vin in lines:
    vin = vin.strip()
    processVin(vin)
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
print("Tested {}/{} VIN(s) - Found {} match(es)".format(testedVIN, totalVIN, foundVIN))
