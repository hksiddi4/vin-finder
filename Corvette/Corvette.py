import fitz
import csv
import json
import requests
import time
from variables import *

def extractPDF(contentsByte, updated_vin):
    try:
        with open(f'{year}/temp.pdf', "wb") as f:
            f.write(contentsByte)
        doc = fitz.open(f'{year}/temp.pdf')
        text = ""
        if len(doc) > 0:
            if len(doc) > 1:
                with open(f"{year}/notes.txt", "a") as nf:
                    nf.write(f"{updated_vin} - Multiple Pages\n")
            page = doc.load_page(0)
            text = page.get_text()
        doc.close()
        return text
    except fitz.FileDataError as e:
        return None

def extractInfo(text, updated_vin):
    global year
    global foundVIN
    
    if text is None:
        print("Received None text. Skipping this VIN.")
        # Write VIN to RETRY.txt file
        with open(f'{year}/RETRY.txt', "a") as f:
            f.write(f"{updated_vin}\n")
        return
    
    foundVIN += 1
    # Append only the last 6 digits of the VIN to the list and file
    skip_corvette.append(updated_vin)
    with open(f"{year}/skip_corvette.txt", "a") as file:
        file.write(f"{updated_vin[-6:].zfill(6)}\n")

    lines = text.split('\n')
    info = {}
    
    # Define the order of fields
    field_order = ["vin", "year", "model", "body", "trim", "engine", "transmission", "drivetrain",
                   "exterior_color", "msrp", "dealer", "location", "ordernum", "json", "all_rpos"]
    
    info = {
        "vin": updated_vin,
        "model": "CORVETTE",
        "drivetrain": "RWD",
        "body": "COUPE"
    }

    for i, line in enumerate(lines):
        if any(f"{year} {suffix}" in line for suffix in ["CORVETTE ", "COUPE CORVETTE ", "CABRIOLET CORVETTE "]):
            model_info = ' '.join(line.strip().split())
            modeltrim = model_info[4:].strip().split()
            info["trim"] = ' '.join(modeltrim[1:]).replace(" CONVERTIBLE", "").replace(" COUPE", "").replace("CORVETTE ", "").replace(" CONV", "")
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
                if item in body_dict:
                    info["body"] = body_dict[item]
                if item in colors_dict:
                    info["exterior_color"] = colors_dict[item]
                if item in engines_dict:
                    info["engine"] = engines_dict[item]
                if item in trans_dict:
                    info["transmission"] = trans_dict[item]
                if item == "HP1":
                    info["drivetrain"] = "AWD"
    
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
    fieldnames = pdf_info.keys()

    with open(f"{year}/{year}_corvette.csv", "a", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write the pdf_info to the CSV file
        writer.writerow(pdf_info)

# Main vin processing ---------------------------------------------------------------------------
def processVin(urlIdent, vinChanging, endVIN, yearDig):
    global testedVIN
    urlFirst = "https://cws.gm.com/vs-cws/vehshop/v2/vehicle/windowsticker?vin=1G1Y"

    # Keep going until a specific stopping point
    while vinChanging <= endVIN:
        try:
            # Build the URL (first half + identify trim/gear + check digit + year digit + 0 + incrementing VIN)
            matchedVIN = "1G1Y" + urlIdent + "X" + yearDig + "0" + str(vinChanging)
            updated_vin = calculate_check_digit(matchedVIN)
            newUrl = urlFirst + urlIdent + updated_vin[8:11] + str(vinChanging).zfill(6)

            max_retries = 3
            retries = 0

            while retries < max_retries:
                try:
                    # Get Request
                    contentsGet = requests.get(newUrl, headers = {'User-Agent': 'corvette count finder', 'Accept-Language': 'en-US'}, timeout=120)
                    contentsByte = contentsGet.content
                    contents = contentsGet.text
                    time.sleep(1)

                    try:
                        # If json content found = no window sticker
                        jsonCont = json.loads(contents)
                        print("\033[30m" + jsonCont["errorMessage"] + "\033[0m")
                    # If request returns not a json content = window sticker found
                    except json.decoder.JSONDecodeError:
                        with open(f"{year}/corvette_{year}.txt", "a") as f:
                            f.write(f"{updated_vin}\n")
                        print("\033[33mMatch Found For VIN: [" + updated_vin + "].\033[0m")
                        pdf_text = extractPDF(contentsByte, updated_vin)
                        pdf_info = extractInfo(pdf_text, updated_vin)
                        writeCSV(pdf_info)

                    # Increment VIN by 1
                    vinChanging += 1
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
                    f.write(f"{updated_vin}\n")
                vinChanging += 1
                time.sleep(10)
                continue
            else:
                print(f"Error: {e}")
                print("Skipping this VIN.")
                # Write VIN to RETRY.txt file
                with open(f'{year}/RETRY.txt', "a") as f:
                    f.write(f"{updated_vin}\n")
                vinChanging += 1
                continue
        except KeyboardInterrupt:
            break

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

while True:
    vinChanging_input = input('Enter last 6 numbers of the VIN to start at:\n')
    if vinChanging_input.isdigit() and len(vinChanging_input) == 6:
        vinChanging = int(vinChanging_input)
        break
    else:
        print("Please enter a valid 6-digit number.")
while True:
    endVIN_input = input('Enter last 6 numbers of the VIN to stop at:\n')
    if endVIN_input.isdigit() and len(endVIN_input) == 6:
        endVIN = int(endVIN_input)
        break
    else:
        print("Please enter a valid 6-digit number.")
if int(year) >= 2024:
    while True:
        eray = input('Run as E-Ray? (Y/N)\n').strip().lower()

        if eray == "y":
            tempName = f"urlIdent_eray_list"
            urlChosenList = globals()[tempName]
            break
        elif eray == "n":
            urlChosenList = urlIdent_list
            break
        else:
            print("Please enter Y or N.")
elif int(year) >= 2023:
    while True:
        z06 = input('Run as Z06? (Y/N)\n').strip().lower()

        if z06 == "y":
            tempName = f"urlIdent_z06_list"
            urlChosenList = globals()[tempName]
            break
        elif z06 == "n":
            urlChosenList = urlIdent_list
            break
        else:
            print("Please enter Y or N.")
elif int(year) >= 2025:
    while True:
        zr1 = input('Run as ZR1? (Y/N)\n').strip().lower()

        if zr1 == "y":
            tempName = f"urlIdent_zr1_list"
            urlChosenList = globals()[tempName]
            break
        elif zr1 == "n":
            urlChosenList = urlIdent_list
            break
        else:
            print("Please enter Y or N.")
else:
    urlChosenList = urlIdent_list

totalVIN = int(endVIN_input) - int(vinChanging_input)
totalIdent = 0
foundVIN = 0
testedVIN = 0

startTime = time.time()

# Process request through all variations of trim/gears
for urlIdent in chosenList:
    urlList = len(chosenList)
    print(f"Testing configuration ({str(totalIdent)}/{str(urlList)}): {urlIdent} -------------------------------")
    processVin(urlIdent, vinChanging, endVIN, yearDig)
    print("")
    totalIdent += 1

endTime = time.time()
elapsedTime = endTime - startTime
time_str = format_time(elapsedTime)
currentTime = time.strftime("%H:%M:%S", time.localtime())

print(f"Ended: {currentTime} - Elapsed time: {time_str}")
print(f"Tested {testedVIN}/{totalVIN} VIN(s) - Found {foundVIN} match(es)")
