# -*- coding: utf-8 -*-
# Zobrazuje graf vygenerovaný programom 'osm/graph/graph_generator'.
# \author Adam Hlavatovič
import sys, math, time, random
from PyQt4 import QtCore, QtGui
import layer_interface, gps, qtree, osmgraph_file, osmgraph_graph, dijkstra


class layer(layer_interface.layer):
	def __init__(self, parent):
		layer_interface.layer.__init__(self)
		self.parent = parent
		self.gfile = None
		self.graph = None
		self.drawable = None  # 11 LOD, see LOD-table
		self.path = []
		self.drawable_path = []
		self.sample_compute = True
		self.vertex_qtree = None
		self.source_vertex = -1
		self.target_vertex = -1
		self.drawable_marks = []

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
		r'''
		for i in range(0, len(lod_table)):
			if self.zoom >= lod_table[i]:
			self._paint_drawable_group(self.drawable[i], painter, view_offset)
		'''
		for d in self.drawable:
			d.paint(painter, view_offset)

		# path
		painter.save()
		pen = QtGui.QPen(QtGui.QColor(218, 0, 0))
		pen.setWidth(3)
		painter.setPen(pen)
		for d in self.drawable_path:
			d.paint(painter, view_offset)
		painter.restore()

		# marks
		for d in self.drawable_marks:
			d.paint(painter, view_offset)

	def zoom_event(self, zoom):
		self.zoom = zoom

		t = time.clock()
		self._prepare_drawable_data()
		dt = time.clock() - t

		self.debug('  #osmgraph_layer.zoom_event(): %f s' % (dt, ))

	def mouse_release_event(self, event):
		r = self._smallest_rectangle(
			self.parent.to_world_coordinates((event.x(), event.y())))
		verts = self.vertex_qtree.lookup(r)
		if len(verts) == 0:
			print 'nothing found'
			return

		#assert len(verts) < 2, 'more than one vertex in the area'
		if len(verts) > 1:
			print 'found %d vertices in selection' % (len(verts), )

		if self.source_vertex != -1 and self.target_vertex != -1:
			self.drawable_marks = []
			self.source_vertex = self.target_vertex = -1			

		v = self._choose_closest(verts)
		print 'selected vertex: %d' % (v, )

		if self.source_vertex == -1:
			self.source_vertex = v
			self.path = []
		else:
			self.target_vertex = v
			self._compute_path()

		self.drawable_marks.append(
			to_drawable_mark(self.graph.vertex_property(v), self.zoom))

		self.parent.update()
	#@} layer-interface

	def _choose_closest(self, gpos, verts):
		v_min = verts[0]
		min_dist = euklid_distance_squered(gpos, v_min)
		for i in range(1, len(verts)):
			dist = euklid_distance_squered(gpos, verts[i])
			if dist < min_dist:
				min_dist = dist
				v_min = verts[i]
		return v_min


	def _compute_path(self):
		tm = time.clock()
		search_algo = dijkstra.dijkstra(self.graph)
		self.path = search_algo.search(self.source_vertex, self.target_vertex)
		dt = time.clock() - tm

		if self.path:
			print 'search takes: %f s (%d -> %d : %d)' % (dt, 
				self.source_vertex, self.target_vertex, len(self.path))
			self._fill_drawable_path()
			self.parent.update()
		else:
			print 'search failed'

	def _prepare_drawable_data(self):
		r'''
		self.drawable = []
		for i in range(0, len(lod_table)):
			self.drawable.append([])

		g = self.graph
		for v in g.vertices():
			vprop = g.vertex_property(v)
			for e in g.adjacent_edges(v):
				w = g.target(e)
				wprop = g.vertex_property(w)
				self.drawable[e.type].append(
					to_drawable_edge(vprop, wprop, self.zoom))

		print 'LOD summary:'
		for i in range(0, len(lod_table)):
			print '  %d:%d' % (i, len(self.drawable[i]))
		'''
		self.drawable = []
		if len(self.graph.vertices()) < 500:
			g = self.graph
			for v in g.vertices():
				vprop = g.vertex_property(v)
				for e in g.adjacent_edges(v):
					w = g.target(e)
					wprop = g.vertex_property(w)
					self.drawable.append(
						to_drawable_edge(vprop, wprop, self.zoom))

		if len(self.path) > 0:
			self._fill_drawable_path()

		self.drawable_marks = []
		if self.source_vertex != -1:
			self.drawable_marks.append(to_drawable_mark(
				self.graph.vertex_property(self.source_vertex), self.zoom))

		if self.target_vertex != -1:
			self.drawable_marks.append(to_drawable_mark(
				self.graph.vertex_property(self.target_vertex), self.zoom))
		
	def _fill_drawable_path(self):
		self.drawable_path = []
		path = self.path
		if len(path) > 1:
			for i in range(0, len(path)-1):
				vprop = self.graph.vertex_property(path[i])
				wprop = self.graph.vertex_property(path[i+1])
				self.drawable_path.append(to_drawable_edge(vprop, wprop, 
					self.zoom))

	def _paint_drawable_group(self, group, painter, view_offset):
		for d in group:
			d.paint(painter, view_offset)

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

	def _smallest_rectangle(self, xypos):
		p1 = gps.mercator.xy2gps((xypos[0]-20, xypos[1]-20), self.zoom)
		p2 = gps.mercator.xy2gps((xypos[0]+20, xypos[1]+20), self.zoom)
		sw = gps.gpspos(min(p1.lat, p2.lat), min(p1.lon, p2.lon))
		ne = gps.gpspos(max(p1.lat, p2.lat), max(p1.lon, p2.lon))
		r = gps.georect(sw, ne)
		return QtCore.QRectF(r.x()*1e7, r.y()*1e7, r.width()*1e7, 
			r.height()*1e7)


def to_drawable_edge(vprop, wprop, zoom):
	vpos = [vprop.position.lat/float(1e7), vprop.position.lon/float(1e7)]
	wpos = [wprop.position.lat/float(1e7), wprop.position.lon/float(1e7)]
	
	vpos_xy = gps.mercator.gps2xy(gps.gpspos(vpos[0], vpos[1]), zoom)
	wpos_xy = gps.mercator.gps2xy(gps.gpspos(wpos[0], wpos[1]), zoom)

	return drawable_edge(vpos_xy, wpos_xy);

def to_drawable_mark(vprop, zoom):
	vpos = [vprop.position.lat/float(1e7), vprop.position.lon/float(1e7)]
	vpos_xy = gps.mercator.gps2xy(gps.gpspos(vpos[0], vpos[1]), zoom)
	return drawable_mark(vpos_xy, 5)
	

def fill_vertex_qtree(g, tree):
	for v in g.vertices():
		vpos = g.vertex_property(v).position
		tree.insert((vpos.lat, vpos.lon), v)

def euklid_distance_squered(p1, p2):
	return (p1.lat-p2.lat)**2 + (p1.lon-p2.lon)**2


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
		painter.drawRect(self.p1.x()+x0-2, self.p1.y()+y0-2, 4, 4)
		painter.drawRect(self.p2.x()+x0-2, self.p2.y()+y0-2, 4, 4)
	#@}

class drawable_mark:
	def __init__(self, xypos, r):
		self.xypos = QtCore.QPoint(xypos[0], xypos[1])
		self.r = r

	#@{ drawable interface
	def paint(self, painter, view_offset):
		painter.save()
		
		black_solid_pen = QtGui.QPen(QtGui.QColor(0, 0, 0))
		black_solid_pen.setStyle(QtCore.Qt.SolidLine)
		black_solid_pen.setWidth(5)

		red_brush = QtGui.QBrush(QtGui.QColor(222, 0, 0))

		painter.setPen(black_solid_pen)
		painter.setBrush(red_brush)		

		x0,y0 = view_offset
		painter.drawEllipse(self.xypos.x()+x0-self.r, 
			self.xypos.y()+y0-self.r, 2*self.r, 2*self.r)

		painter.restore()
	#@}

class highway_values:
	r'\saa http://wiki.openstreetmap.org/wiki/Map_features#Highway'
	MOTORWAY = 0
	MOTORWAY_LINK = 1
	TRUNK = 2
	TRUNK_LINK = 3
	PRIMARY = 4
	PRIMARY_LINK = 5
	SECONDARY = 6
	SECONDARY_LINK = 7
	TERTIARY = 8
	TERTIAY_LINK = 9
	LIVING_STREET = 10
	PEDESTRIAN = 11
	UNCLASSIFIED = 12
	SERVICE = 13
	TRACK = 14
	BUS_GUIDEWAY = 15
	RACEWAY = 16
	ROAD = 17
	PATH = 18
	FOOTWAY = 19
	CYCLEWAY = 20
	BRIDLEWAY = 21
	STEPS = 22
	PROPOSED = 23
	CONSTRUCTION = 24

r'''
LOD (levels of detail) table
levels
0 - 2 : nothing
3 - 4 : 0
5 - 6 : (p), 1, 2
7     : (p), 3
8 - 9 : (p), 4
10    : (p), 5
11    : (p), 6
12    : (p), 7
13    : (p), 8, 9
14    : (p), 10, 11, 12, 13, 14, 15, 16, 17, 18
15    : all

\note keys are highway-values, values are minimal zoom level
'''
lod_table = [
	3,   # motorway
	5,   # motorway-link
	5,   # trunk
	7,   # trunk-link
	8,   # primary
	10,  # primary-link
	11,  # secondary
	12,  # secondary-link
	13,  # tertiary
	13,  # tertiary-link
	14,  # living-street
	14,  # pedestrian
	14,  # unclassified
	14,  # service
	14,  # track
	14,  # bus-guideway
	14,  # raceway
	14,  # road
	14,  # path
	15,  # footway
	15,  # cycleway
	15,  # bridleway
	15,  # steps
	15,  # proposed
	15   # construction
]

