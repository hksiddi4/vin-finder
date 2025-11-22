import fitz
import csv

# Working Check Digit Calculator --------------------------------------------------------
# Step 1: Assign values to letters
alpha_numeric_conversion = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'P': 7, 'R': 9, 'S': 2,
    'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9
}

# Step 2: Position and Weight Factor
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
    
    # Step 3: Divide the total by 11 and find the remainder
    remainder = total % 11
    
    # Step 4: Calculate the check digit or use 'X' if remainder is 10
    check_digit = str(remainder) if remainder < 10 else 'X'
    
    # Insert the check digit at the ninth position and return the updated VIN
    updated_vin = vin[:8] + check_digit + vin[9:]
    return updated_vin

def format_time(seconds):
    days = int(seconds // 86400)
    remainder = seconds % 86400
    hours = int(remainder // 3600)
    remainder %= 3600
    minutes = int(remainder // 60)
    seconds = int(remainder % 60)

    if seconds >= 30:
        minutes += 1
    
    time_parts = []
    
    if days == 1:
        time_parts.append(f"{days} day")
    elif days > 1:
        time_parts.append(f"{days} days")
    
    if hours == 1:
        time_parts.append(f"{hours} hour")
    elif hours > 1:
        time_parts.append(f"{hours} hours")
    
    if minutes == 1:
        time_parts.append(f"{minutes} minute")
    elif minutes > 1:
        time_parts.append(f"{minutes} minutes")
    
    return ", ".join(time_parts) if time_parts else "< 1 minute"

def extractPDF(contentsByte, updated_vin, path):
    pdf_path = f"{path}/temp.pdf"
    try:
        with open(pdf_path, "wb") as f:
            f.write(contentsByte)
        doc = fitz.open(pdf_path)
        text = ""
        if len(doc) > 0:
            if len(doc) > 1:
                with open(f"{path}/notes.txt", "a") as nf:
                    nf.write(f"{updated_vin} - Multiple Pages\n")
            page = doc.load_page(0)
            text = page.get_text()
        doc.close()
        return text
    except fitz.FileDataError as e:
        return None

def writeCSV(pdf_info, path, model):
    global year
    if pdf_info is None:
        return
    fieldnames = pdf_info.keys()

    with open(f"{path}/{year}_{model.lower()}.csv", "a", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(pdf_info)

years = {
    '2026': 'T',
    '2025': 'S',
    '2024': 'R',
    '2023': 'P',
    '2022': 'N',
    '2021': 'M',
    '2020': 'L',
    '2019': 'K'
}

while True:
    year = input('Enter year to test:\n')
    yearDig = years.get(year)
    if yearDig:
        break
    else:
        print("\033[91mInvalid year.\033[0m")

# Plant Codes ----------------------- As of July 2025 ---------------------------------
# 0 = Lansing Grand River Assembly                  : Camaro, CT4-CT5
# 1 = Wentzville Assembly                           : Colorado, Express, Canyon, Savana
# 4 = Orion Assembly                                : Sierra Denali EV, Silverado - Sierra Denali EV isn't right?
# 5 = Bowling Green Assembly                        : Corvette
# F = Fairfax II Assembly                           : Bolt EV (Starting Nov. '25)
# F = Flint Truck Assembly                          : Silverado HD, Sierra HD, Sierra HD Denali, HD ZR2, HD ZR2 Bison, HD Trail Boss, HD AT4X, HD AT4X AEV
# J = Lansing Delta Township Assembly               : Enclave, Traverse, Acadia
# R = Arlington Assembly                            : Tahoe, Suburban, Yukon, Yukon XL, Escalade, Escalade-V
# S = Ramos Arizpe Assembly                         : OPTIQ, Blazer EV, Equinox EV, Equinox, Blazer - Hundreds of thousands of sequence...
# U = Factory Zero (Detroit-Hamtramck Assembly)     : Hummer EV (Pickup and SUV), Silverado EV, Sierra EV, Escalade IQ
# Z = Fort Wayne Assembly                           : Silverado 1500, Sierra 1500
# Z = Spring Hill Manufacturing                     : XT5, XT6, Lyriq, Vistiq

model_data = {
    "CAMARO": {"start_vin": "1G1F", "plant": "0"},
    "CORVETTE": {"start_vin": "1G1Y", "plant": "5"},
    "CT4": {"start_vin": "1G6D", "plant": "0"},
    "CT5": {"start_vin": "1G6D", "plant": "0"},
    "CT6": {"start_vin": "1G6K", "plant": "U"},
    "HUMMER EV": [
        {"start_vin": "1GKB", "plant": "U"},
        {"start_vin": "1GT4", "plant": "U"},
        {"start_vin": "1GT1", "plant": "U"},
    ],
    "SILVERADO EV": {"start_vin": "1GC1", "plant": "U"},
    "SIERRA EV": {"start_vin": "1GT4", "plant": "U"},
    "ESCALADE IQ": {"start_vin": "1GYT", "plant": "U"},
}

skip_files_map = {
    "CAMARO_CT4_CT5": [
        f'CAMARO/{year}/skip_camaro.txt',
        f'CT4-CT5/{year}/skip_ct4-ct5.txt'
    ],
    "HUMMER_SILVERADO_SIERRA_ESCALADEIQ_EV": [
        f'HUMMER EV/{year}/skip_hummer ev.txt',
        f'SILVERADO EV/{year}/skip_silverado ev.txt',
        f'SIERRA EV/{year}/skip_sierra ev.txt',
        #f'ESCALADE IQ/{year}/skip_escalade iq.txt' # Repeating sequence in Hummer/Escalade IQ
    ],
    "HUMMER_SILVERADO_SIERRA_EV": [
        f'HUMMER EV/{year}/skip_hummer ev.txt',
        f'SILVERADO EV/{year}/skip_silverado ev.txt',
        f'SIERRA EV/{year}/skip_sierra ev.txt'
    ],
    "HUMMER_EV": [f'HUMMER EV/{year}/skip_hummer ev.txt'],
    "CT4-CT5": [f'CT4-CT5/{year}/skip_ct4-ct5.txt'],
    "CORVETTE": [f'CORVETTE/{year}/skip_corvette.txt'],
    "CT6": [f'CT4-CT5/{year}/skip_cadillac_ct6.txt']
}

engines_dict = {
    "L3B": "2.7L TURBO",
    "LF4": "3.6L V6 TWIN TURBO SIDI, DOHC, VVT",
    "LGX": "3.6L V6, DI, VVT",
    "LGY": "3.0L TWIN TURBO V6, SIDI",
    "LSY": "2.0L TURBO, 4-CYL, SIDI",
    "LT1": "6.2L (376 ci) V8 DI",
    "LT2": "6.2L V8 DI",
    "LT4": "6.2L SUPERCHARGED V8",
    "LT5": "6.2L SUPERCHARGED V8 TPI",
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
    "M5N": "A8",
    "M5U": "A8",
    "MEK": "M7",
    "MEL": "M7",
    "MEP": "M7",
    "MG9": "M6",
    "MHA": "A8",
    "MHS": "A10",
    "MHU": "A10",
    "MHW": "A10",
    "MHX": "A10",
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
    "1SE": "SUV",
    "1SF": "SUV",
    "1SG": "SUV",
}
