# -*- coding: utf-8 -*-
# \author Adam Hlavatovič
import time
from PyQt4 import QtCore, QtGui
import gps, layers, qtree


class layer(layers.layer_interface):
	def __init__(self, widget):
		layers.layer_interface.__init__(self, widget)
		self.forward = ([], None)  # edges, rectange
		self.backward = []
		self.avoids = []
		self.path = []
		self.drawable_fwd = []
		self.drawable_bwd = []
		self.drawable_avoids = []
		self.drawable_path = []
		self.qtree_fwd = None
		
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

		bwd_common = 0  # stats
		for e in backward:
			if e not in path:
				self.backward.append(e)
			else:
				bwd_common += 1
		
		path_common = 0  # stats
		for e in path:
			if e not in avoids:
				self.path.append(e)
			else:
				path_common += 1	
		
		self.avoids = avoids		 
		
	def paint(self, painter):
		t = time.clock()
		
		view_offset = self.widget.view_offset
		self.paint_forward(view_offset, painter)
		self.paint_backward(view_offset, painter)
		self.paint_avoids(view_offset, painter)
		self.paint_path(view_offset, painter)
						
		dt = time.clock() - t
		self.debug('  #edge_layer.paint(): %f s' % (dt, ))

	def zoom_event(self, zoom):
		t = time.clock()

		layers.layer_interface.zoom_event(self, zoom)
		self.prepare_drawable_data()
		
		dt = time.clock() - t
		self.debug('  #edge_layer.zoom_event(): %f s' % (dt, ))

	def mouse_press_event(self, event):
		pass
	#@}
	
	def paint_forward(self, view_offset, painter):
		old_pen = painter.pen()
		old_brush = painter.brush()
		painter.setPen(QtCore.Qt.black)
		for d in self.drawable_fwd:
			d.paint(view_offset, painter)
		painter.setPen(old_pen)
		painter.setBrush(old_brush)
				
	def paint_backward(self, view_offset, painter):
		old_pen = painter.pen()
		old_brush = painter.brush()
		painter.setPen(QtCore.Qt.gray)		
		for d in self.drawable_bwd:
			d.paint(view_offset, painter)
		painter.setPen(old_pen)
		painter.setBrush(old_brush)
		
	def paint_avoids(self, view_offset, painter):
		old_pen = painter.pen()
		old_brush = painter.brush()
		painter.setPen(self.pen_avoids)
		for d in self.drawable_avoids:
			d.paint(view_offset, painter)
		painter.setPen(old_pen)
		painter.setBrush(old_brush)
		
	def paint_path(self, view_offset, painter):
		old_pen = painter.pen()
		old_brush = painter.brush()
		painter.setPen(self.pen_path)
		for d in self.drawable_path:
			d.paint(view_offset, painter)
		painter.setPen(old_pen)
		painter.setBrush(old_brush)

	def prepare_drawable_data(self):	
		# edges
		self.drawable_fwd = to_drawable_edges2(self.forward[0], self.zoom)
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
			
	def fill_qtree_fwd(self, data):		
		gpsr = data[1]
		edges = data[0]
		self.qtree_fwd = qtree.quad_tree(gpsr)
		for e in edges:
			self.qtree_fwd.append(e.p1, e)
			

def to_drawable_edges(edges, zoom):
	forward_drawable = []
	for e in edges:
		s = e[0]
		t = e[1]
		p1_gps = gps.gpspos(s[0]/float(1e5), s[1]/float(1e5))
		p2_gps = gps.gpspos(t[0]/float(1e5), t[1]/float(1e5))
		if p1_gps.is_valid() and p2_gps.is_valid():
			p1 = gps.mercator.gps2xy(p1_gps, zoom)
			p2 = gps.mercator.gps2xy(p2_gps, zoom)		
		forward_drawable.append(edge(p1, p2))
	return forward_drawable

def to_drawable_edges2(edges, zoom):
	drawable_edges = []
	for e in edges:
		s = e[0]
		t = e[1]
		p1 = gps.mercator.gps2xy(s, zoom)
		p2 = gps.mercator.gps2xy(t, zoom)
		drawable_edges.append(edge(p1, p2))
	return drawable_edges


def to_xyrect(gps_rect, zoom):
	pass

def process_raw_edges(edges):
	d = []
	r = QtCore.QRectF(0, 0, 0, 0)
	for e in edges:
		s = e[0]
		t = e[1]
		s_gps = gps.gpspos(s[0]/float(1e5), s[1]/float(1e5))
		t_gps = gps.gpspos(t[0]/float(1e5), t[1]/float(1e5))
		if s_gps.is_valid() and t_gps.is_valid():
			d.append((s_gps, t_gps))
			r.unite(to_rect(s_gps, t_gps))
	return (d, r)
		
def to_rect(s_gps, t_gps):
	x0 = (min(s_gps.lon, t_gps.lon),	min(s_gps.lat, t_gps.lat))
	return QtCore.QRectF(x0[0], x0[1], abs(t_gps.lon - s_gps.lon), 
		abs(t_gps.lat - s_gps.lat))
	

class position:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		
	def __hash__(self):		
		return self.x<<32|self.y
		 

class drawable:
	def paint(self):
		pass
	
class vertex(drawable):
	def __init__(self, xypos):
		self.r = 8
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

