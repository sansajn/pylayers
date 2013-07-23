# -*- coding: utf-8 -*-
# Zobrazuje graf vygenerovaný programom 'osm/graph/graph_generator'.
# \author Adam Hlavatovič
import sys, math, time, random
from PyQt4 import QtCore, QtGui
import layer_interface, gps, qtree, osmgraph_file, osmgraph_graph, dijkstra, \
	geo_helper, qt_helper

# g:graph, q:qtree-grid
drawable_settings = {'graph':False, 'qtree-grid':True}

class layer(layer_interface.layer):
	def __init__(self, widget):
		layer_interface.layer.__init__(self)
		self.widget = widget
		self.gfile = None
		self.graph = None
		self.drawable = None  # 11 LOD, see LOD-table
		self.path = []
		self.drawable_path = []
		self.sample_compute = True
		self.vertex_qtree = None  # vrcholy grafu v priestorovom usporiadani
		self.vertex_collections = None  # oblasti v ktorych je maximalne N vrcholou (v podstate listy vertex_qtree stromu).
		self.vertex_collection_under_cursor = None
		self.vertex_under_cursor = None
		self.source_vertex = -1
		self.target_vertex = -1
		self.drawable_marks = []
		
		widget.append_layer_description(self._layer_description())

	#@{ layer-interface
	def create(self, graph_fname):
		self.gfile = osmgraph_file.graph_file(graph_fname)
		self.graph = osmgraph_graph.graph(self.gfile)

		helper = geo_helper.layer(self.widget)
		helper.zoom_to(self._graph_gps_bounds())

		bounds = qt_helper.grect_to_qrect(self._graph_bounds())
		self.vertex_qtree = qtree.qtree(bounds)
		fill_vertex_qtree(self.graph, self.vertex_qtree)
		
	def paint(self, painter, view_offset):
		t = time.clock()
		
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
			
		# qtree-grid
		if drawable_settings['qtree-grid']:
			leafs = self.vertex_qtree.leafs()
			for leaf in leafs:
				self._draw_geo_rect(leaf.bounds(), view_offset, painter)
			
		# collection under cursor
		if self.vertex_collection_under_cursor:
			painter.save()
			
			# bounds
			painter.setPen(QtCore.Qt.red)
			collection = self.vertex_collection_under_cursor			
			self._draw_geo_rect(collection.bounds(), view_offset, painter)			
			
			# vertices
			painter.setPen(QtCore.Qt.black)
			for elem in collection.data():
				v_pos = elem[0]
				self._draw_geo_circle(v_pos, view_offset, painter)
				
			painter.restore()
			
		# vertex under cursor
		if self.vertex_under_cursor:
			g = self.graph
			vprop = g.vertex_property(self.vertex_under_cursor)
			self._draw_vertex_under_cursor(vprop.position, view_offset, painter)
			
		dt = time.clock() - t
		self.debug('  #osmgraph_layer.paint(): %f s' % (dt, ))

	def zoom_event(self, zoom):
		self.zoom = zoom

		t = time.clock()
		self._prepare_drawable_data()
		dt = time.clock() - t

		self.debug('  #osmgraph_layer.zoom_event(): %f s' % (dt, ))

	def mouse_release_event(self, event):
		cursor_geo = self._cursor_xy_to_geo(event.pos())
		v = self._find_vertex_under_cursor(cursor_geo)
		if not v:
			return

		# new selection
		if self.source_vertex != -1 and self.target_vertex != -1:
			self.drawable_marks = []
			self.source_vertex = self.target_vertex = -1

		if self.source_vertex == -1:
			self.source_vertex = v
			self.path = []
		else:
			self.target_vertex = v
			self._compute_path()

		self.drawable_marks.append(
			to_drawable_mark(self.graph.vertex_property(v), self.zoom))

		self.widget.update()
		
	def mouse_move_event(self, event):
		t = time.clock()

		update = False

		point_geo_sig = self._cursor_xy_to_geo(event.pos())

		if self._colletion_visualisation(point_geo_sig):
			update = True
				
		if self._vertex_visualisation(point_geo_sig):
			update = True
			
		if update:
			self.widget.update()
			print '#mouse_move_event: update()'
			
		dt = time.clock() - t
		#print '  #mouse_move_event(): %f s' % (dt, )
			
	def key_press_event(self, event):
		if event.key() == QtCore.Qt.Key_G:			
			drawable_settings['graph'] = not drawable_settings['graph']
			if drawable_settings['graph']:
				self._prepare_drawable_graph()
			else:
				self.drawable = []
		if event.key() == QtCore.Qt.Key_Q:
			drawable_settings['qtree-grid'] = not drawable_settings['qtree-grid']

	def _colletion_visualisation(self, cursor_geo):
		update = False		
		bounds = QtCore.QRectF(cursor_geo, QtCore.QSizeF(1, 1))
		leafs = self.vertex_qtree.leafs(bounds)
		if len(leafs):
			collection = leafs[0]
			if not self.vertex_collection_under_cursor:
				self.vertex_collection_under_cursor = collection
				update = True
			elif collection.bounds() != self.vertex_collection_under_cursor.bounds():
				self.vertex_collection_under_cursor = collection
				update = True
		elif self.vertex_collection_under_cursor:
			self.vertex_collection_under_cursor = None
			update = True
			
		return update
		
	def _vertex_visualisation(self, cursor_geo):
		update = False
		v = self._find_vertex_under_cursor(cursor_geo)
		if v and v != self.vertex_under_cursor:			
			update = True
		elif (not v) and self.vertex_under_cursor:
			update = True
		self.vertex_under_cursor = v
		return update
			
	#@} layer-interface
	
	def _compute_path(self):
		tm = time.clock()
		search_algo = dijkstra.dijkstra(self.graph)
		self.path = search_algo.search(self.source_vertex, self.target_vertex)
		dt = time.clock() - tm

		if self.path:
			print 'search takes: %f s (%d -> %d : %d)' % (dt, 
				self.source_vertex, self.target_vertex, len(self.path))
			self._fill_drawable_path()
			self.widget.update()
		else:
			self.path = []
			print 'search failed'

	def _prepare_drawable_data(self):
		'''
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
		
		if drawable_settings['graph']:
			self._prepare_drawable_graph()		

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
		'Vrati hranice grafu ako signed georect.'
		graph_header = self.gfile.read_header()
		bounds = graph_header['bounds']
		sw = gps.signed_position(bounds[0][0], bounds[0][1])
		ne = gps.signed_position(bounds[1][0], bounds[1][1])
		return gps.georect(sw, ne)

	def _graph_gps_bounds(self):
		b = self._graph_bounds()
		sw = gps.gpspos(b.sw.lat/float(1e7), b.sw.lon/float(1e7))
		ne = gps.gpspos(b.ne.lat/float(1e7), b.ne.lon/float(1e7))
		assert valid_bounds(b), 'invalid bounds'
		return gps.georect(sw, ne)
	
	def _find_vertex_under_cursor(self, cursor_geo):
		if self.vertex_collection_under_cursor:
			verts = self.vertex_collection_under_cursor.data()
			
			dists = []
			for v in verts:
				dists.append(self._point_distance(v[0], cursor_geo))
								
			min_idx = min_val_idx(dists)
			if min_idx != -1 and dists[min_idx] < 1000**2:
				return verts[min_idx][1]			
		return None

	def _draw_geo_rect(self, rect_geo, view_offset, painter):
		x0,y0 = view_offset
		sw_geo = rect_geo.topLeft()
		ne_geo = rect_geo.bottomRight()
		sw_xy = gps.mercator.gps2xy(gps.gpspos(sw_geo.x()/1e7, sw_geo.y()/1e7), self.zoom)
		ne_xy = gps.mercator.gps2xy(gps.gpspos(ne_geo.x()/1e7, ne_geo.y()/1e7), self.zoom) 
		
		painter.drawRect(QtCore.QRectF(QtCore.QPointF(sw_xy[0]+x0, ne_xy[1]+y0), 
			QtCore.QPointF(ne_xy[0]+x0, sw_xy[1]+y0)))
		
	def _draw_geo_circle(self, center_geo, view_offset, painter):
		center = geo_helper.coordinate.to_xy_drawable(
			(center_geo.x()/1e7, center_geo.y()/1e7), view_offset, self.zoom)
		painter.drawEllipse(QtCore.QPointF(center[0], center[1]), 3, 3)
		
	def _draw_vertex_under_cursor(self, pos, view_offset, painter):
		center = geo_helper.coordinate.to_xy_drawable(
			(pos.lat/1e7, pos.lon/1e7), view_offset, self.zoom)
		painter.save()
		painter.setBrush(QtGui.QBrush(QtCore.Qt.red))
		painter.drawEllipse(QtCore.QPointF(center[0], center[1]), 3, 3)
		painter.restore()
		
	def _prepare_drawable_graph(self):
		'debugovacia funkcia, predpripravy graf na kreslenie'
		g = self.graph
		for v in g.vertices():
			vprop = g.vertex_property(v)
			for e in g.adjacent_edges(v):
				w = g.target(e)
				wprop = g.vertex_property(w)
				self.drawable.append(
					to_drawable_edge(vprop, wprop, self.zoom))
				
	def _point_distance(self, a, b):
		return (b.x() - a.x())**2 + (b.y() - a.y())**2
	
	def _cursor_xy_to_geo(self, cursor_pos):
		# (?) <> jak toto moze fungovat, ked pozicia mysi je od laveho horneho rohu ?
		point_local = (cursor_pos.x(), cursor_pos.y())
		point_world = self.widget.to_world_coordinates(point_local)
		point_geo = gps.mercator.xy2gps(point_world, self.zoom)
		point_geo_sig = QtCore.QPointF(point_geo.lat*1e7, point_geo.lon*1e7)
		return point_geo_sig
	
	def _layer_description(self):
		return {
			'title':'OSM graph layer',
			'description':"Simple graph imlementation.",
			'commands':[
				'g to show/hide graph',
				'q to show/hide quad-tree structure',
				'left to select source/target vertex'
			]
		}

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
		tree.insert(QtCore.QPointF(vpos.lat, vpos.lon), v)

def euklid_distance_squered(p1, p2):
	return (p1.lat-p2.lat)**2 + (p1.lon-p2.lon)**2

def min_val_idx(seq):
	first = True
	min_idx, min_val = (-1, None)
	for k,v in enumerate(seq):
		if not first:
			if v < min_val:
				min_idx = k
				min_val = v
		else:
			min_idx = k
			min_val = v
			first = False
	return min_idx

def valid_bounds(b):
	return valid_position(b.sw) and valid_position(b.ne)

def valid_position(p):
	return p.lat <= 180*1e7 and p.lat >= -180*1e7 and p.lon <= 180*1e7 and p.lon >= -180*1e7 

class drawable_edge:
	def __init__(self, p1, p2):
		self.set_position(p1, p2)
		
	def set_position(self, p1, p2):
		self.p1 = QtCore.QPoint(p1[0], p1[1])
		self.p2 = QtCore.QPoint(p2[0], p2[1])
			
	#@{ drawable interface
	def paint(self, painter, view_offset):
		x0,y0 = view_offset
		# line
		painter.drawLine(self.p1.x()+x0, self.p1.y()+y0, self.p2.x()+x0,
			self.p2.y()+y0)
		# vertices
		painter.drawRect(self.p1.x()+x0-2, self.p1.y()+y0-2, 4, 4)
		painter.drawRect(self.p2.x()+x0-2, self.p2.y()+y0-2, 4, 4)
		# direction
		
	#@}
	
arrow_angle = 30
arrow_length = 4
#arrow_size_coef = arrow_length*tg(arrow_angle)

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

