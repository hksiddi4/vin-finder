import fitz
import csv
import os

# Step 1: Alpha-numeric values for Check Digit
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
    return vin[:8] + check_digit + vin[9:]

def format_time(seconds):
    days, remainder = divmod(int(seconds), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    if seconds >= 30: minutes += 1
    
    time_parts = []
    if days > 0: time_parts.append(f"{days}d")
    if hours > 0: time_parts.append(f"{hours}h")
    if minutes > 0: time_parts.append(f"{minutes}m")
    return ", ".join(time_parts) if time_parts else "< 1m"

def extractPDF(contentsByte):
    try:
        doc = fitz.open(stream=contentsByte, filetype="pdf")
        text = doc.load_page(0).get_text() if len(doc) > 0 else ""
        doc.close()
        return text
    except Exception:
        return None

def writeCSV(pdf_info, path, model, year):
    if pdf_info is None: return
    fullPath = os.path.join(path, f"{year}_{model.lower()}.csv")
    file_exists = os.path.isfile(fullPath)
    with open(fullPath, "a", newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=pdf_info.keys())
        if not file_exists: writer.writeheader()
        writer.writerow(pdf_info)

# Global Config
years = {'2027': 'V', '2026': 'T', '2025': 'S', '2024': 'R'}
year = '2026'
yearDig = years.get(year)

model_data = {
    "CORVETTE": {"start_vin": "1G1Y", "plant": "5"},
}

skip_files_map = {
    "CORVETTE": [f'{year}/skip_corvette.txt'],
}

engines_dict = {
    "LT2": "6.2L V8 DI", "LS6": "6.7L V8 DI",
    "LT6": "5.5L V8 DI", "LT7": "5.5L (335 ci) Twin-Turbo V8",
}

trans_dict = {
    "M1K": "DCT8", "M1L": "DCT8", "M1M": "DCT8", 
    "M1N": "DCT8", "MLP": "DCT8", "MLH": "DCT8",
}

body_dict = {"CM9": "CONVERTIBLE", "CFC": "CONVERTIBLE"}