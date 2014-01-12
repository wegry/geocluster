from math import atan2, cos, radians, sin, sqrt
import requests

class Cluster:
	def __init__(self, center, points, letter='A'):
		self.center = center
		self.points = points
		self.number = letter

	def __str__(self):
		point_list = '\n'.split([point for point in self.points])
		form = (self.letter, self.center, point_list)
		return 'Cluster {} is centered at {} with the following points associated:\n{}'.format(*form)

class Point:
	"Has latitude and lonitude attributes"
	def __init__(self, lat=0, lon=0, *args):
		self.lat = lat
		self.lon = lon

	def distance_between(self, other_point):
		'''Haversine function from http://www.movable-type.co.uk/scripts/gis-faq-5.1.html'''
		dlat = radians(self.lat - other_point.lat)
		dlon = radians(self.lon - other_point.lon)

		R = 3963.1676  #Radius of the earth in miles

		a = sin(dlat/2)**2 + cos(radians(self.lat))*cos(radians(other_point.lat))*(sin(dlon/2)**2)
		c = 2 * atan2(sqrt(a), sqrt(1 - a))
		return R * c

	def is_uninitialized(self):
		'''Make sure one of the coordinates is non-zero. There's only open
		place it won't work...'''
		return self.lat and self.lon

	def __str__(self):
		return '({}, {})'.format(self.lat, self.lon)


class Geopoint(Point):
	'''Geopoints have names and addresses as well as geocoded points'''
	def __init__(self, name, address, lat=0, lon=0):
		self.name = name
		self.address = address.replace(',', '')
		if self.is_uninitialized:
			self.geocodeset()

	def geocodeset(self):
		'''Change default lat lon to actual address(hopefully)'''
		if self.address:
			plussed_address = self.address.replace(' ', '+')
			new_point = self.get_lat_lon(plussed_address)
			self.geocode = Point(*new_point)

	def get_lat_lon(self, location):
		output = 'json'
		base_url = 'http://maps.google.com/maps/api/geocode/{}?address={}&sensor=false'
		request = base_url.format(output, location)
		raw_json = requests.get(request)
		data = raw_json.json()

		try:
			location = data['results'][0]['geometry']['location']
			return (location['lat'], location['lng'])
		except Exception as e:
			print('Something went wrong...{}'.format(e))

		return (0, 0)

	def __str__(self):
		'''Override of the default. Returns a string representation of the 
		Geopoint.'''
		raw_rep = '{} {} {}'.format(self.name, self.address, self.geocode)
		return raw_rep.title()

if __name__ == '__main__':
	print(Geopoint('Boise Capitol', 'Capitol Boise ID'))