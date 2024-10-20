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
    "LT2": "6.2L V8 DI",
    "LT6": "5.5L V8 DI",
    "LT7": "5.5L (335 ci) Twin-Turbo V8"
}

body_dict = {
    "CM9": "CONVERTIBLE"
}

trans_dict = {
    "M1L": "DCT8",
    "M1M": "DCT8",
    "MLH": "DCT8",
}

trim_dict = {
    "3LZ": "3LZ",
    "2LZ": "2LZ",
    "1LZ": "1LZ",
    "3LT": "3LT",
    "2LT": "2LT",
    "1LT": "1LT"
}

mmc = {
    "1YC07": "CORVETTE STINGRAY",
    "1YC67": "CORVETTE STINGRAY",
    "1YH07": "CORVETTE Z06",
    "1YH67": "CORVETTE Z06",
    "1YG07": "CORVETTE E-RAY",
    "1YG67": "CORVETTE E-RAY"
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
    "A2D4",
    "A3D4",
    "B2D4",
    "B3D4",
    "C2D4",
    "C3D4"
]

urlIdent_z06_list = [
    "D2D3",
    "D3D3",
    "E2D3",
    "E3D3",
    "F2D3",
    "F3D3"
]

urlIdent__eray_list = [
    "K2D4",
    "K3D4",
    "L2D4",
    "L3D4",
    "M2D4",
    "M3D4"
]

urlIdent__zr1_list = [
    "?2D7",
    "?3D7",
    "J2D7",
    "J3D7"
]

while True:
    year = input('Enter year to test:\n')

    if year in years:
        yearDig = years[year]
        break
    else:
        print("Invalid year.")

with open(f'{year}/skip_corvette.txt', 'r') as file:
    skip_corvette = [int(line.strip()) for line in file if line.strip().isdigit()]

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
