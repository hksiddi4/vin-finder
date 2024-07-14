import fitz
import csv
import json
import requests
import time
import http.client, urllib
from variables import *

# Extract text from PDF -------------------------------------------------------------------------
def extractPDF(contentsGet, updated_vin):
    try:
        with open(f'{year}/temp.pdf', "wb") as f:
            f.write(contentsGet.content)
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
        return None
    
    foundVIN += 1
    # Append only the last 6 digits of the VIN to the list and file
    skip_cadillac.append(updated_vin)
    with open(f"{year}/skip_cadillac.txt", "a") as file:
        file.write(f"{updated_vin[-6:].zfill(6)}\n")

    lines = text.split('\n')
    info = {}
    
    # Define the order of fields
    field_order = ["vin", "year", "model", "body", "trim", "engine", "transmission", "drivetrain",
                   "exterior_color", "msrp", "dealer", "location", "ordernum", "json", "all_rpos"]
    
    info["vin"] = updated_vin
    info["body"] = "SEDAN"
    for i, line in enumerate(lines):
        if f"{year} CT4 " in line or f"{year} CT5 " in line:
            model_info = ' '.join(line.strip().split())
            model_info = model_info.replace("LUX HAUT DE GAMME", "PREMIUM LUXURY").replace("LUXE HAUT DE GAMME", "PREMIUM LUXURY").replace("LUXE", "LUXURY").replace("SERIE V", "V-SERIES").replace("SERIE-V", "V-SERIES")
            modeltrim = model_info[4:].strip().split()
            info["model"] = modeltrim[0]
            info["trim"] = ' '.join(modeltrim[1:])
        if "PRICE*" in line:
            info["msrp"] = lines[i + 1].strip()
        if "DELIVERED" in line:
            info["dealer"] = lines[i + 1].strip().replace("\u2013", "-")
            info["location"] = lines[i + 3].strip()
            json_data = lines[i + 7:i + 11]
            all_json = json.loads(' '.join(json_data))
            info["json"] = all_json
            all_rpos = all_json.get("Options",[])
            all_rpos_filt = [item for item in all_rpos if item]
            info["all_rpos"] = all_rpos_filt

            for item in all_rpos_filt:
                if item in colors_dict:
                    info["exterior_color"] = colors_dict[item]
                    continue
                if item in engines_dict:
                    info["engine"] = engines_dict[item]
                    continue
                if item in trans_dict:
                    info["transmission"] = trans_dict[item]
                    continue
                if item in ext_dict:
                    info["drivetrain"] = ext_dict[item]
                    continue

            if "order_number" in all_json:
                info["ordernum"] = all_json["order_number"]

            if "model_year" in all_json:
                info["year"] = all_json["model_year"]
    
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

# Main vin processing ---------------------------------------------------------------------------
def processVin(urlIdent, vinChanging, endVIN, yearDig):
    global totalVIN
    global foundVIN
    urlFirst = "https://cws.gm.com/vs-cws/vehshop/v2/vehicle/windowsticker?vin=1G6D"

    # Keep going until a specific stopping point
    while vinChanging <= endVIN:
        if vinChanging in skip_cadillac or vinChanging in skip_camaro:
            print("\033[30mExisting sequence, skipping\033[0m")
            vinChanging += 1
            continue
        else:
            try:
                # Build the URL (first half + identify trim/gear + check digit + year digit + 0 + incrementing VIN)
                matchedVIN = "1G6D" + urlIdent + "X" + yearDig + "0" + str(vinChanging)
                updated_vin = calculate_check_digit(matchedVIN)
                newUrl = urlFirst + urlIdent + updated_vin[8:11] + str(vinChanging).zfill(6)

                max_retries = 3
                retries = 0

                while retries < max_retries:
                    try:
                        # Get Request
                        contentsGet = requests.get(newUrl, headers = {'User-Agent': 'caddy count finder', 'Accept-Language': 'en-US'}, timeout=120)
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
                            print("\033[33mMatch Found For VIN: [" + updated_vin + "].\033[0m")
                            pdf_text = extractPDF(contentsGet, updated_vin)
                            pdf_info = extractInfo(pdf_text, updated_vin)
                            writeCSV(pdf_info)

                        # Increment VIN by 1
                        vinChanging += 1
                        totalVIN += 1
                        break

                    except requests.exceptions.ReadTimeout:
                        # Retry request
                        print("Timed out, retrying...")
                        retries += 1
                        time.sleep(120)

            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
                if isinstance(e, requests.exceptions.ConnectionError) and isinstance(e.__cause__, ConnectionResetError):
                    # Write VIN to RETRY.txt file
                    with open(f'{year}/RETRY.txt', "a") as f:
                        f.write(f"{updated_vin}\n")
                    vinChanging += 1  # Move to the next VIN
                    print("ConnectionResetError occurred. Retrying...")
                    continue  # Continue with the next VIN
                else:
                    print("Skipping this VIN.")
                    # Write VIN to RETRY.txt file
                    with open(f'{year}/RETRY.txt', "a") as f:
                        f.write(f"{updated_vin}\n")
                    vinChanging += 1  # Move to the next VIN
                    continue  # Continue with the next VIN

            # When canceled in console, record last checked VIN to lastVin.txt
            except KeyboardInterrupt:
                break

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
if year >= 2022:
    while True:
        blackwing = input('Run as Blackwing? (Y/N)\n').strip().lower()

        if blackwing == "y":
            tempName = f"urlIdent_blackwing_list_{year}"
            urlChosenList = globals()[tempName]
            break
        elif blackwing == "n":
            urlChosenList = urlIdent_list
            break
        else:
            print("Please enter Y or N.")
else:
    urlChosenList = urlIdent_list

totalVIN = 0
foundVIN = 0
i = 1

startTime = time.time()

# Process request through all variations of trim/gears
for urlIdent in urlChosenList:
    urlList = len(urlChosenList)
    print("Testing configuration (" + str(i) + "/" + str(urlList) + "): " + urlIdent + " -------------------------------")
    processVin(urlIdent, vinChanging, endVIN, yearDig)
    print("")
    i += 1

endTime = time.time()
elapsedTime = endTime - startTime
elapsedTime = round(elapsedTime,1)

hours = int(elapsedTime // 3600)
remainder = elapsedTime % 3600
minutes = int(remainder // 60)
seconds = int(remainder  % 60)

with open(f'{year}/time.txt', "a") as f:
    f.write("{},{},{}\n".format(vinChanging_input, endVIN_input, elapsedTime))

t = time.localtime()
currentTime = time.strftime("%H:%M:%S", t)
print("Ended:", currentTime, " - Elapsed time: {} hour(s), {} minute(s), {} second(s)".format(hours, minutes, seconds))
print("Tested {} VIN(s) - Found {} match(es)".format(totalVIN, foundVIN))
