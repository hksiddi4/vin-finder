# 2024 Camaro ZL1 Collector's Edition Finder

Made this to find all 350 of the collector's edition cars.

The only input is:
* Get the starting and ending 6 numbers of VINs you want to search through

## 2024 Camaro VIN breakdown
![Camaro VIN breakdown](https://www.camaro6.com/forums/attachment.php?attachmentid=1022448&stc=1&d=1583377227)
Example (#001 Collector's Edition used)
```
1G1FJ1R6XR0100021
```

J1R6 = Manual, Coupe, LT4 Engine

Check digit can be anything including "X" and 0~9

R = 2024 Model Year

The last 6 digits are the sequence of the build.

## How it works
Add any 2020+ GM vehicle's VIN to the end of this URL and you should get a window sticker for that vehicle.
```
https://cws.gm.com/vs-cws/vehshop/v2/vehicle/windowsticker?vin=
```
Sticker.py takes the input of starting and ending sequence numbers and (specifically for ZL1's only) runs against every iteration including all 10 check digits as well as all 4 bodystyle/transmission combos for a total of 40 tests per one VIN.

Each VIN has an API call sent to the link created and if the window sticker returns then an error is sent as a JSONDecodeError (since it's a PDF). If there isn't a VIN then a JSON object is returned with one item being 'errorMessage'.

If a window sticker is returned, the VIN will be appended to the 'ceVin.txt' file and will be told in the console (along with the mobile notification).

This continues until the script finishes the specified ending VIN.

## Notes
There are commented lines as I changed the approach multiple times.

def sendNotif is solely for the Pushover iOS app, I have muted it recently due to an issue detailed below.

'lastVin.txt' is unused as it is a part of the commented-out code. Originally I had thought the CEs were all within a few thousand from #001-350 but that is not the case so now I'm going in batches (this is where I added the user input for starting/ending VINs)

## Issues
I was having timeout issues but just recently added the timeout=10 to my requests so fingers crossed.

The greatest issue is false positives, for some reason, the API requests will return as JSONDecodeError even though they are JSON objects. My guess is the server messing up as I've tested false positives alone and received no error.

This caused me to create the (aptly named) 'Test.py' script.

You paste the VINs from 'ceVin.txt' in the same format in this file and run the script. It will open each VIN individually in a tab for me to manually check through. I have to do this anyway to check if the VIN is a CE as all 2024 VINs are included not solely CE. But this us a lot of 'Error failed to load pdf' tabs that pop up, unfortunately. Not sure how to fix this since GM returns the PDF but literally nothing else in the request :(
