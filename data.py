import pandas as pd

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
        railroad = input("Enter the railroad (MNRR/LIRR): ")
        
        if railroad.lower() == 'mnrr':
            print("Wait a moment as we read in data...")
            return pd.read_csv(f'data/MNRR/calendar_dates.csv'), pd.read_csv(f'data/MNRR/routes.csv'), pd.read_csv(f'data/MNRR/stop_times.csv'), pd.read_csv(f'data/MNRR/stops.csv'),  pd.read_csv(f'data/MNRR/trips.csv'), pd.read_csv(f'data/MNRR/calendar_dates.csv'), pd.read_csv(f'data/MNRR/transfers.csv'), railroad
        elif railroad.lower() == 'lirr':
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

def getStopingTrainsAtStop(railroad,stops,reformated):

    while True:
        stop_name = input("Enter station name: ")
        num = cvtStringToNumber(stop_name,stops)
        if num == None:
            print("Error, station not found!")
        else:
            break
   
    count = 0
    for i in reformated:
        arr = i[0].to_numpy()
        for ii in arr:
            if ii[3] == int(num):
                if railroad == 'mnrr':
                    print(f'{ii[1]} on track {ii[7]} {ii[8]} Train: {i[1]} to: {i[2]} going: {i[3]}')
                else:
                    print(f'{ii[1]} Train: {i[1]} to: {i[2]} going: {i[3]}')
                count += 1
    print(count)

def cvtStringToNumber(stop_name,stops):
    trainName = stops[stops.stop_name == stop_name]
    if trainName.empty == True:
        return None
    else:
        return trainName.stop_id.to_numpy()[0]

def reformat(listOfTrains,stop_times): 
    reformated = []
    for index,train in enumerate(listOfTrains.trip_id):
        temp = [stop_times[stop_times.trip_id == train],listOfTrains.trip_short_name.iloc[index],listOfTrains.trip_headsign.iloc[index],listOfTrains.direction_id.iloc[index],listOfTrains.shape_id.iloc[index]]
        reformated.append(temp)

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
        userRequest = input('What to do (A/B/C/D/E/Exit)\nA: Overall stats. on trains\nB: Search by train number\nC: Search Train Station\nD: Dump into file\nE: Dump to JSON\nInput: ')
        if (userRequest == '-1' or userRequest == 'Exit'):
            break
        elif userRequest == 'A':
            trainAnaysis(listOfTrains,routes)
        elif userRequest == 'B':
            getInfoByTrainNumber(listOfTrains,stop_times,routes,stops)
        elif userRequest == 'C':
            getStopingTrainsAtStop(railroad,stops,reformated)
        elif userRequest == 'D':
            myFile = open("output.txt","w")
            myFile.write(listOfTrains.to_string())
            myFile.close()

if __name__ == "__main__":
    main()