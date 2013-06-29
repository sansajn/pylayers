# -*- coding: utf-8 -*-
# \author Adam Hlavatovič
import time
from PyQt4 import QtCore, QtGui
import layer_interface, gps


class layer(layer_interface.layer):
	def __init__(self, widget):
		layer_interface.layer.__init__(self)
		self.zoom = None
		self.widget = widget
		self.forward = ([], None)  # edges, rectange
		self.drawable_fwd = []

	#@{ layer_interface implementation
	def create(self, edge_fname):
		loc, glob = {}, {}
		execfile(edge_fname, glob, loc)		
		
		forward = []
		if 'forward' in loc:
			forward = loc['forward']
			
		self.forward = process_raw_edges([e for e in forward])
		
	def paint(self, painter, view_offset):
		painter.setPen(QtCore.Qt.black)
		for d in self.drawable_fwd:
			d.paint(view_offset, painter)

	def zoom_event(self, zoom):
		self.zoom = zoom
		self.prepare_drawable_data()
	#@}
	
	def prepare_drawable_data(self):
		self.drawable_fwd = to_drawable_edges(self.forward[0], self.zoom)
			
			
def to_drawable_edges(edges, zoom):
	drawable_edges = []	
	for e in edges:
		s = e[0]
		t = e[1]
		p1 = gps.mercator.gps2xy(s, zoom)
		p2 = gps.mercator.gps2xy(t, zoom)
		drawable_edges.append(edge(p1, p2))
	return drawable_edges


def process_raw_edges(edges):
	d = []
	r = QtCore.QRectF(0, 0, 0, 0)
	for e in edges:
		s = e[0]
		t = e[1]
		cost = e[2]
		s_gps = gps.gpspos(s[0]/float(1e5), s[1]/float(1e5))
		t_gps = gps.gpspos(t[0]/float(1e5), t[1]/float(1e5))
		if s_gps.is_valid() and t_gps.is_valid():
			d.append((s_gps, t_gps, cost))
			r = r.unite(to_rect(s_gps, t_gps))
		else:
			print('edge ignored')
	# zvecsim ju o 10%, aby do nej padli vsetky body
	r.adjust(-r.width()/20.0, -r.height()/20.0, r.width()/20.0, r.height()/20.0)
	return (d, r)
		
def to_rect(s_gps, t_gps):
	x0 = (min(s_gps.lat, t_gps.lat), min(s_gps.lon, t_gps.lon))
	r = QtCore.QRectF(x0[0], x0[1], abs(t_gps.lat - s_gps.lat), 
		abs(t_gps.lon - s_gps.lon))
	return r
	

class edge:
	def __init__(self, p1, p2):
		self.set_position(p1, p2)
		
	def set_position(self, p1, p2):
		self.p1 = QtCore.QPoint(p1[0], p1[1])
		self.p2 = QtCore.QPoint(p2[0], p2[1])
			
	#@{ drawable interface implementation
	def paint(self, view_offset, painter):
		x0,y0 = view_offset
		s = (self.p1.x()+x0, self.p1.y()+y0)
		t = (self.p2.x()+x0, self.p2.y()+y0)
		painter.drawLine(s[0], s[1], t[0], t[1])
		painter.drawEllipse(QtCore.QPointF(s[0], s[1]), 2, 2)
		painter.drawEllipse(QtCore.QPointF(t[0], t[1]), 2, 2)
	#@}
