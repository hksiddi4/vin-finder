import requests
import PyPDF2
import os
import shutil

def download_pdf(url, save_path):
    response = requests.get(url, stream=True)
    with open(save_path, 'wb') as pdf_file:
        for chunk in response.iter_content(chunk_size=128):
            pdf_file.write(chunk)

with open("openVin.txt", "r") as f:
    vins = f.readlines()

# Specify the folder where you want to save the PDFs
download_folder = 'download'

for vin in vins:
    vin = vin[:17]
    fullUrl = "https://cws.gm.com/vs-cws/vehshop/v2/vehicle/windowsticker?vin=" + vin
    save_path = os.path.join(download_folder, vin + ".pdf")  # Include the folder path in save_path
    download_pdf(fullUrl, save_path)
    print(vin)

def read_pdf(file_path, page_number=0):
    with open(file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        if page_number < len(pdf_reader.pages):
            page = pdf_reader.pages[page_number]
            text = page.extract_text()
            return text
        else:
            return None

# Directory containing the PDF files
pdfs_directory = download_folder  # Use the same download folder for reading PDFs

# Specify the page number you want to extract (0 for the first page)
page_number = 0

search_phrases = ["PANTHER", "GARAGE 56"]
output_folders = ["CE", "G56"]

for filename in os.listdir(pdfs_directory):
    if filename.endswith('.pdf'):
        pdf_file_path = os.path.join(pdfs_directory, filename)
        vin = filename.replace(".pdf", "")
        if os.path.getsize(pdf_file_path) > 0:
            pdf_text = read_pdf(pdf_file_path, page_number)
        else:
            print(f"Incomplete download: {filename} --------------- RETRY DOWNLOAD")

        for i in range(len(search_phrases)):
            search_phrase = search_phrases[i]
            if pdf_text and search_phrase in pdf_text:
                output_folder = output_folders[i]
                output_path = os.path.join(download_folder, output_folder, filename)  # Updated output path
                os.makedirs(os.path.dirname(output_path), exist_ok=True)  # Ensure output directory exists
                shutil.copy(pdf_file_path, output_path)
                break
        else:
            print(f"No matching phrases found in {filename}")
