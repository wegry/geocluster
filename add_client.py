import csv
import json
import math
import os
import requests
import string

#Reads and writes from a file called cluster.csv in the same directory as it. Must have the following columns [name, address, longitude, latitude, cluster]

print('{0}\n{0}\nThis program checks to see what geopoints (and therefore cluster) a potential point\n is nearest to.'.format('-'*40))

#geopoints have names and addresses as well as geocoded points
class geopoints:
    'Has name, address, geocode, and frequency attribute'
    def __init__(self, name, address, lat = 0, long = 0, cluster = 0):
        self.name = name
        self.address = remove_commas(address)
        self.geocode = Point(float(lat), float(long))
        self.cluster = cluster
        if lat == 0 and long == 0:
            self.__geocodeset__()

    #Haversine function from http://www.movable-type.co.uk/scripts/gis-faq-5.1.html
    def distance_between(self, other_point):
        dlat = math.radians(self.geocode.lat - other_point.geocode.lat)
        dlon = math.radians(self.geocode.lon - other_point.geocode.lon)
        #Radius of the earth in miles
        R = 3963.1676
        #a = sin^2(dlat/2) + cos(lat1) * cos(lat2) * sin^2(dlon/2)
        a = (math.sin(dlat/2))*(math.sin(dlat/2)) + math.cos(math.radians(self.geocode.lat))*math.cos(math.radians(other_point.geocode.lat))*(math.sin(dlon/2))*(math.sin(dlon/2))
        #c = 2 * arcsin(min(1,sqrt(a)))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        #d = R * c
        return R * c

    def __str__(self):
        return string.capwords(self.name + ' ' + self.address + ' ' + self.geocode.__str__())

    #Changes default lat long to actual address(hopefully)
    def __geocodeset__(self):
        if (len(self.address) > 0):
            plussedAddress = ''
            for char in self.address:
                if char == ' ':
                    char = '+'
                plussedAddress += char
            returnPoint = get_lat_long(plussedAddress)
            self.geocode = Point(returnPoint[0], returnPoint[1])

def remove_commas(le_string):
    return_string = ''
    for character in le_string:
        if character != ',':
            return_string += character
    return return_string

class Point:
    'Has latitude and longitude attributes'
    def __init__(self, lat, lon): #for the uninitiated, lat and lon
        self.lat = lat
        self.lon = lon

    def __str__(self):
        return '(' + str(self.lat) + ', ' + str(self.lon) + ')'

def get_lat_long(location):
    if (len(location) > 0):
        output = 'json'
        request = 'http://maps.google.com/maps/api/geocode/{}?address={}&sensor=false'.format(output, location)
        rawJSON = requests.get(request)
        data = rawJSON.json()
        return_tuple = [0, 0]
        try:
            return_tuple[0] = data['results'][0]['geometry']['location']['lat']
            return_tuple[1] = data['results'][0]['geometry']['location']['lng']
        except BaseException:
            print('Something went wrong...')
    return return_tuple

def geopoints_creation():
    #Getting the geopoints's name from user input
        print('______________________________________________________\n')
        print('You selected the option to find the closest cluster to a particular geopoints.\n')
        name = ''
        while (True):
            name = input('What\'s this geopoints\'s name? ').strip()
            print('Is', name, 'correct? ', end = '')
            confirmation = input('(y/n) ').casefold()
            if confirmation == 'y' or confirmation == 'yes':
                print()
                break
            else:
                print('Try again. ', end = '')

        #Getting their address
        address = ''
        while (True):
            print('What\'s ', name, '\'s address?', sep = '', end = ' ')
            address = input()
            print('Is', address, 'correct? ', end = '')
            confirmation = input('(y/n) ').casefold()
            if confirmation == 'y' or confirmation == 'yes':
                print()
                break
            else:
                print('Try again.', end = ' ')

        return geopoints(name, address)

#The procedure

#parses the incoming csv
list = []
with open('cluster.csv') as csvfile:
    infoReader = csv.reader(csvfile, delimiter=',')

    print('\nReading in geopoints list...', end = '')
    for row in infoReader:
        column = []
        for item in row:
            column.append(' '.join(item.split()))
        list.append(column)
    print ('done.', len(list), 'entries read.\n')

if len(list) == 0:
    print('The list is empty, so nothing can be done...')
    quit()

header = list.pop(0) #takes care of header till later

geopoints_list = []
for row in list:
    column = row
    geopoints_list.append(geopoints(column[0], column[1], column[3], column[2], column [6], column[5], column[4], column [7])) #fix this

choice = ''
#Validates input
while (choice != 'quit' and choice != 'q'):
    print('What would you like to do?\n')
    print('A) Enter an address to see what cluster it would belong to')
    print('Or enter \'quit\' (or just q) to exit the program')
    while (True):
        choice = input('\tYour choice--> ').strip().casefold()
        if (choice == 'a' or choice == 'quit' or choice == 'q'):
            break
        else:
            print('Try again...')

    if choice == 'a':
        new_geopoints = geopoints_creation()
        if (new_geopoints.geocode.lat == 0 and new_geopoints.geocode.lon == 0):
            print('That address couldn\'t be found on Google Maps.')
        else:
            print('Matching', new_geopoints.__str__(), 'to existing geopoints...\n')
            closest = None
            closest_distance = float('inf')

            list_length = len(geopoints_list)
            for i in range(0, list_length):
                current_distance = geopoints_list[i].distance_between(new_geopoints)
                if (current_distance < closest_distance):
                    closest_distance =  current_distance
                    closest = geopoints_list[i]

            print('The closest geopoints in the list is ', closest.name, '. They\'re ', closest_distance.__round__(), ' miles away and their address is ', closest.address, '.', sep = '')
            new_geopoints.cluster = closest.cluster
            add = input('\nAdd the new geopoints to the geopoints list? (y/n) ').casefold()
            while(True):
                if add == 'y' or add == 'yes':
                    geopoints_list.append(new_geopoints)
                    geopoints_list.sort(key = lambda geopoints : float(geopoints.frequency))
                    geopoints_list.sort(key = lambda geopoints : float(geopoints.hours))
                    geopoints_list.sort(key = lambda geopoints : int(geopoints.cluster))
                    with open('temp.csv', 'w', newline='') as csvfile:
                        writer = csv.writer(csvfile, delimiter=',')
                        writer.writerow(header)
                        for person in geopoints_list:
                            writer.writerow([person.name, person.address, person.geocode.lon, person.geocode.lat, person.frequency, person.cleanTime, person.cluster])
                    os.rename('temp.csv', 'cluster.csv') #Overwrites old file after writing the new one's entirity
                    print('\nDone!\n{}\n'.format('_'*43))
                    break
                elif add == 'n' or add == 'no':
                    break
                    pass
                else:
                    add = input('Try again. (y/n)')
