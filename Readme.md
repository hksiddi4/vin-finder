# Currently expanding to other brands
Currently finishing up Camaro and then Cadillac, Challenger is always running in the background since they have immensely more sequences than GM (a few hundred thousand vs maybe 50-60k on a good year)

If the Challenger script is a success then any Stellantis model will work with tweaking

Any GM model will work with tweaking, there are a few more brands I will look into later.

Currently known API's (thanks to Spork Marketing LLC)

- GM - 2020+

- Stellantis - 2013+

- Stellantis EU - 2015+

- Chrysler - 2014+

Not publicly available

- Genesis - 2018+

- Hyundai - 2014+

# All 350 ZL1 Collectors Edition cars have been found
* 2024 Camaro ZL1 Collectors Edition Finder
I made this script to find all 350 of the collectors edition cars.

[List and Excel Sheet of Known VINs](https://www.camaro6.com/forums/showthread.php?t=619436)

## Example script run
![Camaro VIN breakdown](https://www.camaro6.com/forums/attachment.php?attachmentid=1022448&stc=1&d=1583377227)
Example (#001 Collectors Edition used)
```
1G1FJ1R6XR0100021
```
1G1F = All 6th generation Camaro VINs start with these same four characters

J1R6 = VIN Identification - Manual, Coupe, LT4 Engine

The check digit can be anything including "X" and 0~9 - The script will calculate the check digit

R = 2024 Model Year - [Each year digit is predetermined](https://www.alldata.com/us/en/support/repair-collision/article/vin-to-year-chart)

The last 6 digits are the sequence of the build. Aka what order it was built.

## How it works
Add any 2020+ GM vehicle's VIN to the end of this URL and you should get a window sticker for that vehicle.
```
https://cws.gm.com/vs-cws/vehshop/v2/vehicle/windowsticker?vin=
```
The start and end inputs define the range of sequences to search through, it will go through the predefined VIN identifications combos for the year specified.

Each VIN has an API call sent to the link created, if the window sticker is there than an error is sent as a JSONDecodeError (since it's a PDF). If there isn't a VIN then a JSON object is returned with one item being 'errorMessage'. (Dodge returns a PDF no matter what so slightly tweaked to check the returned PDF instead)

The returned VIN is then written in a few different files and finally written to the .csv inside the year folder.

This continues until the script finishes the specified ending VIN.

# Notes
Retry.py is meant for the VIN's that were skipped during the main script run, if there's an error or issue it skips the VIN and appends it to RETRY.txt so that this other script when ran will only run the VIN's in that .txt file

Other API's found thanks to https://windowstickerlookup.com/

## Issues
MuPDF error's out sometimes, unsure how to fix as the only sign is missing fields typically in the .csv. Have implemented a missing_field operation to maybe assist in finding a solution.

Dodge scripts work but I recently returned to trying it as my first attempt broke something after a few thousand successful pulls, crossing fingers it doesn't break again.
