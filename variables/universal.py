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

years = {
    '2025': 'S',
    '2024': 'R',
    '2023': 'P',
    '2022': 'N',
    '2021': 'M',
    '2020': 'L',
    '2019': 'K'
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
}

trans_dict = {
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
}

body_dict = {
    "CM8": "CONVERTIBLE",
    "CM9": "CONVERTIBLE",
}
