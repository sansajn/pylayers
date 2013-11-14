# -*- coding: utf-8 -*-
# \author Adam Hlavatovič
import math

class signed_position:
	def __init__(self, lat, lon):
		self.lat = lat
		self.lon = lon

class gpspos:
	def __init__(self, lat, lon):
		self.lat = lat
		self.lon = lon

	def is_valid(self):
		return self.lat >= -180.0 and self.lat <= 180.0 and \
			self.lon >= -180.0 and self.lon <= 180.0

	def __eq__(self, b):
		return self.lat == b.lat and self.lon == b.lon

	def __hash__(self):
		a=int(self.lon*1e5); b=int(self.lat*1e5)
		return b<<32|a
	
	def __getitem__(self, key):
		if key == 0:
			return self.lat
		elif key == 1:
			return self.lon
		else:
			raise Exception('index overflow only 0 or 1 supported')

class georect:
	'''Georect je o 90deg otoceny stvorec v porovnani s vyznamom 
	transformacie bodu na guly (lat, lon) na plochu.'''
	def __init__(self, sw, ne):
		'Expressions sw.lat, sw.lon must be valid (same for ne).'
		self.sw = sw
		self.ne = ne

	def width(self):
		return abs(self.ne.lat - self.sw.lat)

	def height(self):
		return abs(self.ne.lon - self.sw.lon)
	
	def x(self):
		return self.sw.lat
	
	def y(self):
		return self.ne.lon

	def center(self):
		return gpspos(
			self.sw.lat+self.width()/2, self.sw.lon+self.height()/2)

	def contains(self, lat, lon):
		sw, ne = (self.sw, self.ne)
		return lat >= sw.lat and lat <= ne.lat and lon >= sw.lon	\
			and lon <= ne.lon

			
class mercator:
	r'''\note Pri zmene levelu nie je potrebné znova počítať xy súradnice, stačí
	ich vynásobiť koeficientom 2^(zoom_diff), kde zoom_dif je zmena levelu.'''

	@staticmethod
	def gps2xy(gpos, zoom):
		r'\param gpos gpspos(lat, lon)'
		lat,lon = (gpos.lat, gpos.lon)
		n = 2**zoom*256
		lat_rad = math.radians(lat)
		x = int((lon+180.0)/360.0 * n)
		y = int((1.0 - math.log(math.tan(lat_rad)+(1/math.cos(lat_rad)))
			/ math.pi) / 2.0*n)
		return (x, y)

	@staticmethod
	def xy2gps(xypos, zoom):
		r'\param xypos (x,y)'
		x,y = xypos
		n = 2.0**zoom*256
		lon_deg = x/n*360.0 - 180.0
		lat_rad = math.atan(math.sinh(math.pi * (1 - 2*y/n)))
		lat_deg = math.degrees(lat_rad)
		return gpspos(lat_deg, lon_deg)

