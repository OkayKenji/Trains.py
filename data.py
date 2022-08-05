import pandas as pd
import os
import time as t
from datetime import timedelta as td


def getServices(calendar_dates,railroad):
    calendar_dates = calendar_dates.astype({'date':'str'})
    while True:
        listOfServices = calendar_dates[calendar_dates.date == getDate()]
        if not listOfServices.empty:
            break
        else:
            if railroad == 'mnrr':
                print("Opps! That was not a valid date. 07/14/2022 to 11/20/2022 only.")
            else:
                print("Opps! That was not a valid date. 07/13/2022 to 09/05/2022 only.")
    return listOfServices

def getDate():
    month = input("Enter the month (as a two digit number): ")
    day = input("Enter the day (as a two digit number): ")
    year = input("Enter the year (as a four digit number): ")
    if year+month+day == '':
        return '20220723'
    return year+month+day

def loadData():
    while True:
        railroad = input("Enter the railroad (MNRR/LIRR): ").lower()
        
        if railroad == 'mnrr':
            print("Wait a moment as we read in data...")
            return pd.read_csv(f'data/MNRR/calendar_dates.csv'), pd.read_csv(f'data/MNRR/routes.csv'), pd.read_csv(f'data/MNRR/stop_times.csv'), pd.read_csv(f'data/MNRR/stops.csv'),  pd.read_csv(f'data/MNRR/trips.csv'), pd.read_csv(f'data/MNRR/calendar_dates.csv'), pd.read_csv(f'data/MNRR/transfers.csv'), railroad
        elif railroad == 'lirr':
            print("Wait a moment as we read in data...")
            return pd.read_csv(f'data/LIRR/calendar_dates.csv'), pd.read_csv(f'data/LIRR/routes.csv'), pd.read_csv(f'data/LIRR/stop_times.csv'), pd.read_csv(f'data/LIRR/stops.csv'),  pd.read_csv(f'data/LIRR/trips.csv'), None, None, railroad
        else:
            print("Error, invalid name, try again.")

def getTrains(listOfServices,trips): 
    listOfTrains = []
    for service in listOfServices.service_id:
        listOfTrains.append(trips[trips.service_id == service])
    return pd.DataFrame(pd.concat(listOfTrains))

def trainAnaysis(listOfTrains,routes):
    print("Total number of trains:", len(listOfTrains))

    print("Number of trains per line/branch: ")
    for index,route in enumerate(routes.route_id):
        print("    "+routes.route_long_name.iloc[index]+":",len(listOfTrains[listOfTrains.route_id == route]))

def getInfoByTrainNumber(listOfTrains,stop_times,routes,stops):
    while True:
        trainNum = input("Train number: ")
        if trainNum == 'Exit':
            return
        try: 
            trip_id = listOfTrains[listOfTrains.trip_short_name == trainNum].trip_id.to_numpy()[0]
            route = routes[routes.route_id == listOfTrains[listOfTrains.trip_short_name ==trainNum].route_id.to_numpy()[0]].route_long_name.to_numpy()[0]
            trip_headsign = listOfTrains[listOfTrains.trip_short_name == trainNum].trip_headsign.to_numpy()[0]
            trip_stops = stop_times[stop_times.trip_id == trip_id]
        except:
            print("Error train not found!")
        else:
            break
            

    print('Train line:',route)
    print('Train to:',trip_headsign)
    listStops(trip_stops,stops)

def listStops(trip_stops,stops):
    trip_stops = trip_stops.to_numpy()
    for stop in trip_stops:
        stop_name = stops[stops.stop_id == stop[3]].stop_name.to_numpy()[0]
        print(stop_name,stop[1])

def getStopingTrainsAtStop(routes,railroad,stops,reformated,asNumber=None):

    if asNumber == None:
        while True:
            stop_name = input("Enter station name: ")
            num = cvtStringToNumber(stop_name,stops)
            if num == None:
                print("Error, station not found!")
            else:
                break
    else:
        num = asNumber
   
    allTrains = []
    count = 0
    for train in reformated:
        stopsArr = train[0].to_numpy()
        for stop in stopsArr:
            if stop[3] == int(num): # stop[3] contains the id of the station
                if railroad == 'mnrr':
                    allTrains.append([stop[1], stop[7], stop[8], train[1], train[2], train[3],stopsArr[0][1],train[4],cvtNumberToString(stopsArr[0][3],stops),stopsArr])
                    # print(f'{ii[1]} on track {ii[7]} {ii[8]} Train: {i[1]} to: {i[2]} going: {i[3]}') 
                else:
                    allTrains.append([stop[1], None, None, train[1], train[2], train[3],stopsArr[0][1],train[4],cvtNumberToString(stopsArr[0][3],stops),stopsArr])
                    # print(f'{ii[1]} Train: {i[1]} to: {i[2]} going: {i[3]}')
                count += 1

    allTrains = sorted(allTrains, key=lambda allTrains: allTrains[0]) # sort by time it get's to the station

    if railroad == 'mnrr':
        allTrains = cleanAllTrains(allTrains,routes)
    else:
        for i,ele in enumerate(allTrains):
            allTrains[i][7] = cvtRouteStringToNumber(routes,allTrains[i][7])
            if ele[5] == '1':
                allTrains[i][5] = 'West'
            else:
                allTrains[i][5] = 'East'


    for i in allTrains:
        if railroad == 'mnrr':
            if i[2] == 'H':
                print(f'{i[0]} {i[7]} Line train to {i[4]}. Arrivng track {i[1]} going {i[5]}. (Train: {i[3]}) *Train may depart 5 minutes earlier than the time shown')
            else:
                print(f'{i[0]} {i[7]} Line train to {i[4]}. Arrivng track {i[1]} going {i[5]}. (Train: {i[3]})')
        else:
            print(f'{i[0]} {i[7]} train to {i[4]}. Going: {i[5]}. (Train: {i[3]})')
    # print(ah)

    
    aaabbb = pd.DataFrame(data=allTrains)
    myFile = open("output.txt","w")
    myFile.write(aaabbb.to_string())
    myFile.close()

    return allTrains


def cleanAllTrains(allTrains,routes):
    for i,ele in enumerate(allTrains):
        allTrains[i][7] = cvtRouteStringToNumber(routes,allTrains[i][7]) 

        if ele[5] == '1':
            allTrains[i][5] = 'South'
        else:
            allTrains[i][5] = 'North'

        # if int(ele[0][0:2])>23:
        #    allTrains[i][0] = f'0{str(int(ele[0][0:2])%24)}{ele[0][2:8]}'



    count = 0
    for i,ele in enumerate(allTrains):
        if int(ele[6][0:2])<4:
            count+=1
        else:
            break
    for AXN in range(count):
        moveBack = allTrains.pop(0)
        moveBack[0] = f'{str(int(moveBack[0][0:2])+24)}{moveBack[0][2:8]}'
        allTrains.append(moveBack)

    allTrains = sorted(allTrains, key=lambda allTrains: allTrains[0])

    return allTrains

def cvtStringToNumber(stop_name,stops):
    trainName = stops[stops.stop_name == stop_name]
    if trainName.empty == True:
        return None
    else:
        return trainName.stop_id.to_numpy()[0]

def cvtNumberToString(stop_num,stops):
    stopName = stops[stops.stop_id == stop_num]
    if stopName.empty == True:
        return None
    else:
        return stopName.stop_name.to_numpy()[0]

def cvtRouteStringToNumber(routes,route_id):
    route_name = routes[routes.route_id == route_id]
    if route_name.empty == True:
        return None
    else:
        return route_name.route_long_name.to_numpy()[0]

def getInfoByMultiStops(railroad,stops,reformated,routes):
    listOfStations = []

    while True:
        stop_name = input("Enter first station name: ")
        num = cvtStringToNumber(stop_name,stops)
        if num == None:
            print("Error, station not found!")
        else:
            listOfStations.append(num)
            break

    while True:
        stop_name = input("Enter intermidiate station name: ")
        if stop_name == 'exit':
            break
        num = cvtStringToNumber(stop_name,stops)
        if num == None:
            print("Error, station not found!")
        else:
            listOfStations.append(num)
    while True:
        stop_name = input("Enter last station name: ")
        num = cvtStringToNumber(stop_name,stops)
        if num == None:
            print("Error, station not found!")
        else:
            listOfStations.append(num)
            break

    print(listOfStations)
    allTrains = getStopingTrainsAtStop(routes,railroad,stops,reformated,asNumber=listOfStations[0])
    
    os.system('cls')

    indexToRemove = len(allTrains)-1
    doNotRemove = False
    for index in range(1,len(listOfStations)):
        selectStations = listOfStations[index]
        indexToRemove = len(allTrains)-1
        # print(selectStations)
        for train in reversed(allTrains):
            
            please_Remove = False
            for stop in train[9]:
                if stop[3] == int(selectStations):
                    please_Remove = False
                    break
                else:
                    please_Remove = True


            if please_Remove:
                allTrains.pop(indexToRemove)

            indexToRemove -= 1
    allTrains = sorted(allTrains, key=lambda allTrains: allTrains[5])

    for train in allTrains:
        print(f'Train: {train[3]}, departing {train[0]}, making {str(len(train[9]))} stops. Goes from {train[8]} to {train[4]} going {train[5]}.')
    return allTrains

def reformat(listOfTrains,stop_times): 
    reformated = []
    tempPercent = 0
    print(f'{0}%...')
    for index,train in enumerate(listOfTrains.trip_id):
        if ((index/len(listOfTrains))*100 > tempPercent+10 ):
            print(f'{tempPercent+10}%...')
            tempPercent += 10
        
        # print(f'Percent complete: {str((index/len(listOfTrains))*100)}%')
        temp = [stop_times[stop_times.trip_id == train],listOfTrains.trip_short_name.iloc[index],listOfTrains.trip_headsign.iloc[index],listOfTrains.direction_id.iloc[index],listOfTrains.route_id.iloc[index],listOfTrains.shape_id.iloc[index]]
        reformated.append(temp)
    print(f'{100}%...')
    return reformated


def main():

    # prepare data
    calendar_dates, routes, stop_times, stops, trips, calendar, transfers, railroad = loadData()

    # get dates from user & finds the services that run that day
    listOfServices = getServices(calendar_dates,railroad)

    # gets all of the trains that run that day
    listOfTrains = getTrains(listOfServices,trips)
    listOfTrains = listOfTrains.astype({'trip_short_name':'str','trip_headsign':'str','trip_short_name':'str','direction_id':'str','shape_id':'str'})
    print("Wait a while as we process data...")
    reformated = reformat(listOfTrains,stop_times)

    userRequest = ''
    while True:
        os.system('cls')
        userRequest = input('What to do (A/B/C/D/E/F/Exit)\nA: Overall stats. on trains\nB: Search by train number\nC: Search Train Station (only trains that stop there)\nD: Dump into file\nE: Dump to JSON\nF: Multiple Stations\nInput: ')
        if (userRequest == '-1' or userRequest == 'Exit'):
            exit(0)
        elif userRequest == 'A':
            trainAnaysis(listOfTrains,routes)
        elif userRequest == 'B':
            getInfoByTrainNumber(listOfTrains,stop_times,routes,stops)
        elif userRequest == 'C':
            getStopingTrainsAtStop(routes,railroad,stops,reformated)
        elif userRequest == 'D':
            myFile = open("output.txt","w")
            myFile.write(listOfTrains.to_string())
            myFile.close()
            print('Done')
        elif userRequest == 'E':
            print('opps not done yet.')
        elif userRequest == 'F':
            getInfoByMultiStops(railroad,stops,reformated,routes)
        else:
            print('Try again.')
            t.sleep(0.5)
            continue

        input()

if __name__ == "__main__":
    main()