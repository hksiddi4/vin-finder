import json
import requests
import time
import urllib3.exceptions
from variables.universal import *
from variables.corvette import *
from variables.ct import *
from variables.camaro import *
from variables.hummer_ev import *
from variables.silverado_ev import *
from variables.sierra_ev import *
from variables.escalade_iq import *

def extractInfo(text, updated_vin, model):
    config = model_configs.get(model)
    if not config:
        raise ValueError(f"Unsupported model: {model}")
    return parse_generic(text, updated_vin, config)

# Main vin processing ---------------------------------------------------------------------------
def processVin(session, urlIdent, vinChanging, endVIN, yearDig, startVIN, plant):
    global testedVIN, foundVIN
    mYear = int(year)

    if model in ("CAMARO", "CT4", "CT5"):
        if 2020 <= mYear <= 2024:
            files_to_read = skip_files_map["CAMARO_CT4_CT5"]
        else:
            files_to_read = skip_files_map["CT4-CT5"]
    elif model in ("HUMMER EV", "SILVERADO EV", "SIERRA EV", "ESCALADE IQ"):
        if model == "HUMMER EV" and 2022 <= mYear <= 2023:
            files_to_read = skip_files_map.get("HUMMER_EV")
        elif mYear == 2024:
            files_to_read = skip_files_map.get("HUMMER_SILVERADO_SIERRA_EV")
        elif mYear >= 2025:
            files_to_read = skip_files_map.get("HUMMER_SILVERADO_SIERRA_ESCALADEIQ_EV")
    else:
        files_to_read = skip_files_map.get(model, [])

    skipping = []
    for file_path in files_to_read:
        with open(file_path, 'r') as file:
            skipping.extend(int(line.strip()) for line in file if line.strip().isdigit())

    urlFirst = f"https://cws.gm.com/vs-cws/vehshop/v2/vehicle/windowsticker?vin={startVIN}"

    # Keep going until a specific stopping point
    while vinChanging <= endVIN:
        skip_count = 0
        # Count consecutive skips
        while vinChanging <= endVIN and vinChanging in skipping:
            skip_count += 1
            vinChanging += 1
        if skip_count > 0:
            print(f"\033[30mExisting sequence{'s' if skip_count > 1 else ''}, skipped {skip_count} VIN{'s' if skip_count > 1 else ''}.\033[0m")
            # After skipping block, continue with next iteration to process non-skipped VIN
            if vinChanging > endVIN:
                break
        try:
            # Build the URL (first half + identify trim/gear + check digit + model year + plant location + sequence number)
            matchedVIN = startVIN + urlIdent + "X" + yearDig + plant + str(vinChanging).zfill(6)
            updated_vin = calculate_check_digit(matchedVIN)
            newUrl = urlFirst + urlIdent + updated_vin[8:11] + str(vinChanging).zfill(6)

            max_retries = 3
            retries = 0

            while retries < max_retries:
                try:
                    # Get Request
                    contentsGet = session.get(newUrl, timeout=10)
                    contentsByte = contentsGet.content
                    contents = contentsGet.text
                    time.sleep(1)

                    # Retry if contents is empty
                    if contents == "":
                        print("\033[91mEmpty content received. Retrying in 3 seconds...\033[0m")
                        time.sleep(3)
                        retries += 1
                        continue

                    try:
                        # If JSON content found = no window sticker
                        jsonCont = json.loads(contents)
                        print("\033[30m" + jsonCont["errorMessage"] + "\033[0m")
                    # If request returns not a JSON content = window sticker found
                    except json.decoder.JSONDecodeError:
                        print("\033[33mMatch Found For VIN: [" + updated_vin + "].\033[0m")
                        if model in ("CT4", "CT5"):
                            fullPath = f"{path}/ct4-ct5_{year}.txt"
                        else:
                            fullPath = f"{path}/{model.lower()}_{year}.txt"
                        with open(fullPath, "a") as f:
                            f.write(f"{updated_vin}\n")
                        try:
                            pdf_text = extractPDF(contentsByte, updated_vin, path)
                            pdf_info = extractInfo(pdf_text, updated_vin, model)
                            
                            required_fields = ["trim", "engine", "transmission", "dealer"]
                            missing = [field for field in required_fields if not pdf_info.get(field)]

                            if missing:
                                print("\033[91mMissing fields.\033[0m")
                                with open(f"{path}/RETRY.txt", "a") as f:
                                    f.write(f"{updated_vin}\n")
                            else:
                                writeCSV(pdf_info, path, model)

                            # Append only the last 6 digits of the VIN to the list and file
                            skipping.append(int(updated_vin[-6:]))
                            if model in ("CT4", "CT5"):
                                fullPath = f"{path}/skip_ct4-ct5.txt"
                            else:
                                fullPath = f"{path}/skip_{model.lower()}.txt"
                            with open(fullPath, "a") as file:
                                file.write(f"{updated_vin[-6:].zfill(6)}\n")

                            break
                        except Exception as e:
                            if retries < max_retries - 1:
                                print("\033[91mMuPDF error. Retrying in 3 seconds...\033[0m")
                                retries += 1
                                time.sleep(3)
                                continue
                            else:
                                print(f"\033[91mMuPDF error: {e}. Skipping this VIN.\033[0m")
                                with open(f'{path}/RETRY.txt', "a") as f:
                                    f.write(f"{updated_vin}\n")
                                continue

                    # Increment VIN by 1
                    vinChanging += 1
                    testedVIN += 1
                    break

                except requests.exceptions.ReadTimeout:
                    # Retry request
                    print("\033[91mTimed out, retrying in 2 minutes...\033[0m")
                    retries += 1
                    time.sleep(120)
                except urllib3.exceptions.NameResolutionError:
                    print("\033[91mName resolution failed. Retrying in 2 minutes...\033[0m")
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
                if "NameResolutionError" in str(e):
                    print("\033[91mDNS resolution failed. Waiting 2 minutes before retrying...\033[0m")
                    time.sleep(120)
                else:
                    print(f"\033[91mError: {e}\033[0m")
                    print("Skipping this VIN.")
                with open(f'{path}/RETRY.txt', "a") as f:
                    f.write(f"{updated_vin}\n")
                vinChanging += 1
                continue
        except KeyboardInterrupt:
            break

def parse_generic(text, updated_vin, config):
    global foundVIN
    foundVIN += 1

    lines = text.split('\n')

    info = {
        "vin": updated_vin,
        "model": config["model_name"],
        "drivetrain": config.get("default_drivetrain"),
        "body": config.get("default_body"),
    }

    for i, line in enumerate(lines):
        if any(f"{year} {suffix}" in line for suffix in ["CT4 ", "CT5 ", "CT6 "]):
            model_info = ' '.join(line.strip().split())
            model_info = model_info.replace("LUX HAUT DE GAMME", "PREMIUM LUXURY").replace("LUXE HAUT DE GAMME", "PREMIUM LUXURY").replace("LUXE", "LUXURY").replace("SERIE V", "V-SERIES").replace("SERIE-V", "V-SERIES")
            modeltrim = model_info[4:].strip().split()
            info["model"] = modeltrim[0]
            info["trim"] = ' '.join(modeltrim[1:]).replace(" AWD", "").replace("3.6L ", "").replace("3,6L LUXURY A TI", "LUXURY")
        if "PRICE*" in line:
            info["msrp"] = lines[i + 1].replace("$", "").replace(",", "").replace(".00", "").strip()
        if "DELIVERED" in line:
            json_data = ' '.join(lines[i + 7:i + 11])
            all_json = json.loads(json_data)
            all_json["Options"] = [opt for opt in all_json["Options"] if opt]
            info.update({
                "dealer": lines[i + 1].strip().replace("\u2013", "-"),
                "location": lines[i + 3].strip(),
                "json": all_json,
                "all_rpos": all_json["Options"],
                "ordernum": all_json["order_number"],
                "year": all_json["model_year"],
            })
            mmc_code = all_json["mmc_code"] = all_json["mmc_code"].strip()
            all_json["sitedealer_code"] = all_json["sitedealer_code"].strip()

            for item in info["all_rpos"]:
                if item in config["body_dict"]:
                    if model in ("CT4", "CT5", "CT6"):
                        info["body"] = "SEDAN"
                    else:
                        info["body"] = config["body_dict"][item]
                if item in config["color_dict"]:
                    info["exterior_color"] = config["color_dict"][item]
                if item in engines_dict:
                    info["engine"] = engines_dict[item]
                if item in trans_dict:
                    info["transmission"] = trans_dict[item]
                if item in config["trim_dict"]:
                    info["trim"] = config["trim_dict"][item]
                if item == "HP1" or item == "F46":
                    info["drivetrain"] = "AWD"
            if info.get("model") == "CAMARO" and (info.get("engine") == "2.0L Turbo, 4-cylinder, SIDI, VVT" or (info.get("year") == "2019" and info.get("engine") == "3.6L V6, DI, VVT")):
                info["transmission"] = "A8"
            if "FH1" in info["all_rpos"]:
                info["trim"] = trim_dict_hummer_ev["FH1"]
            if info["model"] == "HUMMER EV":
                if info["body"] == "TRUCK":
                    info["model"] = "HUMMER EV PICKUP"
                elif info["body"] == "SUV":
                    info["model"] = "HUMMER EV SUV"
            if mmc_code in mmc:
                info["model"] = mmc[mmc_code]
                if mmc_code in ("1YG07", "1YG67", "1YS07", "1YS67"):
                    info["drivetrain"] = "AWD"

    # Reorder and check missing fields as before
    field_order = ["vin", "year", "model", "body", "trim", "engine", "transmission", "drivetrain",
                   "exterior_color", "msrp", "dealer", "location", "ordernum", "json", "all_rpos"]

    info_ordered = {field: info.get(field, None) for field in field_order}

    missing_fields = [field for field, value in info_ordered.items() if value is None]
    if missing_fields:
        with open(f'{path}/missing_info.txt', "a") as f:
            f.write(f"{updated_vin} - {','.join(missing_fields)}\n")

    return info_ordered

model_configs = {
    "ESCALADE IQ": {
        "model_name": "ESCALADE IQ",
        "default_drivetrain": "4WD",
        "default_body": "SUV",
        "body_dict": body_dict,
        "color_dict": colors_dict_escalade_iq,
        "trim_dict": trim_dict_escalade_iq,
    },
    "HUMMER EV": {
        "model_name": "HUMMER EV",
        "default_drivetrain": "4WD",
        "default_body": "TRUCK",
        "body_dict": body_dict,
        "color_dict": colors_dict_hummer_ev,
        "trim_dict": trim_dict_hummer_ev,
    },
    "SIERRA EV": {
        "model_name": "SIERRA EV",
        "default_drivetrain": "4WD",
        "default_body": "TRUCK",
        "body_dict": body_dict,
        "color_dict": colors_dict_sierra_ev,
        "trim_dict": trim_dict_sierra_ev,
    },
    "SILVERADO EV": {
        "model_name": "SILVERADO EV",
        "default_drivetrain": "4WD",
        "default_body": "TRUCK",
        "body_dict": body_dict,
        "color_dict": colors_dict_silverado_ev,
        "trim_dict": trim_dict_silverado_ev,
    },
    "CT4": {
        "model_name": "CT4",
        "default_drivetrain": "RWD",
        "default_body": "SEDAN",
        "body_dict": body_dict,
        "color_dict": colors_dict_ct,
        "trim_dict": trim_dict_ct,
    },
    "CT5": {
        "model_name": "CT5",
        "default_drivetrain": "RWD",
        "default_body": "SEDAN",
        "body_dict": body_dict,
        "color_dict": colors_dict_ct,
        "trim_dict": trim_dict_ct,
    },
    "CT6": {
        "model_name": "CT6",
        "default_drivetrain": "RWD",
        "default_body": "SEDAN",
        "body_dict": body_dict,
        "color_dict": colors_dict_ct,
        "trim_dict": trim_dict_ct,
    },
    "CAMARO": {
        "model_name": "CAMARO",
        "default_drivetrain": "RWD",
        "default_body": "COUPE",
        "body_dict": body_dict,
        "color_dict": colors_dict_camaro,
        "trim_dict": trim_dict_camaro,
    },
    "CORVETTE": {
        "model_name": "CORVETTE",
        "default_drivetrain": "RWD",
        "default_body": "COUPE",
        "body_dict": body_dict,
        "color_dict": colors_dict_corvette,
        "trim_dict": trim_dict_corvette,
    },
}

def get_six_digit_input(prompt):
    while True:
        value = input(prompt)
        if value.isdigit() and len(value) == 6:
            return int(value)
        print("\033[91mPlease enter a valid 6-digit number.\033[0m\n")

urlChosenList = None
while True: # urlChosenList
    vinChanging = get_six_digit_input('Enter last 6 numbers of the VIN to start at:\n')
    endVIN = get_six_digit_input('Enter last 6 numbers of the VIN to stop at:\n')
    
    model = input('Enter model to use:\n').upper()
    model_entries = model_data.get(model)
    if not model_entries:
        print("\033[91mModel not found in model_data.\033[0m")
        continue
    if not isinstance(model_entries, list):
            model_entries = [model_entries]

    start_digit = str(vinChanging)[0]
    second_digit = str(vinChanging)[1]

    if isinstance(model_entries[0].get("start_vin"), dict):
        selected_start_vin = model_entries[0]["start_vin"].get(start_digit)
        if not selected_start_vin:
            print("\033[91mInvalid sequence.\033[0m\n")
            continue
    else:
        selected_start_vin = model_entries[0]["start_vin"]
    if model == "CORVETTE":
        mmc = mmc_2019 if int(year) == 2019 else mmc_2020
        if int(year) == 2019:
            if start_digit in ("8", "7"):
                urlChosenList = globals()["urlIdent_2019_zr1_list"]
            elif start_digit == "6":
                urlChosenList = globals()["urlIdent_2019_z06_list"]
            elif start_digit == "1":
                urlChosenList = globals()["urlIdent_2019_list"]
            else:
                print("\033[91mInvalid sequence.\033[0m\n")
                continue
        elif int(year) >= 2026 and start_digit in ("7", "9"):
            urlChosenList = globals()["urlIdent_zr1x_list"]
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
        if int(year) >= 2022 and start_digit in ["2", "4", "5"]:
            if second_digit == "1":
                urlChosenList = globals()["urlIdent_blackwing_ct4_a10"]
            elif second_digit == "6":
                urlChosenList = globals()["urlIdent_blackwing_ct4_m6"]
        elif int(year) >= 2022 and start_digit in ["6", "8", "9"]:
            if second_digit == "1":
                urlChosenList = globals()["urlIdent_blackwing_ct5_a10"]
            elif second_digit == "6":
                urlChosenList = globals()["urlIdent_blackwing_ct5_m6"]
        elif start_digit == "1":
            if int(year) < 2025:
                urlChosenList = globals()["urlIdent_list_ct45_2020"]
            elif int(year) >= 2025:
                urlChosenList = globals()["urlIdent_list_ct45_2025"]
        else:
            print("\033[91mInvalid sequence.\033[0m\n")
            continue
    elif model == "CT6":
        if int(year) == 2019:
            urlChosenList = globals()["urlIdent_list_ct6_2019"]
        elif int(year) == 2020:
            urlChosenList = globals()["urlIdent_list_ct6_2020"]
        else:
            print("\033[91mInvalid sequence.\033[0m\n")
            continue
    elif model == "HUMMER EV":
        if int(year) == 2022:
            urlChosenList = globals()["urlIdent_2022_hummer_ev"]
        elif int(year) == 2023:
            urlChosenList = globals()["urlIdent_2023_hummer_ev"]
        elif int(year) in [2024, 2025]:
            urlChosenList = globals()["urlIdent_2024_hummer_ev"]
        elif int(year) == 2026:
            urlChosenList = globals()["urlIdent_2026_hummer_ev"]
        else:
            print("\033[91mInvalid sequence.\033[0m\n")
            continue
    elif model in ("SILVERADO EV", "SILVERADO EV WT"):
        if int(year) == 2024:
            if start_digit in ["3", "4"]:
                urlChosenList = globals()["urlIdent_silverado_ev"]
            elif start_digit in ["2"]:
                urlChosenList = globals()["urlIdent_silverado_evwt"]
        elif int(year) >= 2025:
            urlChosenList = globals()["urlIdent_silverado_ev_2025"]
        else:
            print("\033[91mInvalid sequence.\033[0m\n")
            continue
    elif model == "SIERRA EV":
        if int(year) == 2024:
            urlChosenList = globals()["urlIdent_sierra_ev"]
        elif int(year) == 2025:
            urlChosenList = globals()["urlIdent_sierra_ev_2025"]
        elif int(year) == 2026:
            urlChosenList = globals()["urlIdent_sierra_ev_2026"]
        else:
            print("\033[91mInvalid sequence.\033[0m\n")
            continue
    elif model == "ESCALADE IQ":
        urlChosenList = globals()["urlIdent_escalade_iq"]
    else:
        print("\033[91mPlease enter a valid model or check the year.\033[0m\n")
        continue
    break

path = f"{model}/{year}"
if model in ("CT4", "CT5"):
    path = f"CT4-CT5/{year}"

if not isinstance(model_entries, list):
    model_entries = [model_entries]

startList = len(model_entries)
urlList = len(urlChosenList)

totalVIN = (((int(endVIN) + 1) - int(vinChanging)) * int(urlList)) * int(startList)
totalIdent = 1
totalStart = 1
foundVIN = 0
testedVIN = 0

estTime = totalVIN * 1.3939
estTime = format_time(estTime)
print(f"\033[91mETA: {estTime}\033[0m")

startTime = time.time()

with requests.Session() as session:
    # 2. Set default headers on the session (removes them from the loop)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US'
    })

    # Process request through all variations of trim/gears
    for config in model_entries:
        plant = config["plant"]
        for urlIdent in urlChosenList:
            if model == "SILVERADO EV" and urlIdent == "02EL":
                startVIN = "1GC4"
            if model == "SIERRA EV" and urlIdent == "0MED":
                startVIN = "1GT1"
            else:
                startVIN = config.get("start_vin", selected_start_vin)
            print(f"Testing configuration ({totalIdent}/{urlList}): {urlIdent} | ({totalStart}/{startList}): {startVIN}")
            # 3. Pass the session object to processVin
            processVin(session, urlIdent, vinChanging, endVIN, yearDig, startVIN, plant)
            totalIdent += 1
            print("")
        totalStart += 1
        totalIdent = 1

endTime = time.time()
elapsedTime = endTime - startTime
time_str = format_time(elapsedTime)
currentTime = time.strftime("%H:%M:%S", time.localtime())

print(f"Ended: {currentTime}")
print(f"Estimated time: {estTime} - Elapsed time: {time_str}")
print(f"Tested {testedVIN}/{totalVIN} VIN{'s' if testedVIN > 1 else ''} - Found \033[93m{foundVIN}\033[0m match{'es' if foundVIN > 1 else ''}")
