import json
import requests
import time
import sys
import os
import urllib3.exceptions

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from variables.universal import *
from variables.corvette import *

model_configs = {
    "CORVETTE": {
        "body_dict": body_dict,
        "color_dict": colors_dict_corvette,
        "trim_dict": trim_dict_corvette
    }
}

# Runtime tracking metrics
testedVIN = 0
foundVIN = 0

def extractInfo(text, updated_vin, model):
    config = model_configs.get(model)
    if not config:
        raise ValueError(f"Unsupported model: {model}")
    return parse_generic(text, updated_vin, config)

def processVin(session, urlIdent, vinChanging, endVIN, yearDig, startVIN, plant, totalIdent, urlList):
    global testedVIN, foundVIN
    sticker_folder = os.path.join(path, "Window Stickers")
    
    files_to_read = skip_files_map.get(model, [])
    skipping = []
    for file_path in files_to_read:
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                skipping.extend(int(line.strip()) for line in file if line.strip().isdigit())

    urlFirst = f"https://cws.gm.com/vs-cws/vehshop/v2/vehicle/windowsticker?vin={startVIN}"

    while vinChanging <= endVIN:
        if vinChanging < 1:
            vinChanging = 1

        skip_count = 0
        while vinChanging <= endVIN and vinChanging in skipping:
            skip_count += 1
            vinChanging += 1
        
        if skip_count > 0:
            print(f"\033[30mSkipped {skip_count} already found VINs.\033[0m")
            if vinChanging > endVIN: break

        try:
            matchedVIN = startVIN + urlIdent + "X" + yearDig + plant + str(vinChanging).zfill(6)
            updated_vin = calculate_check_digit(matchedVIN)
            pdf_filename = os.path.join(sticker_folder, f"{updated_vin}.pdf")
            newUrl = urlFirst + urlIdent + updated_vin[8:11] + str(vinChanging).zfill(6)

            max_retries, retries = 3, 0

            while retries < max_retries:
                try:
                    contentsGet = session.get(newUrl, timeout=10)
                    contentsByte = contentsGet.content
                    contents = contentsGet.text
                    time.sleep(1)

                    if not contents:
                        print("\033[91mEmpty content. Retrying...\033[0m")
                        time.sleep(3)
                        retries += 1
                        continue

                    try:
                        json.loads(contents)
                        print(f"\033[30m{updated_vin}\033[0m ({totalIdent}/{urlList})")
                    except json.decoder.JSONDecodeError:
                        print(f"\033[33m{updated_vin}\033[0m - ({totalIdent}/{urlList})")
                        
                        fullPath = os.path.join(path, f"{model.lower()}_{year}.txt")
                        with open(fullPath, "a") as f:
                            f.write(f"{updated_vin}\n")

                        os.makedirs(sticker_folder, exist_ok=True)
                        with open(pdf_filename, "wb") as f:
                            f.write(contentsByte)
                        
                        try:
                            pdf_text = extractPDF(contentsByte) # Clean in-memory parsing
                            pdf_info = extractInfo(pdf_text, updated_vin, model)
                            writeCSV(pdf_info, path, model, year)

                            skip_path = os.path.join(path, f"skip_{model.lower()}.txt")
                            with open(skip_path, "a") as file:
                                file.write(f"{str(vinChanging).zfill(6)}\n")
                            skipping.append(vinChanging)

                        except Exception as e:
                            print(f"\033[91mExtraction Error: {e}\033[0m")

                    vinChanging += 1
                    testedVIN += 1
                    break

                except requests.exceptions.ReadTimeout:
                    print("\033[91mTimeout. Waiting...\033[0m")
                    time.sleep(30)
                    retries += 1

        except KeyboardInterrupt:
            return "stop"
            
    return "continue"

def parse_generic(text, updated_vin, config):
    global foundVIN
    foundVIN += 1
    lines = text.split('\n')

    info = {
        "vin": updated_vin,
        "model": "CORVETTE",
        "drivetrain": "RWD",
        "body": "COUPE",
    }

    for i, line in enumerate(lines):
        if "PRICE*" in line:
            info["msrp"] = lines[i + 1].replace("$", "").replace(",", "").replace(".00", "").strip()
        if "DELIVERED" in line:
            json_data = ' '.join(lines[i + 7:])
            all_json = json.loads(json_data)
            all_json["Options"] = [opt for opt in all_json["Options"] if opt]
            info.update({
                "dealer": lines[i + 1].strip().replace("\u2013", "-"),
                "location": lines[i + 3].strip(),
                "json": all_json,
                "all_rpos": all_json.get("Options"),
                "ordernum": all_json.get("order_number"),
                "year": all_json.get("model_year"),
            })
            
            mmc_code = all_json["mmc_code"] = all_json["mmc_code"].strip()
            all_json["sitedealer_code"] = all_json["sitedealer_code"].strip()

            for item in info["all_rpos"]:
                if item in config["body_dict"]: info["body"] = config["body_dict"][item]
                if item in config["color_dict"]: info["exterior_color"] = config["color_dict"][item]
                if item in engines_dict: info["engine"] = engines_dict[item]
                if item in trans_dict: info["transmission"] = trans_dict[item]
                if item in config["trim_dict"]: info["trim"] = config["trim_dict"][item]
                if item in ["HP1", "F46", "C3F"] or mmc_code in ("1YG07", "1YG67", "1YS07", "1YS67"): 
                    info["drivetrain"] = "AWD"
            if mmc_code in mmc_2020: 
                info["model"] = mmc_2020[mmc_code]

    field_order = ["vin", "year", "model", "body", "trim", "engine", "transmission", "drivetrain",
                   "exterior_color", "msrp", "dealer", "location", "ordernum", "json"]
    info_ordered = {field: info.get(field, None) for field in field_order}

    missing_fields = [field for field, value in info_ordered.items() if value is None]
    if missing_fields:
        with open(os.path.join(path, 'missing_info.txt'), "a") as f:
            f.write(f"{updated_vin} - {','.join(missing_fields)}\n")

    return info_ordered


if __name__ == "__main__":
    model = "CORVETTE"
    path = f"{year}"
    skip_file_path = os.path.join(path, 'skip_corvette.txt')
    found_sequences = []

    if os.path.exists(skip_file_path):
        with open(skip_file_path, 'r') as f:
            found_sequences = [int(line.strip()) for line in f if line.strip().isdigit()]

    if found_sequences:
        last_known_seq = max(found_sequences)
        print(f"\033[94mLast known production sequence: {last_known_seq:06d}\033[0m")
    else:
        print("\033[91mNo sequences found in skip file. Using default 150000.\033[0m")
        last_known_seq = 150000

    searchRange = 5
    vinChanging = max(1, last_known_seq - searchRange)
    endVIN = min(999999, last_known_seq + searchRange)

    print(f"Automated Search Range: \033[93m{vinChanging:06d}\033[0m to \033[93m{endVIN:06d}\033[0m")

    start_digit = str(vinChanging).zfill(6)[0]
    int_year = int(year)

    if int_year >= 2026 and start_digit in ("7", "9"): urlChosenList = urlIdent_zr1x_list
    elif int_year >= 2025 and start_digit in ("4", "8"): urlChosenList = urlIdent_zr1_list
    elif 2024 <= int_year <= 2026 and start_digit in ("2", "5"): urlChosenList = urlIdent_eray_list
    elif int_year >= 2023 and start_digit in ("3", "6"): urlChosenList = urlIdent_z06_list
    else:
        urlChosenList = urlIdent_list
        if start_digit not in ("0", "1"):
            print("\033[91mWarning: Sequence digit doesn't match trim list. Defaulting to base list.\033[0m")

    urlList = len(urlChosenList)
    totalIdent = 1
    startTime = time.time()

    with requests.Session() as session:
        session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

        for urlIdent in urlChosenList:
            print(f"Testing: {urlIdent} ({totalIdent}/{urlList})")
            status = processVin(session, urlIdent, vinChanging, endVIN, yearDig, "1G1Y", "5", totalIdent, urlList)
            if status == "stop": 
                break
            totalIdent += 1

    elapsedTime = time.time() - startTime
    print(f"\nCompleted in: {format_time(elapsedTime)}")
    print(f"Found: {foundVIN} | Tested: {testedVIN}")
