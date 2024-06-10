import fitz
import csv
import json
import requests
import time
from variables import *

startTime = time.time()

# Read VINs from file
with open('RETRY.txt', 'r') as file:
    vin_list = [line.strip() for line in file]

while True:
    year = input('Enter year to test:\n')
    if year in years:
        yearDig = years[year]
        break
    else:
        print("Invalid year.")

totalVIN = len(vin_list)
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
    
    remainder = total % 11
    check_digit = str(remainder) if remainder < 10 else 'X'
    updated_vin = matchedVIN[:8] + check_digit + matchedVIN[9:]
    return updated_vin

def extractPDF(contentsGet, updated_vin):
    try:
        with open("temp.pdf", "wb") as f:
            f.write(contentsGet.content)
        doc = fitz.open("temp.pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        with open("RETRY.txt", "a") as f:
            f.write(str("\n" + updated_vin))

def extractInfo(text, updated_vin):
    if text is None:
        print("Received None text. Skipping this VIN.")
        with open("RETRY.txt", "a") as f:
            f.write(str("\n" + updated_vin))
        return None
    lines = text.split('\n')
    info = {}
    field_order = ["vin", "year", "model", "trim", "engine", "transmission", "drivetrain",
                   "exterior_color", "msrp", "dealer", "location", "ordernum", "json", "all_rpos"]
    
    for i, line in enumerate(lines):
        if line.startswith("VIN "):
            info["vin"] = line.split("VIN ")[1].strip()
        if "2024 CT4 " in line or "2024 CT5 " in line:
            model_info = ' '.join(line.strip().split())
            model_info = model_info.replace("LUX HAUT DE GAMME", "PREMIUM LUXURY").replace("LUXE HAUT DE GAMME", "PREMIUM LUXURY").replace("LUXE", "LUXURY").replace("SERIE V", "V-SERIES")
            info["year"] = model_info[:4].strip()
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
    
    info_ordered = {field: info.get(field, None) for field in field_order}
    
    return info_ordered

def writeCSV(pdf_info):
    fieldnames = pdf_info.keys()
    with open("2024_cadillac.csv", "a", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(pdf_info)

# Main vin processing ---------------------------------------------------------------------------
def processVin(urlIdent, vin_list, yearDig):
    global foundVIN
    urlFirst = "https://cws.gm.com/vs-cws/vehshop/v2/vehicle/windowsticker?vin=1G6D"

    for vinChanging in vin_list:
        vinChanging = int(vinChanging)
        if vinChanging in skip_camaro:
            print("\033[30mExisting sequence, skipping\033[0m")
            continue
        else:
            try:
                matchedVIN = "1G6D" + urlIdent + "X" + yearDig + "0" + str(vinChanging).zfill(6)
                updated_vin = calculate_check_digit(matchedVIN)
                newUrl = urlFirst + urlIdent + updated_vin[8:11] + str(vinChanging).zfill(6)

                max_retries = 3
                retries = 0

                while retries < max_retries:
                    try:
                        contentsGet = requests.get(newUrl, headers = {'User-Agent': 'caddy count finder version', 'Accept-Language': 'en-US'}, timeout=120)
                        contents = contentsGet.text
                        time.sleep(1)

                        try:
                            jsonCont = json.loads(contents)
                            print("\033[30m" + jsonCont["errorMessage"] + "\033[0m")
                        except json.decoder.JSONDecodeError:
                            with open(f"caddy_{year}.txt", "a") as f:
                                f.write(str("\n" + updated_vin))
                            print("\033[33mMatch Found For VIN: [" + updated_vin + "].\033[0m")
                            foundVIN += 1
                            pdf_text = extractPDF(contentsGet, updated_vin)
                            pdf_info = extractInfo(pdf_text, updated_vin)
                            writeCSV(pdf_info)

                        break

                    except requests.exceptions.ReadTimeout:
                        print("Timed out, retrying...")
                        retries += 1
                        time.sleep(120)

            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
                if isinstance(e, requests.exceptions.ConnectionError) and isinstance(e.__cause__, ConnectionResetError):
                    print("ConnectionResetError occurred. Retrying...")
                    continue
                else:
                    print("Unknown error occurred. Skipping this VIN.")
                    with open("RETRY.txt", "a") as f:
                        f.write(str("\n" + updated_vin))
                    continue

            except KeyboardInterrupt:
                break

i = 1

for urlIdent in urlIdent_list:
    urlList = len(urlIdent_list)
    print("Testing configuration (" + str(i) + "/" + str(urlList) + "): " + urlIdent)
    processVin(urlIdent, vin_list, yearDig)
    print("")
    i += 1

endTime = time.time()
elapsedTime = endTime - startTime

hours = int(elapsedTime // 3600)
remainder = elapsedTime % 3600
minutes = int(remainder // 60)
seconds = int(remainder  % 60)

t = time.localtime()
currentTime = time.strftime("%H:%M:%S", t)
print("Ended:", currentTime, " - Elapsed time: {} hour(s), {} minute(s), {} second(s)\nTested {} VIN(s) - Found {} match(es)".format(hours, minutes, seconds, totalVIN, foundVIN))
