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
    "GNW": "PANTHER BLACK METALLIC",
    "GLK": "PANTHER BLACK MATTE",
    "GBA": "BLACK",
    "GJI": "SHADOW GRAY METALLIC",
    "G9K": "SATIN STEEL GREY METALLIC",
    "GXD": "SHARKSKIN METALLIC",
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
    "G7C": "RED HOT"
}

engines_dict = {
    "LTG": "2.0L TURBO, 4-CYL, SIDI, vvt",
    "LGX": "3.6L V6 DI, VVT",
    "LT1": "6.2L (376 ci) V8 DI",
    "LT4": "6.2L SUPERCHARGED V8"
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

body_dict = {
    "CM8": "CONVERTIBLE"
}

# Year digit --------------------------------------------------------------------------
years = {
    '2024': 'R',
    '2023': 'P',
    '2022': 'N',
    '2021': 'M',
    '2020': 'L',
}

# Manual/Auto/Coupe/Conv. Differentiations
urlIdent_list = [
    "J1R6", # Manual Coupe
    "J3D6", # Manual Conv.
    "K1R6", # Auto Coupe
    "K3D6"  # Auto Conv.
]

with open('skip_cadillac.txt', 'r') as file:
    skip_cadillac = [int(line.strip()) for line in file]
