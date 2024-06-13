apiURL = {
    "Buick": "https://cws.gm.com/vs-cws/vehshop/v2/vehicle/windowsticker?vin=",
    "Cadillac": "https://cws.gm.com/vs-cws/vehshop/v2/vehicle/windowsticker?vin=",
    "Chevrolet": "https://cws.gm.com/vs-cws/vehshop/v2/vehicle/windowsticker?vin=",
    "Chrysler": "https://www.chrysler.com/hostd/windowsticker/getWindowStickerPdf.do?vin=",
    "Dodge": "https://www.dodge.com/hostd/windowsticker/getWindowStickerPdf.do?vin=",
    "Fiat": "https://www.fiatusa.com/hostd/windowsticker/getWindowStickerPdf.do?vin=",
    "Genesis": "https://prevapp.hyundaiusa.com/DealerExternalService.svc/Monroney/pdf/GetMonroneyLabelPDF?VIN=",
    "Hyundai": "https://prevapp.hyundaiusa.com/DealerExternalService.svc/Monroney/pdf/GetMonroneyLabelPDF?VIN=",
    "Jeep": "https://www.jeep.com/hostd/windowsticker/getWindowStickerPdf.do?vin=",
    "RAM": "https://www.ramtrucks.com/hostd/windowsticker/getWindowStickerPdf.do?vin="
}

# Working Check Digit Calculator --------------------------------------------------------
# Step 1: Assign values to letters
alpha_numeric_conversion = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'P': 7, 'R': 9, 'S': 2,
    'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9
}

# Step 2: Position and Weight Factor
weight_factors = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]

models = [
    "Cadillac"
]

colors_dict = {
    "G1W": "CRYSTAL WHITE TRICOAT",
    "G7C": "VELOCITY RED",
    "G7E": "RED OBSESSION TINTCOAT",
    "G7W": "DARK EMERALD FROST",
    "G9G": "DIAMOND SKY METALLIC",
    "G9K": "SATIN STEEL METALLIC",
    "GAZ": "SUMMIT WHITE",
    "GBA": "BLACK RAVEN",
    "GCF": "BLAZE METALLIC",
    "GJ0": "EVERGREEN METALLIC",
    "GJI": "SHADOW METALLIC",
    "GJV": "COASTAL BLUE METALLIC",
    "GKK": "WAVE METALLIC",
    "GLK": "BLACK DIAMOND TRICOAT",
    "GLL": "ROYAL SPICE METALLIC",
    "GLR": "GARNET METALLIC",
    "GLU": "DARK MOON METALLIC",
    "GMO": "ELECTRIC BLUE",
    "GNT": "RADIANT RED TINTCOAT",
    "GRW": "RIFT METALLIC",
    "GSK": "INFRARED TINTCOAT",
    "GXD": "ARGENT SILVER METALLIC",
    "GXF": "MIDNIGHT SKY METALLIC",
    "GCP": "CYBER YELLOW METALLIC",
    "GXU": "MIDNIGHT STEEL METALLIC",
    "GKA": "MERCURY SILVER METALLIC",
    "GAI": "DEEP SPACE METALLIC",
    "GAE": "DRIFT METALLIC",
    "GBW": "TYPHOON METALLIC"
}

engines_dict = {
    "LSY": "2.0L TURBO, 4-CYL, SIDI",
    "L3B": "2.7L TURBO",
    "LGY": "3.0L TWIN TURBO V6, SIDI",
    "LF4": "3.6L V6 TWIN TURBO SIDI, DOHC, VVT",
    "LT4": "6.2L SUPERCHARGED V8"
}

trans_dict = {
    "MG9": "M6",
    "MJK": "M6",
    "MHA": "A8",
    "MHU": "A10",
    "MQA": "A10",
    "MHS": "A10",
    "MQ2": "A10",
    "MHX": "A10"
}

ext_dict = {
    "F46": "AWD",
    "RWL": "RWD"
}

# Year digit --------------------------------------------------------------------------
years = {
    '2025': 'S',
    '2024': 'R',
    '2023': 'P',
    '2022': 'N',
    '2021': 'M',
    '2020': 'L'
}

urlIdent_blackwing_list = [
    "75RP", # V-Series Blackwing, LF4 | (410000-411000): Checked | https://www.cadillac.com/sedans/ct4-v-blackwing/mondrian-editions#
    "65RP", # V-Series Blackwing, LF4 | (410000-411000): Ongoing | https://www.cadillac.com/sedans/ct4-v-blackwing/mondrian-editions#
    "25R6", # V-Series Blackwing, LT4 | 
    "35R6"
]

# Manual/Auto/Coupe/Conv. Differentiations
urlIdent_list = [
    # "J5RK", # Luxery/RWD, LSY (w/o 8speaker)
    # "A5RK", # Luxery/RWD, LSY (w/ 8 speaker)
    # "K5RK", # Luxery/AWD, LSY
    # "E5RK", # Luxery/AWD, LSY
    # "B5RK", # Premium Luxery/RWD, LSY
    # "F5RK", # Premium Luxery/AWD, LSY
    # "B5RL", # Premium Luxery/RWD, L3B
    # "F5RL", # Premium Luxery/AWD, L3B
    # "C5RK", # Sport/RWD, LSY
    # "G5RK", # Sport/AWD, LSY
    # "D5RL", # V-Series/RWD, L3B
    # "H5RL", # V-Series/AWD, L3B
    "N5RK", # Premium Luxery/RWD, LSY
    "T5RK", # Premium Luxery/AWD, LSY
    "S5RK", # Premium Luxery/AWD, LSY
    "N5RW", # Premium Luxery/RWD, LGY
    "T5RW", # Premium Luxery/AWD, LGY
    "S5RW", # Premium Luxery/AWD, LGY
    "P5RK", # Sport/RWD, LSY
    "U5RK", # Sport/AWD, LSY
    # "R5RW", # V-Series/RWD, LGY
    # "V5RW" # V-Series/AWD, LGY
]

ct5Ident_list = [
    "N5RW", # PREMIUM LUXURY/AWD LGY
    "P5RK", # Sport/RWD, LSY
    "N5RK", # Premium Luxery/RWD, LSY
    "S5RW" # Premium Luxery/AWD, LGY
]

with open('skip_cadillac.txt', 'r') as file:
    skip_cadillac = [int(line.strip()) for line in file]

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
