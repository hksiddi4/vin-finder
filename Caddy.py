import fitz
import csv
import json
import requests
import time
import http.client, urllib
from variables import *

startTime = time.time()

while True:
    year = input('Enter year to test:\n')

    if year in years:
        yearDig = years[year]
        break
    else:
        print("Invalid year (enter 2020-2024).")

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
print("")
totalVIN = endVIN - vinChanging + 1
foundVIN = 0

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

# Extract text from PDF -------------------------------------------------------------------------
def extractPDF(pdf_url):
    response = requests.get(pdf_url)
    with open("temp.pdf", "wb") as f:
        f.write(response.content)
    doc = fitz.open("temp.pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def extractInfo(text):
    lines = text.split('\n')
    info = {}
    
    # Define the order of fields
    field_order = ["vin", "year", "model", "engine", "transmission", "drivetrain", "exterior_color",
                   "msrp", "dealer", "location", "ordernum", "json", "all_rpos"]
    
    for i, line in enumerate(lines):
        if line.startswith("VIN "):
            info["vin"] = line.split("VIN ")[1].strip()
        if "2024 CT4 " in line or "2024 CT5 " in line:
            model_info = ' '.join(line.strip().split())
            model_info = model_info.replace("LUX HAUT DE GAMME", "PREMIUM LUXURY").replace("LUXE HAUT DE GAMME", "PREMIUM LUXURY")
            info["year"] = model_info[:4].strip()
            modeltrim = model_info[4:].strip().split()
            info["model"] = modeltrim[0]
            info["trim"] = ' '.join(modeltrim[1:])
        if "PRICE*" in line:
            info["msrp"] = lines[i + 1].strip()
        if "DELIVERED" in line:
            info["dealer"] = lines[i + 1].strip().replace("�", "-")
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
    
    # Reorder the fields
    info_ordered = {field: info.get(field, None) for field in field_order}
    
    return info_ordered

def writeCSV(pdf_info):
    # Define the field names based on the keys of pdf_info
    fieldnames = pdf_info.keys()
    
    # Open the CSV file in append mode with newline='' to avoid extra newline characters
    with open("2024_cadillac.csv", "a", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write the pdf_info to the CSV file
        writer.writerow(pdf_info)

# Main vin processing ---------------------------------------------------------------------------
def processVin(urlIdent, vinChanging, endVIN, yearDig):
    global foundVIN
    urlFirst = "https://cws.gm.com/vs-cws/vehshop/v2/vehicle/windowsticker?vin=1G6D"

    # Keep going until a specific stopping point
    while vinChanging <= endVIN:
        if vinChanging in skip_camaro or vinChanging in skip_cadillac:
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
                        contents = requests.get(newUrl, headers = {'User-Agent': 'caddy count finder version', 'Accept-Language': 'en-US'}, timeout=120)
                        contents = contents.text
                        time.sleep(1)

                        # Check if request returns errorMessage or actual content (meaning a window sticker was found)
                        try:
                            # If json content found = no window sticker
                            jsonCont = json.loads(contents)
                            print("\033[30m" + jsonCont["errorMessage"] + "\033[0m")
                        # If request returns not a json content = window sticker found
                        except json.decoder.JSONDecodeError:
                            # Write VIN to txt file
                            with open(f"caddy_{year}.txt", "a") as f:
                                f.write(str("\n" + updated_vin))
                            # Inform console
                            print("\033[33mMatch Found For VIN: [" + updated_vin + "].\033[0m")
                            foundVIN += 1
                            pdf_text = extractPDF(newUrl)
                            pdf_info = extractInfo(pdf_text)
                            writeCSV(pdf_info)
                            # Append only the last 6 digits of the VIN to the list and file
                            skip_cadillac.append(vinChanging)
                            with open("skip_cadillac.txt", "a") as file:
                                file.write("    " + str(vinChanging).zfill(6) + ",\n")

                        # Increment VIN by 1
                        vinChanging += 1
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
                    continue  # Continue with the next VIN
                else:
                    print("Unknown error occurred. Skipping this VIN.")
                    # Write VIN to ceVin.txt file
                    with open("ceVin.txt", "a") as f:
                        f.write(str("\n" + updated_vin + " - ERROR, RETRY THIS VIN"))
                    vinChanging += 1  # Move to the next VIN
                    continue  # Continue with the next VIN

            # When canceled in console, record last checked VIN to lastVin.txt
            except KeyboardInterrupt:
                #with open("lastVin.txt", "w") as f:
                #    f.write(str(vinChanging))
                    break

# Process request through all variations of trim/gears
for urlIdent in urlIdent_list:
#    for checkDig in checkDig_list:
    print("Testing configuration: " + urlIdent)
    processVin(urlIdent, vinChanging, endVIN, yearDig)
    print("")

endTime = time.time()
elapsedTime = endTime - startTime

minutes = int(elapsedTime // 60)
seconds = int(elapsedTime % 60)

t = time.localtime()
currentTime = time.strftime("%H:%M:%S", t)
print("Ended:", currentTime, " - Elapsed time: {} minutes, {} seconds\nTested {} VIN(s) - Found {} match(es)".format(minutes, seconds, totalVIN, foundVIN))
# https://www.camaro6.com/forums/showthread.php?t=426194 - VIN Breakdown
