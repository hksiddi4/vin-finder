import fitz
import csv
import re
import json
import requests
import time
import http.client, urllib
import sys
from variables import *

def extractPDF(contentsGet, vin):
    try:
        with open(f"{year}/temp.pdf", "wb") as f:
            f.write(contentsGet.content)
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
        with open(f"{year}/RETRY.txt", "a") as f:
            f.write(f"{vin}\n")
        return None

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

def extractInfo(text, vin):
    global foundVIN

    # Write VIN to txt file
    with open(f"{year}/challenger_{year}.txt", "a") as f:
        f.write(f"{vin}\n")
    # Append only the last 6 digits of the VIN to the list and file
    skip_challenger.append(int(vin[-6:]))
    with open(f"{year}/skip_challenger.txt", "a") as file:
        file.write(f"{vin[-6:]}\n")

    lines = text.split('\n')
    info = {}
    

    field_order = ["VIN", "Year", "Model", "Body", "Trim", "Engine", "Trans.", "Drivetrain",
                   "Exterior_Color", "Interior_Color", "Interior", "MSRP", "Order #", "Equipment"]

    line_counter = 0

    opt_equipment = extract_opt_equipment(text)
    info["Equipment"] = json.dumps(opt_equipment, indent=4)

    info["VIN"] = vin
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
                value = line.split("Engine: ")[1].strip().replace(" Engine", "").replace(" engine", "").replace("\u00AE","").replace("\u2013","-").replace("HO supercharged","Supercharged HO")
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
                value = line.split("Interior: ")[1].replace("\u00AE","").strip()
            elif "Intérieur : " in line:
                value = line.split("Intérieur : ")[1].strip()
            info[key] = value
    
    # Reorder the fields
    info_ordered = {field: info.get(field, None) for field in field_order}
    
    return info_ordered

def writeCSV(pdf_info):
    if pdf_info is None:
        return
    # Define the field names based on the keys of pdf_info
    fieldnames = pdf_info.keys()
    
    # Open the CSV file in append mode with newline='' to avoid extra newline characters
    with open(f"{year}/{year}_challenger.csv", "a", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write the pdf_info to the CSV file
        writer.writerow(pdf_info)

def processVin(vin):
    global foundVIN
    lastSix = int(vin[-6:])
    urlFirst = "https://www.dodge.com/hostd/windowsticker/getWindowStickerPdf.do?vin="

    if lastSix in skip_challenger or lastSix in skip_charger:
        print("\033[30mExisting sequence, skipping\033[0m")
        return
    else:
        try:
            newUrl = urlFirst + vin

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
                        pdf_text = extractPDF(contentsGet, vin)
                        if pdf_text is None:
                            print("Received None text. Skipping this VIN.")
                            # Write VIN to RETRY.txt file
                            with open(f'{year}/RETRY.txt', "a") as f:
                                f.write(f"{vin}\n")
                        elif "CHALLENGER" not in pdf_text.strip():
                            print("\033[30mNo Window Sticker Found For VIN: [" + vin + "].\033[0m")
                        else:
                            # Inform console
                            print("\033[33mMatch Found For VIN: [" + vin + "].\033[0m")
                            pdf_info = extractInfo(pdf_text, vin)
                            writeCSV(pdf_info)
                            foundVIN += 1
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
                        f.write(f"{vin}\n")
                    vinChanging += 1  # Move to the next VIN
                    print("ConnectionResetError occurred. Retrying...")
                    return
                elif e == "('Connection aborted.', ConnectionResetError(10054, 'An existing connection was forcibly closed by the remote host', None, 10054, None))":
                    # Write VIN to RETRY.txt file
                    with open(f'{year}/RETRY.txt', "a") as f:
                        f.write(f"{vin}\n")
                    vinChanging += 1  # Move to the next VIN
                    print("Connection closed by host, waiting...")
                    time.sleep(3)
                else:
                    print("Skipping this VIN.")
                    # Write VIN to RETRY.txt file
                    with open(f'{year}/RETRY.txt', "a") as f:
                        f.write(f"{vin}\n")
                    vinChanging += 1  # Move to the next VIN
                    return

        except KeyboardInterrupt:
            sys.exit(0)

# Open the file RETRY.txt and read lines
with open(f"{year}/RETRY.txt", 'r') as file:
    lines = file.readlines()

foundVIN = 0

i = 0

startTime = time.time()

# Process each line
for vin in lines:
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

t = time.localtime()
currentTime = time.strftime("%H:%M:%S", t)
print("Ended:", currentTime, " - Elapsed time: {} hour(s), {} minute(s), {} second(s)".format(hours, minutes, seconds))
print("Tested {} VIN(s) - Found {} match(es)".format(i, foundVIN))
