import json
import requests
import time
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
def processVin(vin):
    global testedVIN
    urlFirst = f"https://cws.gm.com/vs-cws/vehshop/v2/vehicle/windowsticker?vin="
    try:
        newUrl = urlFirst + vin

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
                    # If json content found = no window sticker
                    jsonCont = json.loads(contents)
                    print("\033[30m" + jsonCont["errorMessage"] + "\033[0m")
                # If request returns not a json content = window sticker found
                except json.decoder.JSONDecodeError:
                    with open(f"{path}/{model.lower()}_{year}.txt", "a") as f:
                        f.write(f"{vin}\n")
                    print("\033[33mMatch Found For VIN: [" + vin + "].\033[0m")
                    try:
                        pdf_text = extractPDF(contentsByte, vin, path)
                    except Exception as e:
                        print("\033[91mMuPDF error. Retrying in 3 seconds...\033[0m")
                        time.sleep(3)
                        continue
                    pdf_info = extractInfo(pdf_text, vin, model)

                    # Append only the last 6 digits of the VIN to the list and file
                    with open(f"{path}/skip_{model.lower()}.txt", "a") as file:
                        file.write(f"{vin[-6:]}\n")
                    
                    writeCSV(pdf_info, path, model)
                break

            except requests.exceptions.ReadTimeout:
                print("\033[91mTimed out, retrying in 2 minutes...\033[0m")
                retries += 1
                time.sleep(120)
        testedVIN += 1

    except requests.exceptions.RequestException as e:
        if isinstance(e.__cause__, ConnectionResetError):
            print(f"\033[91mConnectionResetError: {e}. Continue in 10 seconds...\033[0m")
            with open(f'{path}/RETRY.txt', "a") as f:
                f.write(f"{vin}\n")
            time.sleep(10)
            return
        else:
            if "NameResolutionError" in str(e):
                print("\033[91mDNS resolution failed. Waiting 2 minutes before retrying...\033[0m")
                time.sleep(120)
            else:
                print(f"\033[91mError: {e}\033[0m")
                print("\033[30mSkipping this VIN.\033[0m")
            with open(f'{path}/RETRY.txt', "a") as f:
                f.write(f"{vin}\n")
            return
    except KeyboardInterrupt:
        return

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
                    info["body"] = config["body_dict"][item]
                if item in config["color_dict"]:
                    info["exterior_color"] = config["color_dict"][item]
                if item in engines_dict:
                    info["engine"] = engines_dict[item]
                if item in trans_dict:
                    info["transmission"] = trans_dict[item]
                if item in config["trim_dict"]:
                    info["trim"] = config["trim_dict"][item]
                if item == "HP1":
                    info["drivetrain"] = "AWD"
            if info.get("engine") == "2.0L Turbo, 4-cylinder, SIDI, VVT" or (info.get("year") == "2019" and info.get("engine") == "3.6L V6, DI, VVT"):
                info["transmission"] = "A8"
            if "FH1" in info["all_rpos"]:
                info["trim"] = trim_dict_hummer_ev["FH1"]
            if mmc_code in mmc:
                info["model"] = mmc[mmc_code]
                if mmc_code == "1YG07" or mmc_code == "1YG67":
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
    "CT": {
        "default_body": "SEDAN",
        "color_dict": colors_dict_ct,
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

model_map = {
    "CT4": "CT4-CT5", "CT5": "CT4-CT5",
    "CAMARO": "CAMARO",
    "HUMMER EV": "HUMMER EV",
    "SILVERADO EV": "SILVERADO EV",
    "SIERRA EV": "SIERRA EV",
    "ESCALADE IQ": "ESCALADE IQ",
}

while True:
    model = input('Enter model to use:\n').upper()
    if model == "CORVETTE":
        mmc = mmc_2019 if int(year) == 2019 else mmc_2020
        break
    elif model in model_map:
        model = model_map[model]
        break
    else:
        print("\033[91mPlease enter a valid model or check the year.\033[0m\n")

path = f"{model}/{year}"

with open(f"{path}/RETRY.txt", 'r') as file:
    lines = file.readlines()

totalVIN = len(lines)
foundVIN = 0
testedVIN = 0

estTime = totalVIN * 2
time_str = format_time(estTime)
print(f"\033[31mETA: {time_str}\033[0m")

startTime = time.time()

for vin in lines:
    vin = vin.strip()
    processVin(vin)
print("")

endTime = time.time()
elapsedTime = endTime - startTime
time_str = format_time(elapsedTime)
currentTime = time.strftime("%H:%M:%S", time.localtime())

print(f"Ended: {currentTime} - Elapsed time: {time_str}")
print(f"Tested {testedVIN}/{totalVIN} VIN(s) - Found \033[93m{foundVIN}\033[0m match(es)")
