# -*- coding: utf-8 -*-
# \author Adam Hlavatovič
# pri zoome je treba urcit, ktore primitivy sa oplati vykreslovat 

import time
from PyQt4 import QtCore, QtGui
import gps, layers, geo_helper, geometry


class layer(layers.layer_interface):
	def __init__(self, widget):
		layers.layer_interface.__init__(self)
		self.zoom = None
		self.widget = widget
		
		# data
		self.forward = []
		self.backward = []
		self.avoids = []
		self.path = []
		
		# drawable
		self.drawable_fwd = []
		self.drawable_bwd = []
		self.drawable_avoids = []
		self.drawable_path = []
				
		pen = QtGui.QPen()
		pen.setColor(QtCore.Qt.red)
		pen.setWidth(3)
		self.pen_avoids = pen
		
		pen = QtGui.QPen()
		pen.setColor(QtCore.Qt.blue)
		pen.setWidth(3)
		self.pen_path = pen

	#@{ layer_interface implementation
	def create(self, edge_fname):
		loc = {}
		glob = {}
		execfile(edge_fname, glob, loc)
		forward = loc['forward']
		backward = loc['backward']		
		avoids = loc['avoids']
		path = loc['path']

		self.forward = process_raw_edges([e for e in forward if e not in path])
		self.backward = process_raw_edges([e for e in backward if e not in path])
		self.path = process_raw_edges([e for e in path if e not in avoids])
		self.avoids = process_raw_edges([e for e in avoids])
		
		rect = self.forward[1]
		rect.unite(self.backward[1])
		rect.unite(self.path[1])
		rect.unite(self.avoids[1])		
		geo_helper.layer(self.window).zoom_to(rect) 
		
	def paint(self, painter, view_offset):
		t = time.clock()
		
		old_pen = painter.pen()
		
		painter.setPen(QtCore.Qt.black)
		self.paint_edges(self.drawable_fwd, view_offset, painter, 'forward')
		
		painter.setPen(QtCore.Qt.gray)
		self.paint_edges(self.drawable_bwd, view_offset, painter, 'backward')
		
		painter.setPen(self.pen_avoids)
		self.paint_edges(self.drawable_avoids, view_offset, painter, 'avoids')
		
		painter.setPen(self.pen_path)
		self.paint_edges(self.drawable_path, view_offset, painter, 'path')
		
		painter.setPen(old_pen)
						
		dt = time.clock() - t
		self.debug('  #edge_layer.paint(): %f s' % (dt, ))
		
	def zoom_event(self, zoom):
		self.zoom = zoom
		t = time.clock()

		layers.layer_interface.zoom_event(self, zoom)
		self.prepare_drawable_data()
		
		dt = time.clock() - t
		self.debug('  #edge_layer.zoom_event(): %f s' % (dt, ))

	def mouse_press_event(self, event):
		pass
	#@}
	
	def paint_edges(self, drawable, view_offset, painter,	string_id = ''):		
		for e in drawable:
			e.paint(view_offset, painter)			
		self.debug('  #paint_edges: painted %d/%d %s edges' % (
			len(drawable), len(drawable), string_id))
	
	def prepare_drawable_data(self):	
		# edges
		self.drawable_fwd = to_drawable_edges(self.forward, self.zoom)
		self.drawable_bwd = to_drawable_edges(self.backward, self.zoom)
		self.drawable_avoids = to_drawable_edges(self.avoids, self.zoom)
		self.drawable_path = to_drawable_edges(self.path, self.zoom)
		
		# vertices
		#verts = []
		#for e in self.drawable:
		#	verts.append((e.p1.x(), e.p1.y()))
		#	verts.append((e.p2.x(), e.p2.y()))	
		#verts_drawable = [vertex(v) for v in verts]		
		#self.drawable.extend(verts_drawable)
				
	def view_geo_rect(self, view_offset, zoom):
		'Vrati geo-rect vyditelnej obrazovky.'
		w,h = self.widget.window_size()
		x0,y0 = view_offset
		xa,ya = (abs(x0), abs(y0)+h)
		sw = gps.mercator.xy2gps((xa, ya), zoom)
		ne = gps.mercator.xy2gps((xa+w, ya-h), zoom)
		return QtCore.QRectF(sw[0], sw[1], ne[0]-sw[0], ne[1]-sw[1])
		
			
def to_drawable_edges(edges, zoom):
	drawable_edges = []
	for e in edges:
		p1 = gps.mercator.gps2xy(e[0], zoom)
		p2 = gps.mercator.gps2xy(e[1], zoom)
		drawable_edges.append(edge(p1, p2))
	return drawable_edges

def process_raw_edges(edges):
	'Vrati zoznam hran a najmensi stvorec obsahujuci vsetky hrany.'
	d = []
	r = geometry.rectangle((0,0), (0,0))
	for e in edges:
		s = e[0]
		t = e[1]
		s_gps = gps.gpspos(s[0]/float(1e5), s[1]/float(1e5))
		t_gps = gps.gpspos(t[0]/float(1e5), t[1]/float(1e5))
		if s_gps.is_valid() and t_gps.is_valid():			
			d.append((s_gps, t_gps))
			r.unite(geometry.rectangle(s_gps, t_gps))
	return (d, r)

def to_rect(s_gps, t_gps):
	x0 = (min(s_gps.lat, t_gps.lat), min(s_gps.lon, t_gps.lon))
	r = QtCore.QRectF(x0[0], x0[1], abs(t_gps.lat - s_gps.lat), 
		abs(t_gps.lon - s_gps.lon))
	return r
	

class drawable:
	def paint(self):
		pass
	
class vertex(drawable):
	def __init__(self, xypos):
		self.r = 8
		self.xypos = None
		self.set_position(xypos)
	
	def set_position(self, xypos):
		self.xypos = QtCore.QPoint(xypos[0], xypos[1])
	
	#@{ drawable interface implementation
	def paint(self, view_offset, painter):
		x0,y0 = view_offset
		painter.drawEllipse(self.xypos.x()+x0, self.xypos.y()+y0, self.r, self.r)		
	#@}
	
class edge(drawable):
	def __init__(self, p1, p2):
		self.set_position(p1, p2)
		
	def set_position(self, p1, p2):
		self.p1 = QtCore.QPoint(p1[0], p1[1])
		self.p2 = QtCore.QPoint(p2[0], p2[1])
			
	#@{ drawable interface implementation
	def paint(self, view_offset, painter):
		x0,y0 = view_offset
		painter.drawLine(self.p1.x()+x0, self.p1.y()+y0, self.p2.x()+x0,
			self.p2.y()+y0)
	#@}

