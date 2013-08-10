import csv
from nexus import Cluster, Geopoint
from numpy  import *
import scipy.cluster.vq as kmean

class Clusterer:
    '''Plots centroids locations on a static Google Map.'''
    
    def plot_center(centroidList):
        print('\nThe centers of the clusters are located at: \n')
        colors = ['black','purple','blue','red','orange','yellow', 'white']
        URL_prefix = 'http://maps.googleapis.com/maps/api/staticmap?size=640x640&maptype=roadmap\\'
        number = 1
        markers = ''
        for centroid in centroidList:
            if centroid.size > 1:
                form = (number, centroid.center, centroid.size)
                print('{} --> {} has {} points around it.'.format(*form))
                if (len(URL_prefix +  markers) + 15 > 2000):
                    print(''.join([URL_prefix, markers, '&sensor=false']))
                    markers = ''
                markers += '&markers=%7Ccolor:blue%7Clabel:{}%7C{},{}'.format(number, centroid.center.lat, centroid.center.lon)
            number += 1

        final_URL = '{}{}%7C&sensor=false'.format(URL_prefix, markers)
        print('\nThe map of the cluster centers\n{}\n{}\n'.format(final_URL, '_'*37))

    def plotter(raw_file, center):
        if center.lat == 0 and center.lon == 0:
            return 0
        colors = ['black','purple','blue','red','orange','yellow', 'white']
        URL_prefix = 'http://maps.googleapis.com/maps/api/staticmap?size=640x640&maptype=roadmap\\'
        color = colors[5]
        markers = '&markers=%7Ccolor:green%7C{},{}'.format(center.lat, center.lon)

        letter = ord('A')
        for point in raw_file:
            if color != colors[int(point[4]) % (len(colors) - 1)]:
                color = colors[int(point[4]) - 1]

            if (len(URL_prefix +  markers) + 15 > 2000):
                print(URL_prefix + markers + '&sensor=false')
                markers = ''
            form = (color, chr(letter), point[2], point[3])
            markers += '&markers=%7Ccolor:{}%7Clabel:{}%7C{},{}'.format(*form)
            letter += 1

        final_URL = '{}{}%7C&sensor=false'.format(URL_prefix, markers)
        print(final_URL, end='\n\n')

    def scan_clustering(placement):
        for i in range (len(placement)):
            atLeastOne = False
            for j in range (len(placement)):
                if i != j and placement[i] == placement[j]:
                    atLeastOne = True
            if atLeastOne == False:
                return False
        return True

#parses the incoming csv
raw_file = []
with open('cluster.csv') as csvfile:
    infoReader = csv.reader(csvfile, delimiter='|', quoting=csv.QUOTE_NONE)
    for row in infoReader:
        column = []
        for item in row:
            column.append(item.strip())
        raw_file.append(column)

header = raw_file.pop(0) #takes care of header

obs_vector = []
for i in range(len(raw_file)):
    item = raw_file[i]
    name = item[0]
    address = item[1]
    lat = item[2]
    lon = item[3]    
    if lat == '' or lon == '':
        temp = Geopoint(name, address)
        item[2] = temp.lat
        item[3] = temp.lon
    else:
        temp = Geopoint(name, address, lat, lon)
    
    obs_vector.append([temp.lon, temp.lat])

        
print(obs_vector)

matrix = array(obs_vector)

numberOfClusters = 2
lastSolution = []
for i in range (2, int(len(obs_vector)/2)):
    cluster = kmean.kmeans2(matrix, i, iter=1000, minit='random')
    if Clusterer.scan_clustering(cluster[1]):
        numberOfClusters = i
        lastSolution = cluster
        print('Clusters =', i, cluster[1])

center = []

for i in range (0, numberOfClusters):
    center.append(Cluster())

codedList = []
for i in range (len(raw_file)):
    print(lastSolution)
    cluster = lastSolution[1][i]
    raw_file[i][4] = cluster
    clusterNode = center[cluster]
    theCenter = center[cluster].center
    if (theCenter.lat == 0 and theCenter.lon == 0):
        theCenter.lat = lastSolution[0][cluster][1]
        theCenter.lon = lastSolution[0][cluster][0]

    clusterNode.size += 1
    clusterNode.points.append(raw_file[i])

Clusterer.plot_center(center)

cluster_number = 1
for centroid in center:
    if centroid.size > 1:
        form = (cluster_number, centroid.center, centroid.size)
        print('Cluster {} centered at {} size: {}'.format(*form))
        print('A static map of the cluster')
        Clusterer.plotter(centroid.points,centroid.center)
        i = ord('A')
        pointsLined = 'from: Capitol Boise ID'
        for points in centroid.points:
            print('{} is {}, {} | {} | {} |'.format(chr(i), points[0], points[1], header[4], points[4]))
            pointsLined += (' to: ' + points[1])
            i += 1
        pointsLined += ' to: Capitol Boise ID'
        print('\nPaste this into Google Maps for distance info:\n{}\n{}'.format(pointsLined, '_'*43))
    cluster_number += 1
