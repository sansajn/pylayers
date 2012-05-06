# -*- coding: utf-8 -*-
# \author Adam Hlavatovič
import math

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


class mercator:
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

