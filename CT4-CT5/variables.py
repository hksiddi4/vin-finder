# Working Check Digit Calculator --------------------------------------------------------
# Step 1: Assign values to letters
alpha_numeric_conversion = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'P': 7, 'R': 9, 'S': 2,
    'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9
}

# Step 2: Position and Weight Factor
weight_factors = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]

colors_dict = {
    "G1W": "CRYSTAL WHITE TRICOAT",
    "G7C": "VELOCITY RED",
    "G7E": "RED OBSESSION TINTCOAT",
    "G7W": "DARK EMERALD FROST",
    "G9G": "DIAMOND SKY METALLIC",
    "G9K": "SATIN STEEL METALLIC",
    "GAN": "RADIANT SILVER METALLIC",
    "GAZ": "SUMMIT WHITE",
    "GB8": "STELLAR BLACK METALLIC",
    "GBA": "BLACK RAVEN",
    "GCF": "BLAZE METALLIC",
    "GCI": "MANHATTAN NOIR METALLIC",
    "GCP": "CYBER YELLOW METALLIC",
    "GJ0": "EVERGREEN METALLIC",
    "GJI": "SHADOW METALLIC",
    "GJV": "COASTAL BLUE METALLIC",
    "GKA": "MERCURY SILVER METALLIC",
    "GKK": "WAVE METALLIC",
    "GLK": "BLACK DIAMOND TRICOAT",
    "GLL": "ROYAL SPICE METALLIC",
    "GLR": "GARNET METALLIC",
    "GLU": "DARK MOON METALLIC",
    "GMO": "ELECTRIC BLUE",
    "GNT": "RADIANT RED TINTCOAT",
    "GNW": "MAVERICK NOIR FROST",
    "GPJ": "RED HORIZON TINTCOAT",
    "GRW": "RIFT METALLIC",
    "GSK": "INFRARED TINTCOAT",
    "GXD": "ARGENT SILVER METALLIC",
    "GXF": "MIDNIGHT SKY METALLIC",
    "GXU": "MIDNIGHT STEEL METALLIC"
}

engines_dict = {
    "LSY": "2.0L TURBO, 4-CYL, SIDI",
    "LGX": "3.6L V6, DI, VVT",
    "L3B": "2.7L TURBO",
    "LGY": "3.0L TWIN TURBO V6, SIDI",
    "LF4": "3.6L V6 TWIN TURBO SIDI, DOHC, VVT",
    "LT4": "6.2L SUPERCHARGED V8",
    "LTA": "4.2L, V8, TWIN TURBO"
}

trans_dict = {
    "M5N": "A8",
    "MHA": "A8",
    "MG9": "M6",
    "MJK": "M6",
    "MHS": "A10",
    "MHS": "A10",
    "MHU": "A10",
    "MHW": "A10",
    "MHX": "A10",
    "MQ2": "A10",
    "MQA": "A10"
}

ext_dict = {
    "F46": "AWD",
    "RWL": "RWD"
}

years = {
    '2025': 'S',
    '2024': 'R',
    '2023': 'P',
    '2022': 'N',
    '2021': 'M',
    '2020': 'L'
}

urlIdent_blackwing_list_2022 = [
    "75RP", # CT4-V Blackwing A10
    "65RP", # CT4-V Blackwing M6
    "L5RP", # CT4-V Blackwing PreProd- Eval
    "Y5R6", # CT5-V Blackwing
    "35R6", # CT5-V Blackwing A10
    "25R6" # CT5-V Blackwing M6
]

urlIdent_blackwing_list_2023 = [
    "L5RP", # CT4-V Blackwing
    "Y5R6" # CT5-V Blackwing
]

urlIdent_blackwing_list_2024 = [
    "75RP", # CT4-V Blackwing A10
    "65RP", # CT4-V Blackwing M6
    "35R6", # CT5-V Blackwing A10
    "25R6", # CT5-V Blackwing M6
]

# Manual/Auto/Coupe/Conv. Differentiations - Orderd by 2025 Highest-Lowest
urlIdent_list_ct45 = [
    "S5RW", # Premium Luxery/AWD, LGY, CT5
    "P5RK", # Sport/RWD, LSY, CT5
    "S5RK", # Premium Luxery/AWD, LSY, CT5
    "U5RK", # Sport/AWD, LSY, CT5
    "N5RW", # Premium Luxery/RWD, LGY, CT5
    "N5RK", # Premium Luxery/RWD, LSY, CT5
    "V5RW", # V-Series/AWD, LGY, CT5
    "W5RK", # Luxery/RWD, LSY, CT5
    "T5RW", # Premium Luxery/AWD, LGY, CT5
    "J5RK", # Luxery/RWD, LSY (w/o 8speaker), CT4
    "T5RK", # Premium Luxery/AWD, LSY, CT5
    "X5RK", # Luxery/AWD, LSY, CT5
    "R5RW", # V-Series/RWD, LGY, CT5
    "K5RK", # Luxery/AWD, LSY, CT4
    "A5RK", # Luxery/RWD, LSY (w/ 8 speaker), CT4
    "B5RK", # Premium Luxery/RWD, LSY, CT4
    "F5RK", # Premium Luxery/AWD, LSY, CT4
    "M5RK", # Luxery/RWD, LSY, CT5
    "G5RK", # Sport/AWD, LSY, CT4
    "C5RK", # Sport/RWD, LSY, CT4
    "H5RL", # V-Series/AWD, L3B, CT4
    "E5RK", # Luxery/AWD, LSY, CT4
    "D5RL", # V-Series/RWD, L3B, CT4
    "F5RL", # Premium Luxery/AWD, L3B, CT4
    "B5RL" # Premium Luxery/RWD, L3B, CT4
]

# CT6
urlIdent_list = [
    "B5RS", # Luxury / LGX
    "E5RS", # Premium Luxury / LGX
    "V5RJ", # Platinum / LTA
    "W5RJ" # V-Series / LTA
]

while True:
    year = input('Enter year to test:\n')

    if year in years:
        yearDig = years[year]
        break
    else:
        print("Invalid year.")

while True:
    ct6 = input('CT6?\n').lower()
    break

if int(year) <= 2024 or ct6 != 'y':
    with open(f'{year}/skip_camaro.txt', 'r') as file:
        skip_camaro = [int(line.strip()) for line in file if line.strip().isdigit()]

if ct6 != 'y':
    with open(f'{year}/skip_cadillac.txt', 'r') as file:
        skip_cadillac = [int(line.strip()) for line in file if line.strip().isdigit()]
else:
    with open(f'{year}/skip_cadillac_ct6.txt', 'r') as file:
        skip_cadillac_ct6 = [int(line.strip()) for line in file if line.strip().isdigit()]

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
