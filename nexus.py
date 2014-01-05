from math import atan2, cos, radians, sin, sqrt
import requests

class Cluster:
	def __init__(self):
		self.size = 0
		self.center = Point(0, 0)
		self.points = []

#geopoints have names and addresses as well as geocoded points
class Geopoint:
	'''Stuff'''
	def __init__(self, name, address, lat = 0, lon = 0, cluster = 0):
		self.name = name
		self.address = address.replace(',', '')
		self.lat = float(lat)
		self.lon = float(lon)
		self.cluster = cluster
		if lat == 0 and lon == 0:
			self.geocodeset()

	def distance_between(self, other_point):
		'''Haversine function from http://www.movable-type.co.uk/scripts/gis-faq-5.1.html'''
		dlat = radians(self.lat - other_point.lat)
		dlon = radians(self.lon - other_point.lon)

		R = 3963.1676  #Radius of the earth in miles

		#a = sin^2(dlat/2) + cos(lat1) * cos(lat2) * sin^2(dlon/2)
		a = sin(dlat/2)**2 + cos(radians(self.lat))*cos(radians(other_point.lat))*(sin(dlon/2)**2)
		#c = 2 * arcsin(min(1,sqrt(a)))
		c = 2 * atan2(sqrt(a), sqrt(1 - a))
		#d = R * c
		return R * c

	def geocodeset(self):
		'''Change default lat lon to actual address(hopefully)'''
		if len(self.address) > 0:
			plussedAddress = self.address.replace(' ', '+')
			returnPoint = self.get_lat_lon(plussedAddress)
			self.lat = returnPoint[0]
			self.lon =  returnPoint[1]

	def get_lat_lon(self, location):
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

	def __str__(self):
		'''Override of the default. Returns a string representation of the 
		Geopoint.'''
		raw_rep = '{} {} {}, {}'.format(self.name, self.address, self.lat, self.lon)
		return raw_rep.title()

class Point:
	"Has latitude and lonitude attributes"
	def __init__(self, lat, lon):
		self.lat = lat
		self.lon = lon

	def __str__(self):
		return "(" + str(self.lat) + ", " + str(self.lon) + ")"