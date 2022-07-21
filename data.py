import pandas as pd

def getServices(calendar_dates,railroad):
    while True:
        listOfServices = calendar_dates[calendar_dates.date == getDate()]
        if not listOfServices.empty:
            break
        else:
            if railroad == 'MNRR':
                print("Opps! That was not a valid date. 07/14/2022 to 11/20/2022 only.")
            else:
                print("Opps! That was not a valid date. 07/13/2022 to 09/05/2022 only.")
    return listOfServices

def getDate():
    month = input("Enter the month (as a two digit number): ")
    day = input("Enter the day (as a two digit number): ")
    year = input("Enter the year (as a four digit number): ")
    if year+month+day == '':
        return int('20220721')
    return int(year+month+day)

def loadData():
    railroad = input("Enter the railroad (MNRR/LIRR): ")
    print("Wait a moment as we read in data...")
    if railroad == 'MNRR':
        return pd.read_csv(f'data/{railroad}/calendar_dates.csv'), pd.read_csv(f'data/{railroad}/routes.csv'), pd.read_csv(f'data/{railroad}/stop_times.csv'), pd.read_csv(f'data/{railroad}/stops.csv'),  pd.read_csv(f'data/{railroad}/trips.csv'), pd.read_csv(f'data/{railroad}/calendar_dates.csv'), pd.read_csv(f'data/{railroad}/transfers.csv'), railroad
    else:
        return pd.read_csv(f'data/{railroad}/calendar_dates.csv'), pd.read_csv(f'data/{railroad}/routes.csv'), pd.read_csv(f'data/{railroad}/stop_times.csv'), pd.read_csv(f'data/{railroad}/stops.csv'),  pd.read_csv(f'data/{railroad}/trips.csv'), None, None, railroad

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
    trainNum = input("Train number: ")
    try: 
        trip_id = listOfTrains[listOfTrains.trip_short_name == trainNum].trip_id.to_numpy()[0]
        route = routes[routes.route_id == listOfTrains[listOfTrains.trip_short_name ==trainNum].route_id.to_numpy()[0]].route_long_name.to_numpy()[0]
        trip_headsign = listOfTrains[listOfTrains.trip_short_name == trainNum].trip_headsign.to_numpy()[0]
        trip_stops = stop_times[stop_times.trip_id == trip_id]
    except:
        print("Error train not found!")
        return

    print('Train line:',route)
    print('Train to:',trip_headsign)
    listStops(trip_stops,stops)

def listStops(trip_stops,stops):
    trip_stops = trip_stops.to_numpy()
    for stop in trip_stops:
        stop_name = stops[stops.stop_id == stop[3]].stop_name.to_numpy()[0]
        print(stop_name,stop[1])

def getTrainsAtStop(listOfTrains,stop_times,routes,stops,reformated,transfers=None):
    stop_name = input("Enter station name: ")
    num = cvtStringToNumber(stop_name,stops)
   
    count = 0
    for i in reformated:
        arr = i.to_numpy()
        for ii in arr:
            if ii[3] == int(num):
                print(ii)
                count += 1
    print(count)
    return None

def cvtStringToNumber(stop_name,stops):
    trainName = stops[stops.stop_name == stop_name]
    if trainName.empty == True:
        return None
    else:
        return trainName.stop_id.to_numpy()[0]

def reformat(listOfTrains,stop_times): 
    reformated = []
    myFile = open("output.txt","a")
    for train in listOfTrains.trip_id:
        temp = stop_times[stop_times.trip_id == train]
        reformated.append(temp)
        myFile.write(temp.to_string()+"\n")
    myFile.close()
    return reformated


def main():

    # prepare data
    calendar_dates, routes, stop_times, stops, trips, calendar, transfers, railroad = loadData()

    # get dates from user & finds the services that run that day
    listOfServices = getServices(calendar_dates,railroad)

    # gets all of the trains that run that day
    listOfTrains = getTrains(listOfServices,trips)
    listOfTrains = listOfTrains.astype({'trip_short_name':'str'})
    print("Wait a while as we process data...")
    reformated = reformat(listOfTrains,stop_times)

    userRequest = ''
    while True:
        userRequest = input('What to do (A/B/C/D/E/Exit)\nA: Overall stats. on trains\nB: Search by train number\nC: Search Train Station\nD: Dump into file\nE: Dump to JSON\nInput: ')
        if (userRequest == '-1' or userRequest == 'Exit'):
            break
        elif userRequest == 'A':
            trainAnaysis(listOfTrains,routes)
        elif userRequest == 'B':
            getInfoByTrainNumber(listOfTrains,stop_times,routes,stops)
        elif userRequest == 'C':
            getTrainsAtStop(listOfTrains,stop_times,routes,stops,reformated)
        elif userRequest == 'D':
            myFile = open("output.txt","w")
            myFile.write(listOfTrains.to_string())
            myFile.close()

if __name__ == "__main__":
    main()