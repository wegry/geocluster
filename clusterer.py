import csv
import scipy.cluster.vq as clusterer
from numpy  import *
import warnings

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

#Plots centroids locations on a static Google Map
def center_plotter(centroidList):
    print("\nThe centers of the clusters are located at: \n")
    colors = ["black","purple","blue","red","orange","yellow", "white"]
    URL_prefix = "http://maps.googleapis.com/maps/api/staticmap?size=640x640&maptype=roadmap\\"
    number = 1
    markers = ""
    for centroid in centroidList:
        if centroid.size > 1:
            print(number, "-->", centroid.center.toString(), "and has", centroid.size, "customers around it.")
            if (len(URL_prefix +  markers) + 15 > 2000):
                print(URL_prefix + markers + "&sensor=false")
                markers = ""
            markers += "&markers=%7Ccolor:blue%7Clabel:" + str(number) + "%7C" + str(centroid.center.lat) + "," + str(centroid.center.lon)
        number += 1

    final_URL = URL_prefix + markers + "%7C&sensor=false"
    print("\nThe map of the cluster centers\n", final_URL, "\n_____________________________________\n", sep = "")

def Plotter(list, center):
    if (center.lat == 0 and center.lon == 0):
        return 0
    colors = ["black","purple","blue","red","orange","yellow", "white"]
    URL_prefix = "http://maps.googleapis.com/maps/api/staticmap?size=640x640&maptype=roadmap\\"
    color = colors[5]
    markers = "&markers=%7Ccolor:green%7C" + str(center.lat) + "," + str(center.lon)

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

def scan_clustering(placement):
    for i in range (0, len(placement)):
        atLeastOne = False
        for j in range (0, len(placement)):
            if i != j and placement[i] == placement[j]:
                atLeastOne = True
        if atLeastOne == False:
            return False
    return True

#parses the incoming csv
list = []
with open("/Users/zachwegrzyniak/Desktop/cluster.csv") as csvfile:
    infoReader = csv.reader(csvfile, delimiter=',', quotechar=' ')

    for row in infoReader:
        column = []
        for item in row:
            column.append(item.strip())
        list.append(column)

header = list.pop(0) #takes care of header

#build 2-dimensional array for kmeans
obs_vector = []
for row in list:
    try:
        obs_vector.append([float(row[3]), float(row[2])])
    except:
        print("something went wrong...You should probably rerun the program.")

matrix = array(obs_vector)

numberOfClusters = 0
lastSolution = []
for i in range (2, int(len(obs_vector)/2)):
    cluster = clusterer.kmeans2(matrix, i, iter = 1000, minit = 'random')
    if (scan_clustering(cluster[1])):
        numberOfClusters = i
        lastSolution = cluster
        print("Clusters =", i, cluster[1])

center = []

for i in range (0, numberOfClusters):
    center.append(Cluster())

codedList = []
for i in range (0, len(list)):
    cluster = lastSolution[1][i]
    list[i][6]= cluster
    clusterNode = center[cluster]
    theCenter = center[cluster].center
    if (theCenter.lat == 0 and theCenter.lon == 0):
        theCenter.lat = lastSolution[0][cluster][0]
        theCenter.lon = lastSolution[0][cluster][1]

    clusterNode.size += 1
    clusterNode.points.append(list[i])

center_plotter(center)

cluster_number = 1
for centroid in center:
    if centroid.size > 1:
        print("Cluster", cluster_number, " ", centroid.center.toString(), "size:", centroid.size)
        print("A static map of the cluster")
        Plotter(centroid.points,centroid.center)
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
