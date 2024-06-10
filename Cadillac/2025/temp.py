import requests
import time

# Open the file RETRY.txt and read lines
with open('RETRY.txt', 'r') as file:
    lines = file.readlines()

# Base URL
base_url = "https://cws.gm.com/vs-cws/vehshop/v2/vehicle/windowsticker?vin="

# Process each line
for line in lines:
    # Strip whitespace and construct the URL
    vin = line.strip()
    url = base_url + vin
    
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Process the response as needed
            print(response.text)
        else:
            print(f"Failed to access {url}: Status code {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        # Handle exceptions
        print(f"An error occurred: {e}")

    time.sleep(1)
