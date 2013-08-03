import csv
import webbrowser

class Cluster:
    def __init__(self):
        self.size = 0
        self.center = Point(0, 0)
        self.points = []

class Point:
    "Has latitude and longitude attributes"
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def toString(self):
        return "(" + str(self.lat) + ", " + str(self.lon) + ")"

def Plotter(list):
    colors = ["black","purple","blue","red","orange","yellow", "white"]
    URL_prefix = "http://maps.googleapis.com/maps/api/staticmap?size=640x640&maptype=roadmap\\"
    color = colors[5]
    markers = ""
    letter = ord("A")
    for person in list:
        if color != colors[int(person[6]) % (len(colors) - 1)]:
            color = colors[int(person[6]) - 1]
 #           markers += "&markers=%7Ccolor:" + color

        if (len(URL_prefix +  markers) + 15 > 2000):
            print(URL_prefix + markers + "&sensor=false")
            markers = ""
        markers += "&markers=%7Ccolor:" + color + "%7Clabel:" + chr(letter) + "%7C" + person[3] + "," + person[2]
        letter += 1

    final_URL = URL_prefix + markers + "%7C&sensor=false"
    print(final_URL, "\n", sep = "")

list = []
with open ("cluster.csv") as csvfile:
    infoReader = csv.reader(csvfile, delimiter=',', quotechar=' ')

    for row in infoReader:
        column = []
        for item in row:
            column.append(item)
        list.append(column)

header = list.pop(0) #takes care of header

numberOfClusters = 0
if len(list) > 1:
    numberOfClusters = int(list[len(list) - 1][6])

else:
    print("There aren't enough points...")
    quit()

center = []

for i in range (0, numberOfClusters):
    center.append(Cluster())

codedList = []
for i in range (0, len(list)):
    cluster = int(list[i][6]) - 1
    clusterNode = center[cluster]
    theCenter = center[cluster].center
    clusterNode.size += 1
    clusterNode.points.append(list[i])

cluster_number = 1
print()
for centroid in center:
    if centroid.size > 1:
        print("Cluster", cluster_number)
        print("A static map of the cluster\n")
        Plotter(centroid.points)
        i = ord("A")
        pointsLined = "from: 1516 S Colorado Ave, Boise, ID"
        for points in centroid.points:
            print(chr(i), "is", points[0], points[1], "|", header[4], points[4], "|", header[5], points[5])
            pointsLined += (" to: " + points[1])
            i += 1
        pointsLined += " to: 1516 S Colorado Ave, Boise, ID"
        print("\nPaste this into Google Maps for distance info:\n" + pointsLined)
        print("___________________________________________\n")
    cluster_number += 1
