import webbrowser
import time

with open("openVin.txt", "r") as f:
    vins = f.readlines()

for vin in vins:
    fullUrl = "https://cws.gm.com/vs-cws/vehshop/v2/vehicle/windowsticker?vin=" + vin.strip()
    time.sleep(2)
    webbrowser.open(fullUrl)