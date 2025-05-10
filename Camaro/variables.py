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
    "GAZ": "SUMMIT WHITE",
    "GNW": "PANTHER BLACK MATTE",
    "GLK": "PANTHER BLACK METALLIC",
    "GBA": "BLACK",
    "GB8": "MOSAIC BLACK METALLIC",
    "GJI": "SHADOW GRAY METALLIC",
    "G9K": "SATIN STEEL GREY METALLIC",
    "GXD": "SHARKSKIN METALLIC",
    "GAN": "SILVER ICE METALLIC",
    "GKK": "RIVERSIDE BLUE METALLIC",
    "GJV": "RIPTIDE BLUE METALLIC",
    "GMO": "RAPID BLUE",
    "GJ0": "RALLY GREEN METALLIC",
    "GKO": "SHOCK",
    "GCP": "NITRO YELLOW METALLIC",
    "GCF": "VIVID ORANGE METALLIC",
    "G16": "CRUSH",
    "GSK": "WILD CHERRY TINTCOAT",
    "GNT": "RADIANT RED TINTCOAT",
    "G7E": "GARNET RED TINTCOAT",
    "G7C": "RED HOT",
}

engines_dict = {
    "LTG": "2.0L Turbo, 4-cylinder, SIDI, VVT",
    "LGX": "3.6L V6, DI, VVT",
    "LT1": "6.2L (376 ci) V8 DI",
    "LT4": "6.2L SUPERCHARGED V8"
}

body_dict = {
    "CM8": "CONVERTIBLE"
}

trans_dict = {
    "MN6": "M6",
    "MX0": "A10"
}

trim_dict = {
    "ZL1": "ZL1",
    "2SS": "2SS",
    "1SS": "1SS",
    "1LZ": "LT1",
    "3LT": "3LT",
    "2LT": "2LT",
    "1LT": "1LT",
    "1LS": "1LS"
}

# Year digit
years = {
    '2024': 'R',
    '2023': 'P',
    '2022': 'N',
    '2021': 'M',
    '2020': 'L',
    '2019': 'K'
}

# Manual/Auto/Coupe/Conv. Differentiations - Ordered by 2024 Highest-Lowest
urlIdent_list_2024 = [
    "B1RS",
    "H1R7",
    "D1RS",
    "D3DS",
    "H3D7",
    "F1R7",
    "B3DS",
    "G1R7",
    "K1R6",
    "J1R6",
    "F3D7",
    "E1R7",
    "K3D6",
    "G3D7",
    "A1RS",
    "C1RS",
    "J3D6",
    "C3DS",
    "A3DS",
    "E3D7"
]

# Manual/Auto/Coupe/Conv. Differentiations - Ordered by 2023 Highest-Lowest
urlIdent_list_2023 = [
    "B1RX",
    "F1R7",
    "H1R7",
    "B1RS",
    "F3D7",
    "K1R6",
    "B3DX",
    "D1RS",
    "E1R7",
    "H3D7",
    "D3DS",
    "B3DS",
    "J1R6",
    "G1R7",
    "K3D6",
    "D1RX",
    "D3DX",
    "E3D7",
    "A1RX",
    "G3D7",
    "J3D6",
    "A1RS",
    "C1RS",
    "C3DS",
    "A3DX",
    "C3DX",
    "C1RX",
    "A3DS"
]

# Manual/Auto/Coupe/Conv. Differentiations - Ordered by 2022 Highest-Lowest
urlIdent_list_2022 = [
    "F1R7",
    "B1RX",
    "H1R7",
    "E1R7",
    "K1R6",
    "B1RS",
    "F3D7",
    "G1R7",
    "H3D7",
    "D1RS",
    "J1R6",
    "B3DX",
    "D1RX",
    "D3DS",
    "K3D6",
    "A1RX",
    "B3DS",
    "E3D7",
    "D3DX",
    "G3D7",
    "A1RS",
    "C1RS",
    "C1RX",
    "J3D6",
    "A3DX",
    "C3DS",
    "C3DX",
    "A3DS"
]

# Manual/Auto/Coupe/Conv. Differentiations - Ordered by 2021 Highest-Lowest
urlIdent_list_2021 = [
    "F1R7",
    "B1RS",
    "B1RX",
    "H1R7",
    "E1R7",
    "D1RS",
    "K1R6",
    "H3D7",
    "B3DS",
    "G1R7",
    "J1R6",
    "D3DS",
    "F3D7",
    "A1RX",
    "A1RS",
    "D1RX",
    "K3D6",
    "C1RS",
    "B3DX",
    "G3D7",
    "D3DX",
    "E3D7",
    "J3D6",
    "C3DS",
    "A3DS",
    "C1RX",
    "A3DX",
    "C3DX"
]

# Manual/Auto/Coupe/Conv. Differentiations - Ordered by 2020 Highest-Lowest
urlIdent_list_2020 = [
    "B1RS",
    "B1RX",
    "H1R7",
    "F1R7",
    "B3DX",
    "H3D7",
    "B3DS",
    "E1R7",
    "D1RS",
    "K1R6",
    "G1R7",
    "A1RX",
    "D3DS",
    "J1R6",
    "A1RS",
    "F3D7",
    "D1RX",
    "K3D6",
    "G3D7",
    "C1RS",
    "D3DX",
    "E3D7",
    "J3D6",
    "A3DS",
    "C1RX",
    "C3DS",
    "A3DX",
    "C3DX"
]

urlIdent_list_2019 = [
    "B1RS",
    "B1RX",
    "H1R7",
    "F1R7",
    "B3DX",
    "H3D7",
    "B3DS",
    "E1R7",
    "D1RS",
    "K1R6",
    "G1R7",
    "A1RX",
    "D3DS",
    "J1R6",
    "A1RS",
    "F3D7",
    "D1RX",
    "K3D6",
    "G3D7",
    "C1RS",
    "D3DX",
    "E3D7",
    "J3D6",
    "A3DS",
    "C1RX",
    "C3DS",
    "A3DX",
    "C3DX"
]

while True:
    year = input('Enter year to test:\n')

    if year in years:
        yearDig = years[year]
        chosenIdent = f"urlIdent_list_{year}"
        chosenList = globals()[chosenIdent]
        break
    else:
        print("Invalid year.")

with open(f'{year}/skip_camaro.txt', 'r') as file:
    skip_camaro = [int(line.strip()) for line in file if line.strip().isdigit()]

with open(f'{year}/skip_cadillac.txt', 'r') as file:
    skip_cadillac = [int(line.strip()) for line in file if line.strip().isdigit()]

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
