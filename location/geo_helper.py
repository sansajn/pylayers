# -*- coding: utf-8 -*-
# Helper class for geographic layers.
# \author Adam Hlavatovič
import gps

class layer:
	#@{ Public interface
	def __init__(self, widget, zoom_max = 18):
		self.widget = widget
		self.zoom_max = zoom_max
		
	def center_to_point(self, point_geo, zoom):
		'Bod ocakava ako gps.gpspos.'
		center_xy = gps.mercator.gps2xy(point_geo, zoom)
		self.widget.center_to(center_xy)
	
	def center_to_rect(self, rect_geo, zoom):
		self.center_to_point(rect_geo.center(), zoom)
		
	def zoom_to(self, rect_geo):
		'\note nahradene pomocou layers_manip.zoom'
		w, h = self.widget.window_size()
		zoom = 0
		for zoom in range(0, self.zoom_max):
			sw_xy = gps.mercator.gps2xy(rect_geo.sw(), zoom)
			ne_xy = gps.mercator.gps2xy(rect_geo.ne(), zoom)
			if not self._inside(sw_xy, ne_xy, w, h):
				break
		zoom = max(0, zoom-1)
		self.widget.set_zoom(zoom)
		self.widget.center_to(gps.mercator.gps2xy(rect_geo.center(), zoom))
	#@} Public interface
	
	def _inside(self, a, b, w, h):
		return abs(a[0] - b[0]) <= w and abs(a[1] - b[1]) <= h


class coordinate:

	@staticmethod
	def to_xy_drawable(coord_geo, view_offset, zoom):
		p = coord_geo
		x0,y0 = view_offset
		p_xy = gps.mercator.gps2xy(gps.gpspos(p[0], p[1]), zoom)
		return (p_xy[0]+x0, p_xy[1]+y0)

