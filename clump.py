import csv

from numpy import *
import scipy.cluster.vq as kmean

from nexus import Cluster, Geopoint



class Clump:

    '''Plot centroid locations on a static Google Map.'''

    def __init__(self):
        self.clusters = []
        self.header = []

    def plot_centers(self, centroid_list):
        print('\nThe centers of the clusters are located at: \n')
        URL_prefix = 'http://maps.googleapis.com/maps/api/staticmap?size=640x640&maptype=roadmap\\'
        number = 1
        markers = ''
        for centroid in centroid_list:
            if centroid.size > 1:
                form = (number, centroid.center, centroid.size)
                print('{} --> {} has {} points around it.'.format(*form))
                if len(URL_prefix + markers) + 15 > 2000:
                    print(''.join([URL_prefix, markers, '&sensor=false']))
                    markers = ''
                form = (number, centroid.center.lat, centroid.center.lon)
                markers += '&markers=%7Ccolor:blue%7Clabel:{}%7C{},{}'.format(*form)
            number += 1

        final_URL = '{}{}%7C&sensor=false'.format(URL_prefix, markers)
        print(
            '\nThe map of the cluster centers\n{}\n{}\n'.format(final_URL, '_' * 37))

    def plotter(self, parsed_file, center):
        if center.lat == 0 and center.lon == 0:
            return 0
        colors = ['black', 'purple', 'green',
                  'red', 'orange', 'yellow', 'white']
        URL_prefix = 'http://maps.googleapis.com/maps/api/staticmap?size=640x640&maptype=roadmap\\'
        color = colors[5]
        markers = '&markers=%7Ccolor:blue%7C{},{}'.format(
            center.lat, center.lon)

        letter = ord('A')
        for point in parsed_file:
            if color != colors[int(point[4]) % (len(colors) - 1)]:
                color = colors[int(point[4]) - 1]

            if (len(URL_prefix + markers) + 15 > 2000):
                print(URL_prefix + markers + '&sensor=false')
                markers = ''
            form = (color, chr(letter), point[2], point[3])
            markers += '&markers=%7Ccolor:{}%7Clabel:{}%7C{},{}'.format(*form)
            letter += 1

        final_URL = '{}{}%7C&sensor=false'.format(URL_prefix, markers)
        print(final_URL, end='\n\n')

    def scan_clustering(self, placement):
        '''Check that there is at least one point in each cluster'''
        for i in range(len(placement)):
            if not placement[i]:
                return False
        return True

    def read_existing_data(self, file_name='cluster.csv'):
        '''Pull in a headered csv and return the header and data'''
        parsed_file = []
        with open(file_name) as csvfile:
            info_reader = csv.reader(
                csvfile, delimiter='|', quoting=csv.QUOTE_NONE)
            for row in info_reader:
                column = []
                for item in row:
                    column.append(item.strip())
                parsed_file.append(column)

        self.header = parsed_file.pop(0)
        return parsed_file

    def write_data(self, data, file_name='cluster.csv'):
        '''Write sorted data out'''
        with open(file_name, 'w') as updated_file:
            data.sort(key=lambda data: data[4])
            writer = csv.writer(updated_file, delimiter='|',
                                quoting=csv.QUOTE_NONE)
            writer.write_row(header)
            for row in data:
                writer.write_row(row)

    def create_observation_vector(self, parsed_file):
        obs_vector = []
        for i in range(len(parsed_file)):
            item = parsed_file[i]
            name = item[0]
            address = item[1]
            lat = item[2]
            lon = item[3]
            if not lat or not lon:
                temp = Geopoint(name, address)
                item[2] = temp.lat
                item[3] = temp.lon
            else:
                temp = Geopoint(name, address, lat, lon)

            obs_vector.append([temp.lon, temp.lat])

        return obs_vector

    def perform_clustering(self, observation):
        print(observation)
        matrix = array(observation)
        last_solution = None
        for i in range(2, len(observation) // 2):
            cluster = kmean.kmeans2(matrix, i, iter=1000, minit='random')
            if self.scan_clustering(cluster[1]):
                last_solution = cluster
                print('Clusters =', i, cluster[1])

        if not last_solution:
            print('Rerun the program, this sort of thing takes time.')
            exit(1)  # change this
        print(last_solution)
        return last_solution

    def initialize_clusters(self, last_solution, parsed_file):

        for i in range(0, max(last_solution[1])):
            self.clusters.append(Cluster())
        codedList = []
        for i in range(len(parsed_file)):
            cluster = last_solution[1][i]
            parsed_file[i][4] = cluster
            clusterNode = self.clusters[cluster]
            theCenter = self.clusters[cluster].center
            if (theCenter.lat == 0 and theCenter.lon == 0):
                theCenter.lat = last_solution[0][cluster][1]
                theCenter.lon = last_solution[0][cluster][0]

            clusterNode.points.append(parsed_file[i])

    def __str__(self):
        cluster_number = 1
        for centroid in self.clusters:
            form = (cluster_number, centroid.center, centroid.size)
            print('Cluster {} centered at {} size: {}'.format(*form))
            print('A static map of the cluster')
            Clump.plotter(centroid.points, centroid.center)
            i = ord('A')
            pointsLined = 'from: Capitol Boise ID'
            for points in centroid.points:
                print('{} is {}, {}'.format(chr(i), points[0], points[1]))
                pointsLined += (' to: ' + points[1])
                i += 1
            pointsLined += ' to: Capitol Boise ID'
            print('\nPaste this into Google Maps for distance info:\n{}\n{}'.format(
                pointsLined, '_' * 43))
            cluster_number += 1


if __name__ == '__main__':
    test = Clump()
    data = test.read_existing_data()
    obs_vector = test.create_observation_vector(data)
    clustered = test.perform_clustering(obs_vector)