import requests
from PyPDF2 import PdfReader
import os
import csv
import re

year = input("What year to run?: ")

def download_pdf(url, save_path):
    response = requests.get(url, stream=True)
    with open(save_path, 'wb') as pdf_file:
        for chunk in response.iter_content(chunk_size=128):
            pdf_file.write(chunk)

def read_pdf(file_path, page_number=0):
    try:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            if page_number < len(pdf_reader.pages):
                page = pdf_reader.pages[page_number]
                text = page.extract_text()
                return text
            else:
                return None
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return None

vin_pattern = r"VIN\s*([\d\w]+)"
exterior_pattern = r"EXTERIOR:\s*(.+)"
interior_pattern = r"INTERIOR:\s*(.+)"
engine_pattern = r"ENGINE, (.+)"
transmission_pattern = r"(\d+-SPEED .+ TRANSMISSION)"
dealer_info_pattern = r"DEALER TO WHOM DELIVERED\s*(.+?)\s*(?:\n|,)\s*(.+?)\s*(?:\n|,)\s*(\w+(?:\s*\w{2})?)\s*[, ]*(.*)"
options_pattern = r'"Options":\s*\[([\s\S]+?)\]'

# Updated patterns for additional information
model_year_pattern = r'"model_year":\s*"(.*?)"'
mmc_code_pattern = r'"mmc_code":\s*"(.*?)"'
msrp_pattern = r"TOTAL VEHICLE PRICE\s*\$([\d,]+)|\$\s*([\d,]+(?:\.\d{2})?)"
order_number_pattern = r'"order_number":\s*"(.*?)"'
creation_date_pattern = r'"creation_date":\s*"(.*?)"'

extracted_data = []

# Directory containing the PDF files
pdfs_directory = f'download{year}'  # Specify the correct directory name

# Specify the page number you want to extract (0 for the first page)
page_number = 0

for filename in os.listdir(pdfs_directory):
    if filename.endswith('.pdf'):
        pdf_file_path = os.path.join(pdfs_directory, filename)
        vin = filename.replace(".pdf", "")
        pdf_text = read_pdf(pdf_file_path, page_number)
        
        if pdf_text:
            model_year = re.search(model_year_pattern, pdf_text)
            vin_match = re.search(vin_pattern, pdf_text)
            exterior_match = re.search(exterior_pattern, pdf_text)
            interior_match = re.search(interior_pattern, pdf_text)
            engine_match = re.search(engine_pattern, pdf_text)
            transmission_match = re.search(transmission_pattern, pdf_text)
            dealer_info_match = re.search(dealer_info_pattern, pdf_text)
            options_match = re.search(options_pattern, pdf_text)
            mmc_code_match = re.search(mmc_code_pattern, pdf_text)
            msrp_match = re.finditer(msrp_pattern, pdf_text)
            order_number_match = re.search(order_number_pattern, pdf_text)
            creation_date_match = re.search(creation_date_pattern, pdf_text)

            msrp_values = [m.group(1) or m.group(2) for m in msrp_match]
            msrp = max(msrp_values, key=lambda x: len(str(x)))  # Get the largest value
        
            options_str = options_match.group(1)
            options = [opt.strip() for opt in re.findall(r'"(.*?)"', options_str) if opt.strip()]

            if (
                vin_match and exterior_match and interior_match and
                engine_match and transmission_match and dealer_info_match and options_match and
                mmc_code_match and msrp_match and order_number_match
            ):

                extracted_info = {
                    "Serial": vin_match.group(1)[-6:],
                    "VIN": vin_match.group(1),
                    "Model Year": model_year.group(1),
                    "MMC Code": mmc_code_match.group(1).strip(),
                    "Transmission": transmission_match.group(1),
                    "Color": exterior_match.group(1),
                    "MSRP": msrp,
                    "Dealer": dealer_info_match.group(1).strip(),
                    "City": dealer_info_match.group(3).strip(),
                    "State": dealer_info_match.group(4).strip()[:2],
                    "Order Number": order_number_match.group(1),
                    "Creation Date": creation_date_match.group(1),
                    "URL": f"https://cws.gm.com/vs-cws/vehshop/v2/vehicle/windowsticker?vin={vin_match.group(1)}",
                    "ALL RPOs": options
                }
                extracted_data.append(extracted_info)
            else:
                print(f"Data extraction failed for PDF: {pdf_file_path}")
        else:
            print(f"Failed to extract text from PDF: {pdf_file_path}")

csv_file_path = f"{year}.csv"

with open(csv_file_path, mode="w", newline='', encoding='utf-8') as csv_file:
    fieldnames = ["Serial", "VIN", "Model Year", "MMC Code", "Transmission", "Color", "MSRP",
                  "Dealer", "City", "State", "Order Number", "Creation Date", "URL", "ALL RPOs"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()

    for data_row in extracted_data:
        writer.writerow(data_row)

print(f"Extracted data has been written to: {csv_file_path}")
