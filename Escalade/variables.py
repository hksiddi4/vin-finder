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
    "G1E": "LONG BEACH RED METALLIC",
    "G1W": "WHITE PEARL METALLIC TRICOAT",
    "G26": "SEBRING ORANGE",
    "G48": "CAFFEINE METALLIC",
    "G8G": "ARCTIC WHITE",
    "G9F": "CERAMIC MATRIX GRAY METALLIC",
    "GA7": "HYPERSONIC GRAY METALLIC",
    "GAN": "BLADE SILVER METALLIC",
    "GAR": "CARBON FLASH METALLIC",
    "GBA": "BLACK",
    "GC5": "AMPLIFY ORANGE TINTCOAT",
    "GD0": "ACCELERATE YELLOW METALLIC",
    "GJI": "SHADOW GRAY METALLIC",
    "GJV": "RIPTIDE BLUE METALLIC",
    "GKZ": "TORCH RED",
    "GMO": "RAPID BLUE",
    "GPH": "RED MIST METALLIC TINTCOAT",
    "GS7": "ELKHART LAKE BLUE METALLIC",
    "GSJ": "SILVER FLARE METALLIC",
    "GUI": "ZEUS BRONZE METALLIC",
    "GVR": "CACTI GREEN",
    "GXA": "SEA WOLF GRAY TRICOAT",
}

engines_dict = {
    "L86": "6.2L EcoTec3 V8 AFM",
    "L87": "6.2L EcoTec3 V8 DFM",
    "LM2": "Duramax 3.0L Turbo-Diesel I6",
    "LT4": "6.2L SUPERCHARGED V8",
}

body_dict = {
    "": "SUV"
}

trans_dict = {
    "MF6": "A10",
    "MHS": "A10",
}

trim_dict = {
    "1SD": "PLATINUM",
    "1SC": "PREMIUM LUXURY",
    "1SB": "LUXURY",
}

mmc = {
    "6K15706": "4WD",
    "6C15706": "RWD",
}

years = {
    '2025': 'S',
    '2024': 'R',
    '2023': 'P',
    '2022': 'N',
    '2021': 'M',
    '2020': 'L'
}

urlIdent_list = [
    "3AKL",
    "3BKJ",
    "3BKL",
    "3CKJ",
    "3CKL",
    "3DKL",
    "3EKL",
    "3FKL",
    "3GKL",
    "4AKT",
    "4BKJ",
    "4BKL",
    "4CKJ",
    "4CKL",
    "4DKJ",
    "4DKL",
    "4EKL",
    "4FKL",
    "4FKT",
    "4GKL",
    "4GKT",
    "4HK9",
]

while True:
    year = input('Enter year to test:\n')

    if year in years:
        yearDig = years[year]
        break
    else:
        print("Invalid year.")

with open(f'{year}/skip_escalade.txt', 'r') as file:
    skip_escalade = [int(line.strip()) for line in file if line.strip().isdigit()]

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
