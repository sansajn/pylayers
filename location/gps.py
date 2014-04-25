# -*- coding: utf-8 -*-
__author__ = 'Adam Hlavatovič'

import math
import geometry

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


class georect(geometry.rectangle):

	def sw(self):
		return self.a

	def ne(self):
		return self.b


# class georect:
# 	'''Georect je o 90deg otoceny stvorec v porovnani s vyznamom
# 	transformacie bodu na guly (lat, lon) na plochu.'''
#
# 	def __init__(self, sw, ne):
# 		'Expressions sw.lat, sw.lon must be valid (same for ne).'
# 		self.sw = sw
# 		self.ne = ne
#
# 	def width(self):
# 		return abs(self.ne.lat - self.sw.lat)
#
# 	def height(self):
# 		return abs(self.ne.lon - self.sw.lon)
#
# 	def x(self):
# 		return self.sw.lat
#
# 	def y(self):
# 		return self.ne.lon
#
# 	def center(self):
# 		return gpspos(
# 			self.sw.lat+self.width()/2, self.sw.lon+self.height()/2)
#
# 	def contains(self, lat, lon):
# 		sw, ne = (self.sw, self.ne)
# 		return lat >= sw.lat and lat <= ne.lat and lon >= sw.lon	\
# 			and lon <= ne.lon


class mercator:

	@staticmethod
	def gps2xy(gpos, zoom):
		'\param gpos is a point type'
		lat,lon = (gpos[0], gpos[1])
		lat_rad = math.radians(lat)
		x = (lon+180.0)/360.0
		y = (1.0 - math.log(math.tan(lat_rad)+(1/math.cos(lat_rad)))
			/ math.pi) / 2.0
		n = 2**zoom*256
		return (int(n*x), int(n*y))

	@staticmethod
	def xy2gps(xypos, zoom):
		'\param xypos is a point type'
		x,y = (xypos[0], xypos[1])
		n = 2.0**zoom*256
		lon_deg = x/n*360.0 - 180.0
		lat_rad = math.atan(math.sinh(math.pi * (1 - 2*y/n)))
		lat_deg = math.degrees(lat_rad)
		return gpspos(lat_deg, lon_deg)

	@staticmethod
	def gps2xybase(gpos):
		'\param gpos is a point type'
		lat,lon = (gpos[0], gpos[1])
		lat_rad = math.radians(lat)
		x = (lon+180.0)/360.0
		y = (1.0 - math.log(math.tan(lat_rad)+(1/math.cos(lat_rad)))
			/ math.pi) / 2.0
		return (x, y)

	@staticmethod
	def apply_zoom(gbasepos, zoom):
		n = mercator.zoom_scale(zoom)
		return (int(n*gbasepos[0]), int(n*gbasepos[1]))

	@staticmethod
	def xy2xybase(xypos, zoom):
		scale = float(mercator.zoom_scale(zoom))
		return (xypos[0]/scale, xypos[1]/scale)

	@staticmethod
	def zoom_scale(zoom):
		return 2**zoom*256

