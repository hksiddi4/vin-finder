import requests
import time

# Working Check Digit Calculator --------------------------------------------------------
# Step 1: Assign values to letters
alpha_numeric_conversion = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'P': 7, 'R': 9, 'S': 2,
    'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9
}

# Step 2: Position and Weight Factor
weight_factors = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]

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

vinChanging = input("Enter start sequence: \n")
endVIN = input("Enter end sequence: \n")

def processVIN(vinChanging, endVIN):
    urlFirst = "https://experience.gm.com/ownercenter/recalls?vin=1G1F91R6"

    while vinChanging <= endVIN:
        if vinChanging in skip:
            print("\033[30mExisting sequence, skipping\033[0m")
            vinChanging += 1
            continue
        else:
            try:
                matchedVIN = "1G1F91R6XR0" + str(vinChanging)
                updated_vin = calculate_check_digit(matchedVIN)
                newUrl = urlFirst + updated_vin[8:11] + str(vinChanging).zfill(6)

                max_retries = 3
                retries = 0

                while retries < max_retries:
                    try:
                        contents = requests.get(newUrl, headers = {'User-Agent': 'camaro ce mexico finder', 'Accept-Language': 'en-US'}, timeout=120)

                        time.sleep(1)

                        input("WAIT")
                        # Write VIN to txt file
                        with open(f"tested.txt", "a") as f:
                            f.write(str(updated_vin + "\n"))

                        # Inform console
                        print("\033[33mMatch Found For VIN: " + updated_vin + "\033[0m")
                        pdf_text = extractPDF(newUrl, updated_vin)
                        pdf_info = extractInfo(pdf_text)
                        writeCSV(pdf_info)
                        # Append only the last 6 digits of the VIN to the list and file
                        with open("skip.txt", "a") as file:
                            file.write(str(vinChanging).zfill(6) + "\n")

                        # Increment VIN by 1
                        vinChanging += 1
                        break

                    except requests.exceptions.ReadTimeout:
                        # Retry request
                        print("Timed out, retrying...")
                        retries += 1
                        time.sleep(120)

            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
                if isinstance(e, requests.exceptions.ConnectionError) and isinstance(e.__cause__, ConnectionResetError):
                    print("ConnectionResetError occurred. Retrying...")
                    continue  # Continue with the next VIN
                else:
                    print("Unknown error occurred. Skipping this VIN.")
                    # Write VIN to RETRY.txt file
                    with open("RETRY.txt", "a") as f:
                        f.write(str("\n" + updated_vin))
                    vinChanging += 1  # Move to the next VIN
                    continue  # Continue with the next VIN

            # When canceled in console, record last checked VIN to lastVin.txt
            except KeyboardInterrupt:
                break

with open('skip.txt', 'r') as file:
    skip = [int(line.strip()) for line in file]

processVIN(vinChanging,endVIN)
