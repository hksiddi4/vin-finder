import json
import requests
import time
from variables.universal import *
from variables.corvette import *
from variables.ct import *
from variables.camaro import *

def extractInfo(text, updated_vin, model):
    parser_registry = {
        "CORVETTE": parse_corvette,
        "CT4-CT5": parse_ct,
        "CAMARO": parse_camaro,
    }
    parser = parser_registry.get(model)

    if parser:
        return parser(text, updated_vin)
    else:
        raise ValueError(f"Unsupported model: {model}")

# Main vin processing ---------------------------------------------------------------------------
def processVin(urlIdent, vinChanging, endVIN, yearDig):
    global testedVIN, foundVIN
    startVIN = model_data.get(model, {}).get("start_vin")
    plant = model_data.get(model, {}).get("plant")

    if model in ("CAMARO", "CT4", "CT5"):
        if 2020 <= int(year) <= 2024:
            files_to_read = skip_files_map["CAMARO_CT4_CT5"]
        else:
            files_to_read = skip_files_map["CT4-CT5"]
    else:
        files_to_read = skip_files_map.get(model, [])

    skipping = []
    for file_path in files_to_read:
        with open(file_path, 'r') as file:
            skipping.extend(int(line.strip()) for line in file if line.strip().isdigit())

    urlFirst = f"https://cws.gm.com/vs-cws/vehshop/v2/vehicle/windowsticker?vin={startVIN}"

    # Keep going until a specific stopping point
    while vinChanging <= endVIN:
        if vinChanging in skipping:
            print("\033[30mExisting sequence, skipping\033[0m")
            vinChanging += 1
            continue
        try:
            # Build the URL (first half + identify trim/gear + check digit + model year + plant location + sequence number)
            matchedVIN = startVIN + urlIdent + "X" + yearDig + plant + str(vinChanging)
            updated_vin = calculate_check_digit(matchedVIN)
            newUrl = urlFirst + urlIdent + updated_vin[8:11] + str(vinChanging).zfill(6)

            max_retries = 3
            retries = 0

            while retries < max_retries:
                try:
                    # Get Request
                    contentsGet = requests.get(newUrl, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36', 'Accept-Language': 'en-US'}, timeout=120)
                    contentsByte = contentsGet.content
                    contents = contentsGet.text
                    time.sleep(1)

                    # Retry if contents is empty
                    if contents == "":
                        print("\033[91mEmpty content received. Retrying in 3 seconds...\033[0m")
                        time.sleep(3)
                        continue

                    try:
                        # If JSON content found = no window sticker
                        jsonCont = json.loads(contents)
                        print("\033[30m" + jsonCont["errorMessage"] + "\033[0m")
                    # If request returns not a JSON content = window sticker found
                    except json.decoder.JSONDecodeError:
                        with open(f"{path}/{model.lower()}_{year}.txt", "a") as f:
                            f.write(f"{updated_vin}\n")
                        print("\033[33mMatch Found For VIN: [" + updated_vin + "].\033[0m")
                        try:
                            pdf_text = extractPDF(contentsByte, updated_vin, path)
                        except Exception as e:
                            print("\033[91mMuPDF error. Retrying in 3 seconds...\033[0m")
                            time.sleep(3)
                            continue
                        pdf_info = extractInfo(pdf_text, updated_vin, model)
                        
                        # Append only the last 6 digits of the VIN to the list and file
                        skipping.append(int(updated_vin[-6:]))
                        with open(f"{path}/skip_{model.lower()}.txt", "a") as file:
                            file.write(f"{updated_vin[-6:].zfill(6)}\n")
                        
                        required_fields = ["trim", "engine", "transmission", "dealer"]
                        missing = [field for field in required_fields if not pdf_info.get(field)]

                        if missing:
                            print("\033[91mMissing fields.\033[0m")
                            with open(f"{path}/RETRY.txt", "a") as f:
                                f.write(f"{updated_vin}\n")
                        else:
                            writeCSV(pdf_info, path, model)

                    # Increment VIN by 1
                    vinChanging += 1
                    testedVIN += 1
                    break

                except requests.exceptions.ReadTimeout:
                    # Retry request
                    print("\033[91mTimed out, retrying in 2 minutes...\033[0m")
                    retries += 1
                    time.sleep(120)

        except requests.exceptions.RequestException as e:
            if isinstance(e.__cause__, ConnectionResetError):
                print(f"\033[91mConnectionResetError: {e}.\033[0m")
                # Write VIN to RETRY.txt file
                with open(f'{path}/RETRY.txt', "a") as f:
                    f.write(f"{updated_vin}\n")
                vinChanging += 1
                time.sleep(10)
                continue
            else:
                print(f"\033[91mError: {e}\033[0m")
                print("Skipping this VIN.")
                with open(f'{path}/RETRY.txt', "a") as f:
                    f.write(f"{updated_vin}\n")
                vinChanging += 1
                continue
        except KeyboardInterrupt:
            break

def parse_corvette(text, updated_vin):
    global foundVIN

    foundVIN += 1

    lines = text.split('\n')

    field_order = ["vin", "year", "model", "body", "trim", "engine", "transmission", "drivetrain",
                   "exterior_color", "msrp", "dealer", "location", "ordernum", "json", "all_rpos"]
    
    info = {
        "vin": updated_vin,
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
                if item in colors_dict_corvette:
                    info["exterior_color"] = colors_dict_corvette[item]
                if item in engines_dict:
                    info["engine"] = engines_dict[item]
                if item in trans_dict:
                    info["transmission"] = trans_dict[item]
                if item in trim_dict_corvette:
                    info["trim"] = trim_dict_corvette[item]
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
        with open(f'{path}/missing_info.txt', "a") as f:
            f.write(f"{updated_vin} - {','.join(missing_fields)}\n")
    
    return info_ordered

def parse_camaro(text, updated_vin):
    global foundVIN

    foundVIN += 1

    lines = text.split('\n')
    
    field_order = ["vin", "year", "model", "body", "trim", "engine", "transmission", "drivetrain",
                   "exterior_color", "msrp", "dealer", "location", "ordernum", "json", "all_rpos"]
    
    info = {
        "vin": updated_vin,
        "model": "CAMARO",
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
            all_json["mmc_code"] = all_json["mmc_code"].replace(' ','')
            all_json["sitedealer_code"] = all_json["sitedealer_code"].replace(' ','')

            for item in info["all_rpos"]:
                if item in body_dict:
                    info["body"] = body_dict[item]
                if item in colors_dict_camaro:
                    info["exterior_color"] = colors_dict_camaro[item]
                if item in engines_dict:
                    info["engine"] = engines_dict[item]
                if item in trans_dict:
                    info["transmission"] = trans_dict[item]
                if item in trim_dict_camaro:
                    info["trim"] = trim_dict_camaro[item]
            if info.get("engine") == "2.0L Turbo, 4-cylinder, SIDI, VVT" or (info.get("year") == "2019" and info.get("engine") == "3.6L V6, DI, VVT"):
                info["transmission"] = "A8"
            
    
    # Reorder the fields
    info_ordered = {field: info.get(field, None) for field in field_order}

    # Check for missing fields
    missing_fields = [field for field, value in info_ordered.items() if value is None]
    if missing_fields:
        with open(f'{path}/missing_info.txt', "a") as f:
            f.write(f"{updated_vin} - {','.join(missing_fields)}\n")
    
    return info_ordered

def parse_ct(text, updated_vin):
    global foundVIN
    
    foundVIN += 1

    lines = text.split('\n')
    
    field_order = ["vin", "year", "model", "body", "trim", "engine", "transmission", "drivetrain",
                   "exterior_color", "msrp", "dealer", "location", "ordernum", "json", "all_rpos"]
    
    info = {
        "vin": updated_vin,
        "body": "SEDAN"
    }
    
    for i, line in enumerate(lines):
        if any(f"{year} {suffix}" in line for suffix in ["CT4 ", "CT5 ", "CT6 "]):
            model_info = ' '.join(line.strip().split())
            model_info = model_info.replace("LUX HAUT DE GAMME", "PREMIUM LUXURY").replace("LUXE HAUT DE GAMME", "PREMIUM LUXURY").replace("LUXE", "LUXURY").replace("SERIE V", "V-SERIES").replace("SERIE-V", "V-SERIES")
            modeltrim = model_info[4:].strip().split()
            info["model"] = modeltrim[0]
            info["trim"] = ' '.join(modeltrim[1:]).replace(" AWD", "").replace("3.6L ", "").replace("3,6L LUXURY A TI", "LUXURY")
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
                if item in colors_dict_ct:
                    info["exterior_color"] = colors_dict_ct[item]
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
        with open(f'{path}/missing_info.txt', "a") as f:
            f.write(f"{updated_vin} - {','.join(missing_fields)}\n")
    
    return info_ordered

urlChosenList = None
while True: # urlChosenList
    while True:
        vinChanging_input = input('Enter last 6 numbers of the VIN to start at:\n')
        if vinChanging_input.isdigit() and len(vinChanging_input) == 6:
            vinChanging = int(vinChanging_input)
            break
        else:
            print("\033[91mPlease enter a valid 6-digit number.\033[0m\n")
    while True:
        endVIN_input = input('Enter last 6 numbers of the VIN to stop at:\n')
        if endVIN_input.isdigit() and len(endVIN_input) == 6:
            endVIN = int(endVIN_input)
            break
        else:
            print("\033[91mPlease enter a valid 6-digit number.\033[0m\n")
    
    model = input('Enter model to use:\n').upper()
    if model == "CORVETTE":
        mmc = mmc_2019 if int(year) == 2019 else mmc_2020
        start_digit = vinChanging_input[0]
        if int(year) == 2019:
            if start_digit == "8":
                urlChosenList = globals()["urlIdent_2019_zr1_list"]
            elif start_digit == "6":
                urlChosenList = globals()["urlIdent_2019_z06_list"]
            elif start_digit == "1":
                urlChosenList = globals()["urlIdent_2019_list"]
            else:
                print("\033[91mInvalid sequence.\033[0m\n")
                continue
        elif int(year) >= 2025 and start_digit == "8":
            urlChosenList = globals()["urlIdent_zr1_list"]
        elif int(year) >= 2024 and start_digit == "5":
            urlChosenList = globals()["urlIdent_eray_list"]
        elif int(year) >= 2023 and start_digit == "6":
            urlChosenList = globals()["urlIdent_z06_list"]
        elif start_digit == "1":
            urlChosenList = urlIdent_list
        else:
            print("\033[91mInvalid sequence.\033[0m\n")
            continue
    elif model == "CAMARO" and 2019 <= int(year) <= 2024:
        urlChosenList = globals()[f"urlIdent_list_{year}"]
    elif model in ("CT4", "CT5"):
        if int(year) >= 2022:
            blackwing = input('Run as Blackwing? (Y/N):\n').upper()
            if blackwing == "Y":
                urlChosenList = globals()["urlIdent_blackwing_list_2024"]
        elif start_digit == "1":
            urlChosenList = urlIdent_list_ct45
        model = "CT4-CT5"
    elif model == "CT6":
        urlChosenList = urlIdent_list_ct6
    else:
        print("\033[91mPlease enter a valid model or check the year.\033[0m\n")
        continue
    break

path = f"{model}/{year}"

urlList = len(urlChosenList)

totalVIN = ((int(endVIN_input) + 1) - int(vinChanging_input)) * int(urlList)
totalIdent = 1
foundVIN = 0
testedVIN = 0

estTime = totalVIN * 2
estTime = format_time(estTime)
print(f"\033[91mETA: {estTime}\033[0m")

startTime = time.time()

# Process request through all variations of trim/gears
for urlIdent in urlChosenList:
    print(f"Testing configuration ({str(totalIdent)}/{str(urlList)}): {urlIdent} -------------------------------")
    processVin(urlIdent, vinChanging, endVIN, yearDig)
    print("")
    totalIdent += 1

endTime = time.time()
elapsedTime = endTime - startTime
time_str = format_time(elapsedTime)
currentTime = time.strftime("%H:%M:%S", time.localtime())

print(f"Ended: {currentTime}")
print(f"Estimated time: {estTime} - Elapsed time: {time_str}")
print(f"Tested {testedVIN}/{totalVIN} VIN(s) - Found Found \033[93m{foundVIN}\033[0m match(es)")
