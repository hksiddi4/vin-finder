import argparse
import time
import os
from datetime import datetime
import mysql.connector
import requests
import traceback
import sys

from variables.universal import *
from variables.corvette import *
from variables.ct import *

def main():
    parser = argparse.ArgumentParser(description="AutoFind Scraper")
    parser.add_argument("--model", type=str, required=True, choices=["CORVETTE", "CT4-CT5"], help="Model to scrape")
    parser.add_argument("--year", type=str, required=True, help="Model year to scrape")
    args = parser.parse_args()
    
    model = args.model
    year = args.year

    # Validate year exists in our config
    if year not in years:
        print(f"[ERROR] Year {year} is not configured in universal.years dictionary.")
        sys.exit(1)
        
    yearDig = years[year]

    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, model, f"{year}")
    os.makedirs(path, exist_ok=True)
    
    skip_file_path = os.path.join(path, f'skip_{model.lower()}.txt')
    found_sequences = []
    if os.path.exists(skip_file_path):
        with open(skip_file_path, 'r') as f:
            found_sequences = [int(line.strip()) for line in f if line.strip().isdigit()]

    current_time = datetime.now().strftime("%B %d, %Y | ") + datetime.now().strftime("%I:%M %p").lstrip('0')
    print(f"\n{current_time}")
    send_discord_message(f"**Starting {year} {model} Scrape**\n_{current_time}_")

    # --- Setup Model Targets ---
    targets = []
    if model == "CORVETTE":
        range_config = {9: 100, 8: 100, 6: 200, 5: 100, 3:100, 1: 500}
        int_year = int(year)
        active_digits = [0, 1] # SR
        if int_year >= 2023: active_digits.extend([3, 6]) # Z06
        if 2024 <= int_year <= 2026: active_digits.extend([2, 5]) # E-Ray
        if int_year >= 2025: active_digits.extend([4, 8]) # ZR1
        if int_year >= 2026: active_digits.extend([7, 9]) # ZR1X
        if int_year >= 2027: active_digits.extend([2, 3, 5]) # GS & GSX
        
        series_maxes = {}
        for seq in found_sequences:
            s_key = seq // 100000
            if s_key not in series_maxes or seq > series_maxes[s_key]:
                series_maxes[s_key] = seq

        for digit in sorted(list(set(active_digits))):
            last_seq = series_maxes.get(digit, (digit * 100000) + 1)
            rng = range_config.get(digit, 50)
            vinChanging = max((digit * 100000) + 1, last_seq - rng)
            endVIN = min(((digit + 1) * 100000) - 1, last_seq + rng)
            targets.append((digit * 100000, vinChanging, endVIN, rng))
            
    elif model == "CT4-CT5":
        sequence_bands = [
            (100000, 130000, 150), (210000, 210050, 50), (260000, 260050, 50),
            (410000, 410500, 50), (460000, 460500, 50), (610000, 610100, 50),
            (660000, 660050, 50), (810000, 810800, 100), (860000, 861200, 100)
        ]
        band_maxes = {band[0]: band[0] + 1 for band in sequence_bands}
        for seq in found_sequences:
            for base, expected_max, _ in sequence_bands:
                if base < seq <= (expected_max + 5000):
                    if seq > band_maxes[base]: band_maxes[base] = seq
                    break

        for base, expected_max, rng in sequence_bands:
            last_seq = band_maxes[base]
            vinChanging = max(base + 1, last_seq - rng)
            endVIN = min(expected_max + rng, last_seq + rng)
            targets.append((base, vinChanging, endVIN, rng))

    db_config = {'host': '192.168.1.126', 'user': 'hussain', 'password': 'Hussain92', 'database': 'vehicles', 'port': 3306}
    startTime = time.time()
    status = "continue"

    with requests.Session() as session, mysql.connector.connect(**db_config) as db_conn:
        session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

        try:
            for base, vinChanging, endVIN, current_range in targets:
                if status == "stop": break
                print(f"--- Processing Sub-Band {base // 1000}k Series ({vinChanging:06d} to {endVIN:06d}) | Range: {current_range} ---")
                
                # Setup specific URL Identifiers
                start_prefix = str(vinChanging).zfill(6)[:2]
                start_digit = start_prefix[0]
                int_year = int(year)
                
                if model == "CORVETTE":
                    if int_year >= 2026 and start_digit in ("7", "9"): urlChosenList = urlIdent_zr1x_list                        
                    elif int_year >= 2025 and start_digit in ("4", "8"): urlChosenList = urlIdent_zr1_list
                    elif 2024 <= int_year <= 2026 and start_digit in ("2", "5"): urlChosenList = urlIdent_eray_list
                    elif int_year >= 2027 and start_digit == "2": urlChosenList = urlIdent_gs_list + urlIdent_gsx_list
                    elif int_year >= 2027 and start_digit == "3": urlChosenList = urlIdent_gs_list
                    elif int_year >= 2027 and start_digit == "5": urlChosenList = urlIdent_gsx_list
                    elif int_year >= 2023 and start_digit in ("3", "6"): urlChosenList = urlIdent_z06_list
                    elif int_year >= 2027: urlChosenList = urlIdent_list_2027
                    else: urlChosenList = urlIdent_list
                else: # CT4-CT5
                    if start_prefix in ("21", "41", "51"): urlChosenList = urlIdent_blackwing_ct4_a10
                    elif start_prefix in ("26", "46", "56"): urlChosenList = urlIdent_blackwing_ct4_m6
                    elif start_prefix in ("61", "81", "91"): urlChosenList = urlIdent_blackwing_ct5_a10
                    elif start_prefix in ("66", "86", "96"): urlChosenList = urlIdent_blackwing_ct5_m6
                    else: urlChosenList = urlIdent_list_ct45_2025
                
                urlList = len(urlChosenList)
                for i, urlIdent in enumerate(urlChosenList, 1):
                    print(f"Testing Prefix: {urlIdent} ({i}/{urlList})")

                    m_data = model_data.get(model.replace("-CT5", ""), model_data["CORVETTE"])

                    status = processVin(session, db_conn, urlIdent, vinChanging, endVIN, yearDig, 
                                        m_data["start_vin"], m_data["plant"], i, urlList, model, path, year)

                    db_conn.commit()

                    if status == "stop":
                        print("Execution halted via KeyboardInterrupt.")
                        break

        finally:
            if db_conn and db_conn.is_connected():
                print("\n[Database] Scrape loop finished or interrupted. Triggering production data sync...")
                try:
                    db_conn.commit()
                    proc_cursor = db_conn.cursor()
                    proc_cursor.callproc('execute_gm_data_sync')
                    db_conn.commit()
                    proc_cursor.close()
                    print("[Database] Success: Relational tables updated successfully.")
                except Exception as e:
                    print(f"[Database] Error running production sync procedure: {e}")

    stats = get_scrape_stats()
    elapsedTime = time.time() - startTime
    formatted_duration = format_time(elapsedTime)
    
    summary_text = (f"✅ **{year} {model} Scrape Completed**\n⏱️ **Duration:** {formatted_duration}\n"
                    f"📦 **Found:** `{stats['found']}` | 🔍 **Tested:** `{stats['tested']}`\n"
                    f"----------------------------------------------------")
    
    print(f"\nCompleted in: {formatted_duration}\nFound: {stats['found']} | Tested: {stats['tested']}")
    print("----------------------------------------------------------------------------\n")
    send_discord_message(summary_text)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        error_details = traceback.format_exc()

        model_name = "Unknown Model"
        year_name = "Unknown Year"
        
        if "--model" in sys.argv:
            try:
                model_idx = sys.argv.index("--model") + 1
                model_name = sys.argv[model_idx]
            except IndexError:
                pass
                
        if "--year" in sys.argv:
            try:
                year_idx = sys.argv.index("--year") + 1
                year_name = sys.argv[year_idx]
            except IndexError:
                pass

        discord_msg = (f"🚨 **CRITICAL ERROR: {year_name} {model_name} Scraper Crashed** 🚨\n"
                       f"**Error:** `{str(e)}`\n"
                       f"----------------------------------------------------")

        try:
            send_discord_message(discord_msg)
        except Exception as discord_err:
            print(f"\n[WARNING] Failed to send Discord crash notification: {discord_err}")

        print(f"\n[FATAL ERROR] Script crashed:\n{error_details}")

        sys.exit(1)
