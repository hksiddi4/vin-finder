# Working Check Digit Calculator --------------------------------------------------------
# Step 1: Assign values to letters
alpha_numeric_conversion = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'P': 7, 'R': 9, 'S': 2,
    'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9
}

# Step 2: Position and Weight Factor
weight_factors = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]

# Year digit --------------------------------------------------------------------------
years = {
    '2025': 'S',
    '2024': 'R',
    '2023': 'P',
    '2022': 'N',
    '2021': 'M',
    '2020': 'L',
    '2019': 'K',
    '2018': 'J',
    '2017': 'H',
    '2016': 'G',
    '2015': 'F',
    '2014': 'E',
    '2013': 'D'
}

# Manual/Auto/Coupe/Conv. Differentiations
urlIdent_list_2023 = [
    "ZL9",
    "ZC9",
    "ZFJ",
    "ZJG",
    "ZBT",
    "ZAG",
    "ZKG",
    "ZGG",
    "YCJ",
    "YBT",
    "YAG"
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

with open(f'{year}/skip_challenger.txt', 'r') as file:
    #skip_challenger = [int(line.strip()) for line in file if line.strip().isdigit()]
    skip_challenger = []

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
