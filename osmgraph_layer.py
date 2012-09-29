# -*- coding: utf-8 -*-
# Zobrazuje graf vygenerovaný programom 'osm/graph/graph_generator'.
# \author Adam Hlavatovič
import sys, math, time, random
from PyQt4 import QtCore, QtGui
import layers, gps, qtree, osmgraph_file, osmgraph_graph, dijkstra


class layer(layers.layer_interface):
	def __init__(self, parent):
		layers.layer_interface.__init__(self, parent)
		self.parent = parent
		self.gfile = None
		self.graph = None
		self.drawable = []
		self.path = []
		self.drawable_path = []
		self.sample_compute = True
		self.vertex_qtree = None

	#@{ layer-interface
	def create(self, graph_fname):
		self.gfile = osmgraph_file.graph_file(graph_fname)
		self.graph = osmgraph_graph.graph(self.gfile)

		layer = self.parent.get_layer('map')
		if layer:
			layer.zoom_to(self._graph_gps_bounds())

		bounds = self._graph_bounds()
		self.vertex_qtree = qtree.quad_tree(
			QtCore.QRectF(bounds.x(), bounds.y(), bounds.width(), 
				bounds.height()))
		fill_vertex_qtree(self.graph, self.vertex_qtree)


	def paint(self, painter, view_offset):
		# graph
		for d in self.drawable:
			d.paint(painter, view_offset)
		# path
		for d in self.drawable_path:
			painter.setPen(QtGui.QColor(218, 0, 0))
			d.paint(painter, view_offset)

	def zoom_event(self, zoom):
		self.zoom = zoom

		if self.sample_compute and False:
			# compute sample route
			graph_header = self.gfile.read_header()
			s = 4032 #random.randint(0, graph_header['vertices'])
			t,distance = self._trace_vertex(s)

			tm = time.clock()
			search_algo = dijkstra.dijkstra(self.graph)
			self.path = search_algo.search(s, t)
			dt = time.clock() - tm
			print 'search takes: %f s (%d -> %d : %d)' % (dt, s, t, distance)
			
			tm = time.clock()
			path = search_algo.search(t, s)
			dt = time.clock() - tm
			print 'search takes: %f s (%d -> %d : %d)' % (dt, t, s, distance)

			self.sample_compute = False

		t = time.clock()
		self._prepare_drawable_data()
		dt = time.clock() - t

		self.debug('  #osmgraph_layer.zoom_event(): %f s' % (dt, ))

	#@} layer-interface

	def _prepare_drawable_data(self):
		g = self.graph
		for v in g.vertices():
			vprop = g.vertex_property(v)
			for e in g.adjacent_edges(v):
				w = g.target(e)
				wprop = g.vertex_property(w)
				self.drawable.append(to_drawable_edge(vprop, wprop, self.zoom))

		# drawable_path
		path = self.path
		if len(path) > 1:
			for i in range(0, len(path)-1):
				vprop = self.graph.vertex_property(path[i])
				wprop = self.graph.vertex_property(path[i+1])
				self.drawable_path.append(to_drawable_edge(vprop, wprop, 
					self.zoom))

			print 'path length: %d' % (len(path), )

	def _trace_vertex(self, v):
		g = self.graph
		distance = 0
		while True:
			edges = g.adjacent_edges(v)
			if len(edges) == 0:
				break
			v = g.target(edges[random.randint(0, len(edges)-1)])
			distance += 1
		return (v, distance)
			
	def _graph_bounds(self):
		graph_header = self.gfile.read_header()
		bounds = graph_header['bounds']
		sw = gps.signed_position(bounds[0][0], bounds[0][1])
		ne = gps.signed_position(bounds[1][0], bounds[1][1])
		return gps.georect(sw, ne)

	def _graph_gps_bounds(self):
		b = self._graph_bounds()
		sw = gps.gpspos(b.sw.lat/float(1e7), b.sw.lon/float(1e7))
		ne = gps.gpspos(b.ne.lat/float(1e7), b.ne.lon/float(1e7))
		return gps.georect(sw, ne)


def to_drawable_edge(vprop, wprop, zoom):
	vpos = [vprop.position.lat/float(1e7), vprop.position.lon/float(1e7)]
	wpos = [wprop.position.lat/float(1e7), wprop.position.lon/float(1e7)]
	
	vpos_xy = gps.mercator.gps2xy(gps.gpspos(vpos[0], vpos[1]), zoom)
	wpos_xy = gps.mercator.gps2xy(gps.gpspos(wpos[0], wpos[1]), zoom)

	return drawable_edge(vpos_xy, wpos_xy);
	

def fill_vertex_qtree(g, tree):
	for v in g.vertices():
		vpos = g.vertex_property(v).position
		tree.insert((vpos.lat, vpos.lon), v)


class drawable_edge:
	def __init__(self, p1, p2):
		self.set_position(p1, p2)
		
	def set_position(self, p1, p2):
		self.p1 = QtCore.QPoint(p1[0], p1[1])
		self.p2 = QtCore.QPoint(p2[0], p2[1])
			
	#@{ drawable interface
	def paint(self, painter, view_offset):
		x0,y0 = view_offset		
		painter.drawLine(self.p1.x()+x0, self.p1.y()+y0, self.p2.x()+x0,
			self.p2.y()+y0)		
	#@}

class drawable_mark:
	def __init__(self, xypos, r):
		self.xypos = QtCore.QPoint(xypos[0], xypos[1])
		self.r = r

	#@{ drawable interface
	def paint(self, painter, view_offset):
		x0,y0 = view_offset
		painter.drawEllipse(self.xypos.x()+x0-self.r/2, 
			self.xypos.y()+y0-self.r/2, self.r, self.r)
	#@}

