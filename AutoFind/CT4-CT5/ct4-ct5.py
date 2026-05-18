import json
import requests
import time
import sys
import os
import urllib3.exceptions
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from variables.universal import *
from variables.ct import *

model_configs = {
    "CT4-CT5": {
        "body_dict": body_dict,
        "color_dict": colors_dict_ct,
        "trim_dict": trim_dict_ct
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
    sticker_folder = f"/mnt/NVMe/Apps/GM-Vehicles/window-stickers/{model}_{year}"

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
            if vinChanging > endVIN: break

        try:
            matchedVIN = startVIN + urlIdent + "X" + yearDig + plant + str(vinChanging).zfill(6)
            updated_vin = calculate_check_digit(matchedVIN)
            pdf_filename = os.path.join(sticker_folder, f"{updated_vin}.pdf")
            newUrl = urlFirst + urlIdent + updated_vin[8:11] + str(vinChanging).zfill(6)

            max_retries, retries, delays = 3, 0, [3, 10, 30]

            while retries < max_retries:
                try:
                    contentsGet = session.get(newUrl, timeout=10)
                    contentsByte = contentsGet.content
                    contents = contentsGet.text
                    time.sleep(1)

                    if not contents:
                        print(f"Empty content. Retrying in {delays[retries]}...")
                        time.sleep(delays[retries])
                        retries += 1
                        continue

                    try:
                        json.loads(contents)
                    except json.decoder.JSONDecodeError:
                        print(f"{updated_vin} ({totalIdent}/{urlList}) - FOUND")

                        fullPath = os.path.join(path, f"{model.lower()}_{year}.txt")
                        with open(fullPath, "a") as f:
                            f.write(f"{updated_vin}\n")

                        os.makedirs(sticker_folder, exist_ok=True)
                        try:
                            with open(pdf_filename, "wb") as f:
                                f.write(contentsByte)
                        except IOError as e:
                            print(f"Failed to save PDF for {updated_vin}: {e}")

                        try:
                            pdf_text = extractPDF(contentsByte)
                            pdf_info = extractInfo(pdf_text, updated_vin, model)
                            writeCSV(pdf_info, path, model, year)

                            if db_conn and db_conn.is_connected():
                                insert_to_mysql(db_conn, pdf_info)

                            skip_path = os.path.join(path, f"skip_{model.lower()}.txt")
                            with open(skip_path, "a") as file:
                                file.write(f"{str(vinChanging).zfill(6)}\n")
                            skipping.append(vinChanging)

                        except Exception as e:
                            print(f"Extraction Error: {e}")

                    vinChanging += 1
                    testedVIN += 1
                    break

                except requests.exceptions.ReadTimeout:
                    print("Timeout. Waiting...")
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
        "model": "CT4-CT5",
        "drivetrain": "RWD",
        "body": "SEDAN",
    }

    for i, line in enumerate(lines):
        if any(f"{year} {suffix}" in line for suffix in ["CT4 ", "CT5 "]):
            model_info = ' '.join(line.strip().split())
            model_info = model_info.replace("LUX HAUT DE GAMME", "PREMIUM LUXURY").replace("LUXE HAUT DE GAMME", "PREMIUM LUXURY").replace("LUXE", "LUXURY").replace("SERIE V", "V-SERIES").replace("SERIE-V", "V-SERIES")
            modeltrim = model_info[4:].strip().split()
            info["model"] = modeltrim[0]
            info["trim"] = ' '.join(modeltrim[1:]).replace(" AWD", "").replace("3.6L ", "").replace("3,6L LUXURY A TI", "LUXURY")
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

            all_json["mmc_code"] = all_json["mmc_code"].strip()
            all_json["sitedealer_code"] = all_json["sitedealer_code"].strip()

            for item in info["all_rpos"]:
                if item in config["body_dict"]: info["body"] = config["body_dict"][item]
                if item in config["color_dict"]: info["exterior_color"] = config["color_dict"][item]
                if item in engines_dict: info["engine"] = engines_dict[item]
                if item in trans_dict: info["transmission"] = trans_dict[item]
                if item in config["trim_dict"]: info["trim"] = config["trim_dict"][item]
                if item in ["HP1", "F46", "C3F"]: 
                    info["drivetrain"] = "AWD"

    if "json" in info and isinstance(info["json"], dict):
        info["json"] = json.dumps(info["json"])

    field_order = ["vin", "year", "model", "body", "trim", "engine", "transmission", "drivetrain",
                   "exterior_color", "msrp", "dealer", "location", "ordernum", "json"]
    info_ordered = {field: info.get(field, None) for field in field_order}

    missing_fields = [field for field, value in info_ordered.items() if value is None]
    if missing_fields:
        with open(os.path.join(path, 'missing_info.txt'), "a") as f:
            f.write(f"{updated_vin} - {','.join(missing_fields)}\n")

    return info_ordered

def insert_to_mysql(db_conn, info):
    try:
        cursor = db_conn.cursor()
        query = """
            INSERT IGNORE INTO staging_allGM (
                vin, modelYear, model, body, trim, vehicleEngine, 
                transmission, drivetrain, exterior_color, msrp, 
                dealer, location, ordernum, allJson
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            info.get("vin"),
            info.get("year"),
            info.get("model"),
            info.get("body"),
            info.get("trim"),
            info.get("engine"),
            info.get("transmission"),
            info.get("drivetrain"),
            info.get("exterior_color"),
            info.get("msrp"),
            info.get("dealer"),
            info.get("location"),
            info.get("ordernum"),
            info.get("json")
        )
        cursor.execute(query, values)
        db_conn.commit()
        cursor.close()
    except Exception as e:
        print(f"MySQL Database Error: {e}")

if __name__ == "__main__":
    import mysql.connector
    model = "CT4-CT5"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, f"{year}")
    skip_file_path = os.path.join(path, 'skip_ct4-ct5.txt')
    found_sequences = []

    if os.path.exists(skip_file_path):
        with open(skip_file_path, 'r') as f:
            found_sequences = [int(line.strip()) for line in f if line.strip().isdigit()]

    current_time = datetime.now().strftime("%B %d, %Y | ") + datetime.now().strftime("%I:%M %p").lstrip('0')
    print(f"\n{current_time}")

    # Explicit custom search range configurations mapping (100k digit prefix -> range)
    sequence_bands = [
        (100000, 130000, 100),  # CT4-CT5
        (210000, 210050, 50),   # CT4-V Blackwing A10 OAR
        (260000, 260050, 50),   # CT4-V Blackwing M6 OAR
        (410000, 410500, 50),   # CT4-V Blackwing A10
        (460000, 460500, 50),   # CT4-V Blackwing M6
        (610000, 610100, 50),   # CT5-V Blackwing A10 OAR
        (660000, 660050, 50),   # CT5-V Blackwing M6 OAR
        (810000, 810800, 100),  # CT5-V Blackwing A10
        (860000, 861200, 100)   # CT5-V Blackwing M6
    ]

    # Initialize each band tracking dictionary with its default fallback sequence
    band_maxes = {band[0]: band[0] + 1 for band in sequence_bands}

    # Match existing historical sequences to their respective sub-bands
    for seq in found_sequences:
        for base, expected_max, _ in sequence_bands:
            # Allow a small 5,000 unit buffer past expected max for late-production anomalies
            if base < seq <= (expected_max + 5000):
                if seq > band_maxes[base]:
                    band_maxes[base] = seq
                break  # Matched; move to the next sequence

    # Construct execution targets dynamically mapped to the correct sub-band
    targets = []
    for base, expected_max, current_range in sequence_bands:
        last_known_seq = band_maxes[base]
        
        # Enforce hard structural boundaries so scans never bleed into adjacent sub-tracks
        vinChanging = max(base + 1, last_known_seq - current_range)
        endVIN = min(expected_max + current_range, last_known_seq + current_range)
        
        targets.append((base, vinChanging, endVIN, current_range))

    db_config = {
        'host': '192.168.1.126',
        'user': 'hussain',
        'password': 'Hussain92',
        'database': 'vehicles',
        'port': 3306
    }

    startTime = time.time()
    status = "continue"

    with requests.Session() as session, mysql.connector.connect(**db_config) as db_conn:
        session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

        # Loop completely isolated across each individual structural range target
        for base, vinChanging, endVIN, current_range in targets:
            if status == "stop":
                break

            print(f"--- Processing Sub-Band {base // 1000}k Series ({vinChanging:06d} to {endVIN:06d}) ---")

            start_prefix = str(vinChanging).zfill(6)[:2]

            if start_prefix in ("21", "41", "51"):
                urlChosenList = urlIdent_blackwing_ct4_a10
            elif start_prefix in ("26", "46", "56"):
                urlChosenList = urlIdent_blackwing_ct4_m6
            elif start_prefix in ("61", "81", "91"):
                urlChosenList = urlIdent_blackwing_ct5_a10
            elif start_prefix in ("66", "86", "96"):
                urlChosenList = urlIdent_blackwing_ct5_m6
            else: urlChosenList = urlIdent_list_ct45_2025

            urlList = len(urlChosenList)
            totalIdent = 1

            for urlIdent in urlChosenList:
                print(f"Testing Prefix: {urlIdent} ({totalIdent}/{urlList})")

                status = processVin(session, db_conn, urlIdent, vinChanging, endVIN, yearDig, "1G1Y", "5", totalIdent, urlList, skipping)
                if status == "stop":
                    print("Execution halted via KeyboardInterrupt.")
                    break
                totalIdent += 1

        # Finalize processing and execute database update sync procedure
        if db_conn and db_conn.is_connected():
            print("\n[Database] Scrape loop finished. Triggering production data sync...")
            try:
                proc_cursor = db_conn.cursor()
                proc_cursor.callproc('execute_gm_data_sync')
                db_conn.commit()
                proc_cursor.close()
                print("[Database] Success: Relational tables updated successfully.")
            except Exception as e:
                print(f"[Database] Error running production sync procedure: {e}")

    elapsedTime = time.time() - startTime
    print(f"\nCompleted in: {format_time(elapsedTime)}")
    print(f"Found: {foundVIN} | Tested: {testedVIN}")
    print("----------------------------------------------------------------------------\n")
