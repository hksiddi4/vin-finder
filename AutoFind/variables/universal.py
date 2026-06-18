import fitz
import csv
import os
import requests
import json
import time

# Step 1: Alpha-numeric values for Check Digit
alpha_numeric_conversion = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'P': 7, 'R': 9, 'S': 2,
    'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9
}

weight_factors = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]

def calculate_check_digit(vin):
    total = 0
    for i, char in enumerate(vin):
        if char.isdigit():
            total += int(char) * weight_factors[i]
        elif char in alpha_numeric_conversion:
            total += alpha_numeric_conversion[char] * weight_factors[i]
        else:
            raise ValueError(f"Invalid character in VIN: {char}")
    
    remainder = total % 11
    check_digit = str(remainder) if remainder < 10 else 'X'
    return vin[:8] + check_digit + vin[9:]

def format_time(seconds):
    days, remainder = divmod(int(seconds), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    if seconds >= 30: minutes += 1
    
    time_parts = []
    if days > 0: time_parts.append(f"{days}d")
    if hours > 0: time_parts.append(f"{hours}h")
    if minutes > 0: time_parts.append(f"{minutes}m")
    return ", ".join(time_parts) if time_parts else "< 1m"

def extractPDF(contentsByte):
    try:
        doc = fitz.open(stream=contentsByte, filetype="pdf")
        text = doc.load_page(0).get_text() if len(doc) > 0 else ""
        doc.close()
        return text
    except Exception:
        return None

def writeCSV(pdf_info, path, model, year):
    if not pdf_info: return
    if model in ("CT4", "CT5"):
        model = "CT4-CT5"
    elif model == "ESCALADE ESV":
        model = "ESCALADE"
    fullPath = os.path.join(path, f"{year}_{model.lower()}.csv")
    file_exists = os.path.isfile(fullPath)
    with open(fullPath, "a", newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=pdf_info.keys())
        if not file_exists: writer.writeheader()
        writer.writerow(pdf_info)

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1506100938799317002/EgAR1--3XYHTrnHZwIiAaNmQndRqHhf4Rkwpz8yRxdErVwRJEjmOPJIPNGTNhEekc2Op"

def send_discord_message(content):
    if not DISCORD_WEBHOOK_URL:
        return
    try:
        payload = {"content": content}
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"Failed to send Discord notification: {e}")

# Global Config
years = {'2027': 'V', '2026': 'T', '2025': 'S', '2024': 'R', '2023': 'P'}

model_data = {
    "CORVETTE": {"start_vin": "1G1Y", "plant": "5"},
    "CT4": {"start_vin": "1G6D", "plant": "0"},
    "CT5": {"start_vin": "1G6D", "plant": "0"},
}

engines_dict = {
    "L3B": "2.7L TURBO",
    "L87": "6.2L V8",
    "LF4": "3.6L V6 TWIN TURBO SIDI, DOHC, VVT",
    "LGW": "3.0L V6 TWIN TURBO DI, DOHC, VVT",
    "LGX": "3.6L V6, DI, VVT",
    "LGY": "3.0L TWIN TURBO V6, SIDI",
    "LSY": "2.0L TURBO, 4-CYL, SIDI",
    "LT1": "6.2L (376 ci) V8 DI",
    "LT2": "6.2L V8 DI",
    "LT4": "6.2L SUPERCHARGED V8",
    "LT5": "6.2L SUPERCHARGED V8 TPI",
    "LS6": "6.7L V8 DI",
    "LT6": "5.5L V8 DI",
    "LT7": "5.5L (335 ci) Twin-Turbo V8",
    "LTA": "4.2L, V8, TWIN TURBO",
    "LTG": "2.0L Turbo, 4-cylinder, SIDI, VVT",
    "EN0": "None",
    "ETI": "Ultium - 20 module pack",
    "EWX": "Ultium - 14 module pack",
    "ETN": "Ultium - 24 module pack",
    "ETJ": "Ultium - 20 module pack",
}

trans_dict = {
    "M1K": "DCT8",
    "M1L": "DCT8",
    "M1M": "DCT8",
    "M1N": "DCT8",
    "MLP": "DCT8",
    "M5N": "A8",
    "M5U": "A8",
    "MEK": "M7",
    "MEL": "M7",
    "MEP": "M7",
    "MG9": "M6",
    "MHA": "A8",
    "MHO": "A10",
    "MHS": "A10",
    "MHU": "A10",
    "MHW": "A10",
    "MHX": "A10",
    "MQC": "A10",
    "MJK": "M6",
    "MLH": "DCT8",
    "MN6": "M6",
    "MQ2": "A10",
    "MQA": "A10",
    "MX0": "A10",
    "MF1": "None",
}

body_dict = {
    "CM8": "CONVERTIBLE",
    "CM9": "CONVERTIBLE",
    "CFC": "CONVERTIBLE",
}

_scrape_stats = {"testedVIN": 0, "foundVIN": 0}

def get_scrape_stats():
    return {"tested": _scrape_stats["testedVIN"], "found": _scrape_stats["foundVIN"]}

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
            info.get("vin"), info.get("year"), info.get("model"), info.get("body"), 
            info.get("trim"), info.get("engine"), info.get("transmission"), 
            info.get("drivetrain"), info.get("exterior_color"), info.get("msrp"), 
            info.get("dealer"), info.get("location"), info.get("ordernum"), info.get("json")
        )
        cursor.execute(query, values)
        cursor.close()
    except Exception as e:
        print(f"MySQL Database Error: {e}")

def parse_generic(text, updated_vin, model_type, path):
    if not text:
        raise ValueError("PDF extraction yielded no text.")
    _scrape_stats["foundVIN"] += 1
    lines = text.split('\n')
    
    from variables.corvette import colors_dict_corvette, trim_dict_corvette, mmc_2020
    from variables.ct import colors_dict_ct, trim_dict_ct
    
    is_corvette = (model_type == "CORVETTE")
    config = {
        "body_dict": body_dict,
        "color_dict": colors_dict_corvette if is_corvette else colors_dict_ct,
        "trim_dict": trim_dict_corvette if is_corvette else trim_dict_ct
    }

    info = {
        "vin": updated_vin,
        "model": "CORVETTE" if is_corvette else "CT4-CT5",
        "drivetrain": "RWD",
        "body": "COUPE" if is_corvette else "SEDAN",
    }

    for i, line in enumerate(lines):
        if not is_corvette and any(f"{year} {suffix}" in line for suffix in ["CT4 ", "CT5 "]):
            model_info = ' '.join(line.strip().split())
            model_info = model_info.replace("LUX HAUT DE GAMME", "PREMIUM LUXURY").replace("LUXE", "LUXURY").replace("SERIE V", "V-SERIES").replace("SERIE-V", "V-SERIES")
            modeltrim = model_info[4:].strip().split()
            info["model"] = modeltrim[0]
            info["trim"] = ' '.join(modeltrim[1:]).replace(" AWD", "").replace("3.6L ", "").replace("3,6L LUXURY A TI", "LUXURY")
            
        if "PRICE*" in line:
            info["msrp"] = lines[i + 1].replace("$", "").replace(",", "").replace(".00", "").strip()
            
        if "DELIVERED" in line:
            json_data = ' '.join(lines[i + 7:])
            all_json = json.loads(json_data)
            
            # Dictionary-safe Options parsing
            all_json["Options"] = [opt for opt in all_json.get("Options", []) if opt]
            
            info.update({
                "dealer": lines[i + 1].strip().replace("\u2013", "-"),
                "location": lines[i + 3].strip(),
                "json": all_json,
                "all_rpos": all_json.get("Options", []),
                "ordernum": all_json.get("order_number"),
                "year": all_json.get("model_year"),
            })

            mmc_code = all_json["mmc_code"] = all_json.get("mmc_code", "").strip()
            all_json["sitedealer_code"] = all_json.get("sitedealer_code", "").strip()

            for item in info["all_rpos"]:
                if item in config["body_dict"]: info["body"] = config["body_dict"][item]
                if item in config["color_dict"]: info["exterior_color"] = config["color_dict"][item]
                if item in engines_dict: info["engine"] = engines_dict[item]
                if item in trans_dict: info["transmission"] = trans_dict[item]
                if item in config["trim_dict"]: info["trim"] = config["trim_dict"][item]
                if item in ["HP1", "F46", "C3F"] or (is_corvette and mmc_code in ("1YG07", "1YG67", "1YS07", "1YS67")): 
                    info["drivetrain"] = "AWD"
                    
            if is_corvette and mmc_code in mmc_2020:
                info["model"] = mmc_2020[mmc_code]

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

def processVin(session, db_conn, urlIdent, vinChanging, endVIN, yearDig, startVIN, plant, totalIdent, urlList, model, path, year):
    sticker_folder = f"/mnt/NVMe/Apps/GM-Vehicles/window-stickers/{model}_{year}"
    
    # Use a set for O(1) instantaneous lookups
    skipping = set()
    
    # Localized file mapping
    skip_file_path = f'{model.upper()}/{year}/skip_{model.lower()}.txt'
    if model == "CT4-CT5":
        skip_file_path = f'CT4-CT5/{year}/skip_ct4-ct5.txt'
        
    if os.path.exists(skip_file_path):
        with open(skip_file_path, 'r') as file:
            skipping.update(int(line.strip()) for line in file if line.strip().isdigit())

    urlFirst = f"https://cws.gm.com/vs-cws/vehshop/v2/vehicle/windowsticker?vin={startVIN}"

    while vinChanging <= endVIN:
        if vinChanging < 1: vinChanging = 1
        skip_count = 0
        
        # This while-loop check is now virtually instant
        while vinChanging <= endVIN and vinChanging in skipping:
            skip_count += 1
            vinChanging += 1

        if skip_count > 0 and vinChanging > endVIN: break

        try:
            matchedVIN = startVIN + urlIdent + "X" + yearDig + plant + str(vinChanging).zfill(6)
            updated_vin = calculate_check_digit(matchedVIN)
            pdf_filename = os.path.join(sticker_folder, f"{updated_vin}.pdf")
            newUrl = urlFirst + urlIdent + updated_vin[8:11] + str(vinChanging).zfill(6)

            retries, max_retries, delays = 0, 3, [3, 10, 30]

            while retries < max_retries:
                try:
                    contentsGet = session.get(newUrl, timeout=10)
                    contentsByte = contentsGet.content
                    contents = contentsGet.text
                    time.sleep(1)

                    if not contents:
                        time.sleep(delays[retries])
                        retries += 1
                        continue

                    try:
                        json.loads(contents)
                    except json.decoder.JSONDecodeError:
                        content_type = contentsGet.headers.get('Content-Type', '')
                        if 'application/pdf' not in content_type:
                            print(f"Skipped {updated_vin}: Server returned {content_type} instead of a PDF.")
                            continue

                        os.makedirs(sticker_folder, exist_ok=True)
                        try:
                            with open(pdf_filename, "wb") as f:
                                f.write(contentsByte)
                        except IOError as e:
                            print(f"Failed to save PDF for {updated_vin}: {e}")

                        try:
                            pdf_text = extractPDF(contentsByte)
                            pdf_info = parse_generic(pdf_text, updated_vin, model, path)

                            print(f"{updated_vin} - ({totalIdent}/{urlList}) - FOUND")
                            
                            fullPath = os.path.join(path, f"{model.lower()}_{year}.txt")
                            with open(fullPath, "a") as f:
                                f.write(f"{updated_vin}\n")

                            writeCSV(pdf_info, path, model, year)
                            
                            if db_conn and db_conn.is_connected():
                                insert_to_mysql(db_conn, pdf_info)

                            skip_path = os.path.join(path, f"skip_{model.lower()}.txt")
                            with open(skip_path, "a") as file:
                                file.write(f"{str(vinChanging).zfill(6)}\n")
                                
                            # Update the set
                            skipping.add(vinChanging)

                        except Exception as e:
                            print(f"Extraction Error for {updated_vin}: {e}")

                        if os.path.exists(pdf_filename):
                            os.remove(pdf_filename)

                    vinChanging += 1
                    _scrape_stats["testedVIN"] += 1
                    break

                except requests.exceptions.ReadTimeout:
                    print("Timeout. Waiting...")
                    time.sleep(30)
                    retries += 1

        except KeyboardInterrupt:
            return "stop"
    return "continue"
