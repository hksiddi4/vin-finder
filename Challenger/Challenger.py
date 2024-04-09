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
        print("Invalid year (2013-2023).")

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

def extractInfo(text, newUrl):
    lines = text.split('\n')
    info = {}
    
    # Define the order of fields ["VIN", "Year", "Model", "Trim", "engine", "transmission", "drivetrain",
                   #"exterior_color", "msrp", "dealer", "location", "ordernum", "json", "all_rpos"]
    field_order = ["VIN", "Year", "Model", "Trim", "Engine", "Trans.", "Drivetrain", "Exterior_Color",
                    "Interior_Color", "Interior", "MSRP", "Order #", "URL"]
    
    for i, line in enumerate(lines):
        if line.startswith("VIN: "):
            info["VIN"] = line.split("VIN: ")[1].strip().replace("–", "")
        info["Year"] = year
        if "CHALLENGER" in line:
            info["Model"] = "CHALLENGER"
            info["Trim"] = line.split("CHALLENGER")[1].strip()
            if "ALL-WHEEL Drive" in info["Trim"]:
                info["Drivetrain"] = "AWD"
            else:
                info["Drivetrain"] = "RWD"
        if "Engine: " in line:
            info["Engine"] = line.split("Engine: ")[1].strip().replace(" Engine", "").replace("\u00AE","")
        if "Transmission: " in line:
            info["Trans."] = line.split("Transmission: ")[1].strip().replace("\u00AE","").replace("\u2013","-")
        if "TOTAL PRICE: * " in line:
            info["MSRP"] = line.split("TOTAL PRICE: * ")[1].strip()
        if "VON: " in line:
            info["Order #"] = line.split("VON: ")[1].strip()
        if "Exterior Color: " in line:
            info["Exterior_Color"] = line.split("Exterior Color: ")[1].replace("Exterior Paint","").replace("\u2013","-").strip()
        if "Interior Color: " in line:
            info["Interior_Color"] = line.split("Interior Color: ")[1].replace("Interior Colors","").replace("\u2013","-").strip()
        if "Interior: " in line:
            info["Interior"] = line.split("Interior: ")[1].replace("\u00AE","").strip()
    
    info["URL"] = newUrl
    # Reorder the fields
    info_ordered = {field: info.get(field, None) for field in field_order}
    
    return info_ordered

def writeCSV(pdf_info):
    # Define the field names based on the keys of pdf_info
    fieldnames = pdf_info.keys()
    
    # Open the CSV file in append mode with newline='' to avoid extra newline characters
    with open("challenger.csv", "a", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write the pdf_info to the CSV file
        writer.writerow(pdf_info)

# Main vin processing ---------------------------------------------------------------------------
def processVin(urlIdent, vinChanging, endVIN, yearDig):
    global foundVIN
    urlFirst = "https://www.dodge.com/hostd/windowsticker/getWindowStickerPdf.do?vin=2C3CD"

    # Keep going until a specific stopping point
    while vinChanging <= endVIN:
        if vinChanging in skip_challenger:
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
                        contents = requests.get(newUrl, headers = {'User-Agent': 'challenger count finder version', 'Accept-Language': 'en-US'}, timeout=120)
                        contents = contents.text
                        time.sleep(1)                        
                        
                        try:
                            jsonCont = json.loads(contents)
#                            print("\033[30m" + jsonCont["errorMessage"] + "\033[0m")
                        except json.decoder.JSONDecodeError:
                            pdf_text = extractPDF(newUrl)
                            if pdf_text.strip() == "Sorry, a Window Sticker is unavailable for this VIN":
                                print("\033[30mNo Window Sticker Found For VIN: " + matchedVIN + "\033[0m")
                            else:
                                # Write VIN to txt file
                                with open(f"challenger_{year}.txt", "a") as f:
                                    f.write(str("\n" + updated_vin))
                                # Inform console
                                print("\033[33mMatch Found For VIN: " + updated_vin + "\033[0m")
                                pdf_info = extractInfo(pdf_text, newUrl)
                                writeCSV(pdf_info)
                                # Append only the last 6 digits of the VIN to the list and file
                                skip_challenger.append(vinChanging)
                                with open("skip_challenger.txt", "a") as file:
                                    file.write("    " + str(vinChanging).zfill(6) + ",\n")
                                foundVIN += 1

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
                    # Write VIN to RETRY.txt file
                    with open("RETRY.txt", "a") as f:
                        f.write(str("\n" + updated_vin))
                    vinChanging += 1  # Move to the next VIN
                    continue  # Continue with the next VIN

            # When canceled in console, record last checked VIN to lastVin.txt
            except KeyboardInterrupt:
                    break

# Process request through all variations of trim/gears
for urlIdent in urlIdent_list:
    print("Testing configuration: " + urlIdent)
    processVin(urlIdent, vinChanging, endVIN, yearDig)
    print("")

endTime = time.time()
elapsedTime = endTime - startTime

hours = int(elapsedTime // 3600)
remainder = elapsedTime % 3600
minutes = int(remainder // 60)
seconds = int(remainder  % 60)

t = time.localtime()
currentTime = time.strftime("%H:%M:%S", t)
print("Ended:", currentTime, " - Elapsed time: {} hour(s), {} minute(s), {} second(s)\nTested {} VIN(s) - Found {} match(es)".format(hours, minutes, seconds, totalVIN, foundVIN))
# https://www.camaro6.com/forums/showthread.php?t=426194 - VIN Breakdown
