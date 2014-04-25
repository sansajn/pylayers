# -*- coding: utf-8 -*-
# Some basic layers manipulation routines.
__author__ = 'Adam Hlavatovič'

import gps

class zoom:
	def __init__(self, widget):
		self._zoom_max = 18
		self._widget = widget

	def to_georect(self, r):
		'r je typu gps.georect'
		w, h = self._widget.window_size()
		z = 0  # zoom
		for z in range(0, self._zoom_max):
			sw_xy = gps.mercator.gps2xy(r.sw(), z)
			ne_xy = gps.mercator.gps2xy(r.ne(), z)
			if not self._inside(sw_xy, ne_xy, w, h):
				break
		z = max(0, z-1)
		self.widget.set_zoom(z)
		self.widget.center_to(gps.mercator.gps2xy(r.center(), z))

	def to_baserect(self, r):
		'r je typu geometry.rectangle'
		w, h = self._widget.window_size()
		z = 0
		for z in range(0, self._zoom_max):
			sw = gps.mercator.apply_zoom(r.a, z)
			ne = gps.mercator.apply_zoom(r.b, z)
			if not self._inside(sw, ne, w, h):
				break
		z = max(0, z-1)
		self._widget.set_zoom(z)
		self._widget.center_to(gps.mercator.apply_zoom(r.center(), z))

	def _inside(self, a, b, w, h):
		return abs(a[0] - b[0]) <= w and abs(a[1] - b[1]) <= h


class window_coordinate:
	'\note malo by to ist do geo-helperu'
	def __init__(self, widget):
		self._widget = widget

	def from_xybase(self, xybase_pos, layer_zoom):
		p_xy = gps.mercator.apply_zoom(xybase_pos, layer_zoom)
		return window_coordinate.from_view_offset(self._widget.view_offset, p_xy)

	def from_geo(self, geo_pos, layer_zoom):
		p_xy = gps.mercator.gps2xy(geo_pos, layer_zoom)
		return window_coordinate.from_view_offset(self._widget.view_offset, p_xy)

	@staticmethod
	def from_view_offset(view_offset, local_pos):
		return (view_offset[0]+local_pos[0], view_offset[1]+local_pos[1])


class world_coordinate:
	def __init__(self, widget):
		self._widget = widget

	def from_window(self, window_pos):
		return self._widget.to_world_coordinate(window_pos)
