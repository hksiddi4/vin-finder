import fitz
import csv
import re
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
                    nf.write(f"{vin} - Multiple Pages\n")
            page = doc.load_page(0)
            text = page.get_text()
        doc.close()
        return text
    except Exception as e:
        with open(f'{year}/RETRY.txt', "a") as f:
            f.write(str(updated_vin + "\n"))

def extract_opt_equipment(text):
    # Regular expression patterns for start and end markers
    if "Prix" in text:
        start_marker_pattern = r'Peut remplacer l\'équipement de série*'
        end_marker_pattern = r'PRIX TOTAL*'
        pattern = r'^\s*(.+?)\s+([\d\s]+)\s*\$\s*$'
    else:
        start_marker_pattern = r'May Replace Standard Equipment.*'
        end_marker_pattern = r'TOTAL PRICE: \*'
        pattern = r'^\s*(.+?)\s+\$([\d,]+)\s*$'

    # Find start and end indices using regex search
    start_match = re.search(start_marker_pattern, text, re.IGNORECASE)
    end_match = re.search(end_marker_pattern, text)

    if not start_match or not end_match:
        return {}

    # Extract the section of text containing optional equipment
    start_index = start_match.end()  # Use end() to get the end of the match
    end_index = end_match.start()

    options = text[start_index:end_index].strip()

    # Find all matches of the pattern in the optional_section
    matches = re.findall(pattern, options, re.MULTILINE)

    # Initialize an empty dictionary for equipment information
    equipment_info = {}

    # Iterate over the matches and populate equipment_info dictionary
    for match in matches:
        item = match[0].strip()  # Item title
        price = match[1].replace(',', '')  # Price, remove commas
        
        # Clean up item title: remove double quotes and replace special characters
        item = item.replace('"', '').replace('–', '-').strip()
        
        equipment_info[item] = price

    return json.dumps(equipment_info, separators=(',', ':'))

def extractInfo(text, updated_vin):
    global year
    
    # Write VIN to txt file
    with open(f"{year}/challenger_{year}.txt", "a") as f:
        f.write(f"{updated_vin}\n")
    # Append only the last 6 digits of the VIN to the list and file
    skip_challenger.append(int(updated_vin[-6:]))
    with open(f"{year}/skip_challenger.txt", "a") as file:
        file.write(f"{updated_vin[-6:]}\n")

    lines = text.split('\n')
    info = {}

    field_order = ["VIN", "Year", "Model", "Body", "Trim", "Engine", "Trans.", "Drivetrain",
                   "Exterior_Color", "Interior_Color", "Interior", "MSRP", "Order #", "Equipment"]

    line_counter = 0
    
    opt_equipment = extract_opt_equipment(text)
    info["Equipment"] = json.dumps(opt_equipment, indent=4)

    info["VIN"] = updated_vin
    info["Year"] = year
    info["Model"] = "CHALLENGER"
    info["Body"] = "COUPE"
    for i, line in enumerate(lines):
        line_counter += 1
        if "CHALLENGER" in line and line_counter <= 7:
            info["Trim"] = line.split("CHALLENGER ")[1].strip()
            if "ALL-WHEEL Drive" in info["Trim"]:
                info["Drivetrain"] = "AWD"
            else:
                info["Drivetrain"] = "RWD"
        if "Engine: " in line or "Moteur : " in line:
            key = "Engine"
            if "Engine: " in line:
                value = line.split("Engine: ")[1].strip().replace(" Engine", "").replace(" engine", "").replace("\u00AE","").replace("HO supercharged","Supercharged HO").replace("\u2013","-")
            elif "Moteur : " in line:
                value = line.split("Moteur : ")[1].strip().replace(" Moteur", "").replace("\u00AE","").replace("\u2013","-")
            value = value.replace("MOTEUR V8 HR SURALIMENTE DE 6,2 L", "6.2L V8 Supercharged HO")
            info[key] = value
        if "Transmission: " in line:
            info["Trans."] = line.split("Transmission: ")[1].strip().replace("\u00AE","").replace("\u2013","-").replace("TRANS AUTO 8 VIT TORQUEFLITE H PERF","TorqueFlite 8-Speed Automatic Transmission").replace("8-speed TorqueFlite high performance automatic","TorqueFlite 8-Speed Automatic Transmission")
        if "TOTAL PRICE: * " in line or "PRIX TOTAL : * " in line:
            key = "MSRP"
            if "TOTAL PRICE: * " in line:
                value = line.split("TOTAL PRICE: * ")[1].strip()
            elif "PRIX TOTAL : * " in line:
                value = line.split("PRIX TOTAL : * ")[1].strip()
                value = value.replace(" ", "").replace("$", "")
            info[key] = value
        if "VON: " in line or "NCV: " in line:
            key = "Order #"
            if "VON: " in line:
                value = line.split("VON: ")[1].strip()
            elif "NCV: " in line:
                value = line.split("NCV: ")[1].strip()
            info[key] = value
        if "Exterior Color: " in line or "Couleur extérieure : " in line:
            key = "Exterior_Color"
            if "Exterior Color: " in line:
                value = line.split("Exterior Color: ")[1].replace("Exterior Paint","").replace("\u2013","-").strip()
            elif "Couleur extérieure : " in line:
                value = line.split("Couleur extérieure : ")[1].strip()
            info[key] = value
        if "Interior Color: " in line or "Couleur intérieure: " in line:
            key = "Interior_Color"
            if "Interior Color: " in line:
                value = line.split("Interior Color: ")[1].replace("Interior Colors","").replace("Interior Color","").replace("\u2013","-").strip()
            elif "Couleur intérieure: " in line:
                value = line.split("Couleur intérieure: ")[1].strip()
            info[key] = value
        if "Interior: " in line or "Intérieur : " in line:
            key = "Interior"
            if "Interior: " in line:
                value = line.split("Interior: ")[1].replace("\u00AE","").replace("\u2013","-").strip()
            elif "Intérieur : " in line:
                value = line.split("Intérieur : ")[1].strip()
            info[key] = value
    
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
    with open(f"{year}/{year}_challenger.csv", "a", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write the pdf_info to the CSV file
        writer.writerow(pdf_info)

# Main vin processing ---------------------------------------------------------------------------
def processVin(urlIdent, vinChanging, endVIN, yearDig):
    global totalVIN
    global foundVIN
    urlFirst = "https://www.dodge.com/hostd/windowsticker/getWindowStickerPdf.do?vin=2C3CD"

    # Keep going until a specific stopping point
    while vinChanging <= endVIN:
        if vinChanging in skip_challenger or vinChanging in skip_charger:
            print("\033[30mExisting sequence, skipping\033[0m")
            vinChanging += 1
            continue
        else:
            try:
                # Build the URL (first half + identify trim/gear + check digit + year digit + 0 + incrementing VIN)
                matchedVIN = "2C3CD" + urlIdent + "X" + yearDig + "H" + str(vinChanging)
                updated_vin = calculate_check_digit(matchedVIN)
                newUrl = urlFirst + urlIdent + updated_vin[8:11] + str(vinChanging).zfill(6)

                max_retries = 3
                retries = 0

                while retries < max_retries:
                    try:
                        # Get Request
                        contentsGet = requests.get(newUrl, headers = {'User-Agent': 'challenger count finder version', 'Accept-Language': 'en-US'}, timeout=120)
                        contents = contentsGet.text
                        time.sleep(1)
                        
                        try:
                            jsonCont = json.loads(contents)
                        except json.decoder.JSONDecodeError:
                            pdf_text = extractPDF(contentsGet, updated_vin)
                            if pdf_text is None:
                                print("Received None text. Skipping this VIN.")
                                # Write VIN to RETRY.txt file
                                with open(f'{year}/RETRY.txt', "a") as f:
                                    f.write(f"{updated_vin}\n")
                            elif "CHALLENGER" not in pdf_text.strip():
                                print("\033[30mNo Window Sticker Found For VIN: [" + matchedVIN + "].\033[0m")
                            else:
                                # Inform console
                                print("\033[33mMatch Found For VIN: [" + updated_vin + "].\033[0m")
                                pdf_info = extractInfo(pdf_text, updated_vin)
                                writeCSV(pdf_info)
                                foundVIN += 1

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
                elif e == "('Connection aborted.', ConnectionResetError(10054, 'An existing connection was forcibly closed by the remote host', None, 10054, None))":
                    # Write VIN to RETRY.txt file
                    with open(f'{year}/RETRY.txt', "a") as f:
                        f.write(f"{updated_vin}\n")
                    vinChanging += 1  # Move to the next VIN
                    print("Connection closed by host, waiting...")
                    time.sleep(3)
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

totalVIN = 0
foundVIN = 0
i = 1

startTime = time.time()

# Process request through all variations of trim/gears
for urlIdent in chosenList:
    urlList = len(chosenList)
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
