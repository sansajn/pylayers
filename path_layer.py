# -*- coding: utf-8 -*-
# Implementuje vrstvu umožnujúcu zobraziť path_dump súbory.
# \author Adam Hlavatovič
# \version 20120403
import math
from PyQt4 import QtCore, QtGui, QtNetwork
import layers, path_dump

class layer(layers.layer_interface):
	def __init__(self, widget):
		layers.layer_interface.__init__(self, widget)
		self.paths = []

	def read_dump(self, fname):
		reader = path_dump.reader()
		self.paths = reader.read(fname)		

	def paint(self, view_offset, zoom, qp):
		WHITE = (255, 255, 255)
		if len(self.paths) == 0:
			return
		i = 1
		path = self.paths[0]
		u = path[0]
		while i < len(path):
			v = path[i]
			self.draw_edge(view_offset, zoom, self.ap2gp(u), self.ap2gp(v), 
				WHITE, qp)
			self.draw_vertex(view_offset, zoom, self.ap2gp(u), WHITE, qp)
			self.draw_vertex(view_offset, zoom, self.ap2gp(v), WHITE, qp)
			u = v
			i += 1

	def draw_vertex(self, view_offset, zoom, latlon, color, qp):
		x0,y0 = view_offset
		x,y = self.latlon2xy(latlon, zoom)
		x,y = (x-12/2, y-12/2)
		old_brush = qp.brush()
		qp.setBrush(QtGui.QBrush(QtGui.QColor(color[0], color[1], color[2])))
		qp.drawEllipse(x+x0, y+y0, 12, 12)
		qp.setBrush(old_brush)

	def draw_edge(self, view_offset, zoom, f_latlon, t_latlon, color, qp):
		x0,y0 = view_offset
		x_f, y_f = self.latlon2xy(f_latlon, zoom)
		x_t, y_t = self.latlon2xy(t_latlon, zoom)
		qp.drawLine(x_f+x0, y_f+y0, x_t+x0, y_t+y0)

	def latlon2xy(self, gpos, zoom):
		lat,lon = gpos
		n = 2**zoom*256
		lat_rad = math.radians(lat)
		x = int((lon+180.0)/360.0 * n)
		y = int((1.0 - math.log(math.tan(lat_rad)+(1/math.cos(lat_rad)))
			/ math.pi) / 2.0*n)
		return (x, y)

	def ap2gp(self, apos):
		return [apos[0]/1e5, apos[1]/1e5]


