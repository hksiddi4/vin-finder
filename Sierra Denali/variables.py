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
    
    updated_vin = vin[:8] + check_digit + vin[9:]
    return updated_vin

colors_dict = {
    "GCI": "CARBON BLACK METALLIC",
    "G1W": "WHITE FROST TRICOAT",
    "G2X": "DEEP MAHOGANY METALLIC",
    "G6M": "TITANIUM RUSH METALLIC",
    "G7C": "CARDINAL RED",
    "G9K": "SATIN STEEL METALLIC",
    "GA0": "PACIFIC BLUE METALLIC",
    "GAN": "QUICKSILVER METALLIC",
    "GAZ": "SUMMIT WHITE",
    "GB8": "EBONY TWILIGHT METALLIC",
    "GBA": "ONYX BLACK",
    "GED": "HUNTER METALLIC",
    "GJI": "DARK SKY METALLIC",
    "GLT": "DDYNAMIC BLUE METALLIC",
    "GNK": "BROWNSTONE METALLIC",
    "GNO": "THUNDERSTORM GRAY",
    "GNT": "VOLCANIC RED TINTCOAT",
    "GPJ": "RED QUARTZ TINTCOAT",
    "GS6": "SMOKEY QUARTZ METALLIC",
    "GSK": "CAYENNE RED TINTCOAT",
    "GTL": "DESERT SAND METALLIC",
    "GXD": "STERLING METALLIC",
    "GXP": "DOWNPOUR METALLIC"
}

engines_dict = {
    "L3B": "4 Cylinder, L4, 2.7L, SIDI VVT, Turbo, DOHC, Aluminum",
    "L5P": "ENGINE DIESEL, 8 CYL, 6.6L, DI, V8, TURBO, DURAMAX, GEN 5, VAR. 1",
    "L82": "8 Cylinder, 5.3L, DI, AFM, Aluminum, GEN 5, VAR 1",
    "L84": "8 Cylinder, 5.3L, DI, DFM, Aluminum, GEN 5, VAR 2",
    "L87": "8 Cylinder, V8, 6.2L, DI AFM, Aluminum, GEN 5",
    "L8T": "8 CYL, 6.6L, SIDI, VVT, CAST IRON",
    "LM2": "DIESEL, 6 Cylinder, 3.0L, CRI, V6, DOHC, Turbo, VGT, Aluminum",
    "LV3": "6 Cylinder, 4.3L, GEN 5, SIDI, V6, VVT, OHV, E85 MAX, Aluminum",
    "LZ0": "DIESEL, Duramax 3.0L Turbo-Diesel I6"
}

trim_dict = {
    "5SA": "1",
    "5SB": "2"
}

mmc = {
    "TK10543": "DENALI"
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
    "8FED",
    "8FET",
    "9FEL",
    "9FET",
    "9FED",
    "HGED",
    "UGE8",
    "UGEL",
    "UGED",
    "UGET",
    "UHEL",
    "UHE8",
    "UHET"
]

while True:
    year = input('Enter year to test:\n')

    if year in years:
        yearDig = years[year]
        break
    else:
        print("Invalid year.")

with open(f'{year}/skip_sierra.txt', 'r') as file:
    skip_sierra = [int(line.strip()) for line in file if line.strip().isdigit()]
