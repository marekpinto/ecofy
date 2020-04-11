import requests
import json
import csv

with open('results.csv', mode='w') as csv_file:
    fieldnames = ['lat', 'lon', 'sol_in', 'sol_out', 'wind_in', 'wind_out']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()


numCoordinates = 101
numRemoved = 0
for x in range(30, 70):
    for y in range(30, 70):
        lat = (x * (180/(numCoordinates-1+60))) - 90
        long = (y * (360/(numCoordinates-1+60))) - 180
        response = requests.get("https://power.larc.nasa.gov/cgi-bin/v1/DataAccess.py?request=execute&identifier=SinglePoint&parameters=ALLSKY_SFC_SW_DWN,WS10M&startDate=20150401&endDate=20190430&userCommunity=SSE&tempAverage=DAILY&outputList=JSON&lat=" + str(lat) + "&lon=" + str(long) + "&user=anonymous")
        solar = response.json()['features'][0]['properties']['parameter']['ALLSKY_SFC_SW_DWN']
        wind = response.json()['features'][0]['properties']['parameter']['WS10M']
        sol_in = []
        sol_out = []
        wind_in = []
        wind_out = []
        prevMon = 3
        solCount = 0
        for date in solar:
            mon = date[5:6]
            if mon != prevMon:
                if solCount!=0:
                    sol_in.append(solTotal/solCount)
                    wind_in.append(windTotal/windCount)
                solTotal = 0
                solCount = 0
                solNumMissing = 0
                windTotal = 0
                windCount = 0
                windNumMissing = 0
                keepGoing = True
            if date == '20180401':
                keepGoing = False
            prevMon = mon
            if keepGoing != True:
                continue
            sun = float(solar[date])
            windValue = float(wind[date])
            if sun < 0:
                solNumMissing+=1
                continue
            if windValue < 0:
                windNumMissing+=1
                continue
            if solNumMissing>=10 or windNumMissing>=10:
                numRemoved+=1
                break
            solTotal += sun
            solCount+=1
            windTotal += windValue
            windCount+=1
            if date == '20190430':
                sol_in.append(solTotal/solCount)
                wind_in.append(windTotal/windCount)
        print(len(sol_in))
        if len(sol_in) == 48:
            for i in range(47, 35, -1):
                sol_out.append(sol_in.pop())
                wind_out.append(wind_in.pop())
            with open('results.csv', mode='a+', newline='') as csv_file:
                fieldnames = ['lat', 'lon', 'sol_in', 'sol_out', 'wind_in', 'wind_out']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writerow({'lat': lat, 'lon': long, 'sol_in': sol_in, 'sol_out': sol_out, 'wind_in': wind_in, 'wind_out': wind_out})

