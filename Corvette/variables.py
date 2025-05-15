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
    "G7Q": "WATKINS GLEN GRAY METALLIC",
    "G8G": "ARCTIC WHITE",
    "G9F": "CERAMIC MATRIX GRAY METALLIC",
    "GA7": "HYPERSONIC GRAY METALLIC",
    "GAN": "BLADE SILVER METALLIC",
    "GAR": "CARBON FLASH METALLIC",
    "GBA": "BLACK",
    "GBK": "COMPETITION YELLOW TINTCOAT METALLIC",
    "GC5": "AMPLIFY ORANGE TINTCOAT",
    "GC6": "CORVETTE RACING YELLOW TINTCOAT",
    "GD0": "ACCELERATE YELLOW METALLIC",
    "GJI": "SHADOW GRAY METALLIC",
    "GJV": "RIPTIDE BLUE METALLIC",
    "GKZ": "TORCH RED",
    "GMO": "RAPID BLUE",
    "GPH": "RED MIST METALLIC TINTCOAT",
    "GS7": "ELKHART LAKE BLUE METALLIC",
    "GSJ": "SILVER FLARE METALLIC",
    "GTR": "ADMIRAL BLUE METALLIC",
    "GUI": "ZEUS BRONZE METALLIC",
    "GVR": "CACTI GREEN",
    "GXA": "SEA WOLF GRAY TRICOAT",
    "GXL": "HYSTERIA PURPLE METALLIC",
}

engines_dict = {
    "LT1": "6.2L (376 ci) V8 DI",
    "LT2": "6.2L V8 DI",
    "LT4": "6.2L SUPERCHARGED V8",
    "LT5": "6.2L SUPERCHARGED V8 TPI",
    "LT6": "5.5L V8 DI",
    "LT7": "5.5L (335 ci) Twin-Turbo V8"
}

body_dict = {
    "CM8": "CONVERTIBLE",
    "CM9": "CONVERTIBLE"
}

trans_dict = {
    "M1L": "DCT8",
    "M1M": "DCT8",
    "MLH": "DCT8",
    # 2019
    "M5U": "A8",
    "MEK": "M7",
    "MEL": "M7",
    "MEP": "M7"
}

trim_dict = {
    "3ZR": "3ZR",
    "1ZR": "1ZR",
    "3LZ": "3LZ",
    "2LZ": "2LZ",
    "1LZ": "1LZ",
    "3LT": "3LT",
    "2LT": "2LT",
    "1LT": "1LT"
}

mmc_2019 = {
    "1YY07": "CORVETTE STINGRAY",
    "1YY67": "CORVETTE STINGRAY",
    "1YX07": "CORVETTE WITH Z51",
    "1YX67": "CORVETTE WITH Z51",
    "1YW07": "CORVETTE GRAND SPORT",
    "1YW67": "CORVETTE GRAND SPORT",
    "1YZ07": "CORVETTE Z06",
    "1YZ67": "CORVETTE Z06",
    "1YV07": "CORVETTE ZR1",
    "1YV67": "CORVETTE ZR1"
}

mmc_2020 = {
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
    '2020': 'L',
    '2019': 'K'
}

urlIdent_2019_list = [
    "A2D7",
    "A3D7",
    "B2D7",
    "B3D7",
    "C2D7",
    "C3D7",
    "D2D7",
    "D3D7",
    "E2D7",
    "E3D7",
    "F2D7",
    "F3D7",
    "G2D7",
    "G3D7",
    "H2D7",
    "H3D7",
    "J2D7",
    "J3D7",
    "K2D7",
    "K3D7",
    "L2D7",
    "L3D7",
    "M2D7",
    "M3D7",
    "V2D7",
    "V3D7",
    "W2D7",
    "W3D7",
    "X2D7",
    "X3D7",
    "Y2D7",
    "Y3D7",
    "Z2D7",
    "Z3D7",
    "12D7",
    "13D7"
]

urlIdent_2019_z06_list = [
    "N2D6",
    "N3D6",
    "P2D6",
    "P3D6",
    "R2D6",
    "R3D6",
    "S2D6",
    "S3D6",
    "T2D6",
    "T3D6",
    "U2D6",
    "U3D6"
]

urlIdent_2019_zr1_list = [
    "42D9",
    "43D9",
    "52D9",
    "53D9"
]

urlIdent_list = [
    "A2D4",
    "A3D4",
    "B2D4",
    "B3D4",
    "C2D4",
    "C3D4"
]

urlIdent_z06_list = [
    "F3D3", # 3LZ Conv.
    "F2D3", # 3LZ Coupe
    "E2D3", # 2LZ Coupe
    "D2D3", # 1LZ Coupe
    "E3D3", # 2LZ Conv.
    "D3D3", # 1LZ Conv.
]

urlIdent_eray_list = [ # Ordered by most-least production
    "M2D4", # 3LZ Coupe
    "M3D4", # 3LZ Conv.
    "L2D4", # 2LZ Coupe
    "L3D4", # 2LZ Conv.
    "K2D4", # 1LZ Coupe
    "K3D4", # 1LZ Conv.
]

urlIdent_zr1_list = [
    "G2D7", # 1LZ Coupe
    "G3D7", # 1LZ Conv.
    "J2D7", # 3LZ Coupe
    "J3D7", # 3LZ Conv.
]

while True:
    year = input('Enter year to test:\n')

    if year in years:
        yearDig = years[year]
        if year == '2019':
            mmc = mmc_2019
        else:
            mmc = mmc_2020
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
