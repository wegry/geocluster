import csv
import string
import urllib.request
import json

#This file takes a csv that contains a name column and one or more addresses
#and turns them into parsed data that is geocoded

#customers have names and addresses as well as geocoded points
class customer:
    "Has name, address, geocode, and frequency attribute"
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.geocode = Point(0, 0)
        self.frequency = "0"
        self.cleanTime = "0"

    def toString(self):
        if (len(self.name) > 10):
            return self.name + self.address + self.geocode.toString()

    #Changes default lat long to actual address(hopefully)
    def __geocodeset__(self):
        if (len(self.address) > 0):
            plussedAddress = ""
            for char in self.address:
                if char == " ":
                    char = "+"
                plussedAddress += char
            returnPoint = get_lat_long(plussedAddress)
            self.geocode = Point(returnPoint[0], returnPoint[1])

class Point:
    "Has latitude and longitude attributes"
    def __init__(self, lat, lon): #for the uninitiated, lat and lon
        self.lat = lat
        self.lon = lon

    def toString(self):
        return "(" + str(self.lon) + ", " + str(self.lat) + ")"

#pulls lat and longitude from Google Maps API
def get_lat_long(location):
    output = "json"
    request = "http://maps.google.com/maps/api/geocode/%s?address=%s&sensor=false" % (output, location)
    rawJSON = urllib.request.urlopen(request)
    response = rawJSON.read()
    data = json.loads(response.decode(), strict = False)
    return_tuple = [0, 0]
    try:
        return_tuple[0] = data["results"][0]["geometry"]["location"]["lat"]
        return_tuple[1] = data["results"][0]["geometry"]["location"]["lng"]
    except BaseException:
        print("Something went wrong...")
        
    rawJSON.close()
    return return_tuple
            
#parses the incoming csv
list = []
with open("/Users/zachwegrzyniak/Desktop/data.csv") as csvfile:
    infoReader = csv.reader(csvfile, delimiter=',', quotechar=' ')

    for row in infoReader:
        column = []
        for item in row:
            column.append(item)
        list.append(column)

#attempts to geocode customers with addresses
codedList = []
for person in list:
    if (float(person[3]) > 0):
        goodAddress = ""
        for i in range (1, 3):
            try:
                goodAddress += " " + person[i]
            except IndexError:
                continue
        goodAddress = goodAddress.strip()
        tempCustomer = customer(person[0], goodAddress)
        tempCustomer.frequency = person[3]
        tempCustomer.cleanTime = person[4]
        if (len(goodAddress) > 0):
            tempCustomer.__geocodeset__()
            codedList.append(tempCustomer)

#writes to current directory the parsed data
with open('geocoded.csv', "w", newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',',
                            quotechar=' ', quoting=csv.QUOTE_MINIMAL)
    for person in codedList:
            writer.writerow([person.name, person.address, person.geocode.lon, person.geocode.lat, person.frequency, person.cleanTime])