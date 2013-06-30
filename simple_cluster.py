# -*- coding: utf-8 -*-
# \author Adam Hlavatovič
import time
from PyQt4 import QtCore, QtGui
import layer_interface, gps, qtree, geometry


class layer(layer_interface.layer):
	def __init__(self, widget):
		layer_interface.layer.__init__(self)
		self.zoom = None
		self.widget = widget
		self.forward = ([], None)  # edges, rectangle
		self.drawable_fwd = []

	#@{ layer_interface implementation
	def create(self, edge_fname):
		loc, glob = {}, {}
		execfile(edge_fname, glob, loc)		
		
		forward = []
		if 'forward' in loc:
			forward = loc['forward']
			
		self.forward = process_raw_edges(forward)
		
	def paint(self, painter, view_offset):
		painter.setPen(QtCore.Qt.black)
		
		t = time.clock()
		
		view_bounds = self.view_geo_rect(view_offset, self.zoom) 
		leafs = self.edges.leafs(view_bounds)
		
		nleafs = 0
		nedges = 0
		
		for leaf in leafs:
			bounds = leaf.bounds()
			if self.too_small(bounds, self.zoom):
				self.paint_cluster(bounds, self.zoom, view_offset, painter)
				nleafs += 1
			else:
				drawable = leaf.data()
				if view_bounds.subset(leaf.bounds()):
					for d in drawable:
						d[1].paint(view_offset, painter)
						nedges += 1
				else:
					for d in drawable:
						if view_bounds.contains(d[0]):
							d[1].paint(view_offset, painter)
							nedges += 1
			
		dt = time.clock() - t
		self.debug('  #lookup-v-strome: %f s (edges:%d, leafs:%d)' % (
			dt, nedges, nleafs))

	def valid_point(self, gps):
		return gps[0] >= -180 and gps[0] <= 180 and gps[1] >= -180 and gps[1] <= 180 

	def too_small(self, bounds, zoom):
		a_xy = gps.mercator.gps2xy(gps.gpspos(bounds.a[1], bounds.a[0]), zoom)
		b_xy = gps.mercator.gps2xy(gps.gpspos(bounds.b[1], bounds.b[0]), zoom)
		w = abs(b_xy[0] - a_xy[0])
		h = abs(b_xy[1] - a_xy[1])
		return w < 10 or h < 10
	
	def paint_cluster(self, bounds, zoom, view_offset, painter):
		painter.setPen(QtCore.Qt.red)
		x0,y0 = view_offset
		p = gps.gpspos(
			bounds.a[0] + bounds.width()/2.0, bounds.a[1] + bounds.height()/2.0)
		p_xy = gps.mercator.gps2xy(p, zoom)
		painter.drawEllipse(QtCore.QPointF(x0+p_xy[0], y0+p_xy[1]), 4, 4)
		painter.setPen(QtCore.Qt.black)

	def zoom_event(self, zoom):
		self.zoom = zoom
		self.prepare_drawable_data()
	#@}
	
	def prepare_drawable_data(self):
		t = time.clock()
		
		# vytvor strom
		edges = qtree.qtree(self.forward[1])
		for e in self.forward[0]:
			s = e[0]
			edges.insert(s, to_drawable_edge(e, self.zoom))
		self.edges = edges

		dt = time.clock() - t
		self.debug('  #vytvorenie-stromu: %f s (%d hran)' % (dt, edges._size))
		
	def view_geo_rect(self, view_offset, zoom):
		w,h = self.widget.window_size()
		x0,y0 = view_offset
		xa,ya = (abs(x0), abs(y0)+h)
		sw = gps.mercator.xy2gps((xa, ya), zoom)
		ne = gps.mercator.xy2gps((xa+w, ya-h), zoom)
		return geometry.rectangle(sw, ne)
			
			
def to_drawable_edges(edges, zoom):
	drawable_edges = []	
	for e in edges:
		drawable_edges.append(to_drawable_edge(e, zoom))
	return drawable_edges

def to_drawable_edge(e, zoom):
	s = e[0]
	t = e[1]
	p1 = gps.mercator.gps2xy(s, zoom)
	p2 = gps.mercator.gps2xy(t, zoom)
	return edge(p1, p2)


def process_raw_edges(edges):
	d = []		
	r = to_gps_rect(edges[0][0], edges[0][1])
	for e in edges:
		s = e[0]
		t = e[1]
		cost = e[2]
		s_gps = gps.gpspos(s[0]/float(1e5), s[1]/float(1e5))
		t_gps = gps.gpspos(t[0]/float(1e5), t[1]/float(1e5))
		if s_gps.is_valid() and t_gps.is_valid():
			d.append((s_gps, t_gps, cost))
			r.expand(s_gps)
			r.expand(t_gps)
		else:
			print('edge ignored')
	return (d, r)
		
def to_gps_rect(a, b):
	a = (a[0]/float(1e5), a[1]/float(1e5))
	b = (b[0]/float(1e5), b[1]/float(1e5))	
	return geometry.rectangle(a, b)
	
	
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
