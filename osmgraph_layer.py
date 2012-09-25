# -*- coding: utf-8 -*-
# Zobrazuje graf vygenerovaný programom 'osm/graph/graph_generator'.
# \author Adam Hlavatovič
import sys, math, re, struct, time, heapq, random
from PyQt4 import QtCore, QtGui
import gps, layers


class layer(layers.layer_interface):
	def __init__(self, parent):
		layers.layer_interface.__init__(self, parent)
		self.parent = parent
		self.graph = None
		self.drawable = []

	#@{ layer_interface
	def create(self, graph_fname):
		gfile = graph_file(graph_fname)
		self.graph = graph(gfile)

		layer = self.parent.get_layer('map')
		if layer:
			raw_bounds = gfile.read_header()['bounds']
			sw = gps.gpspos(raw_bounds[0][0]/float(1e7), 
				raw_bounds[0][1]/float(1e7))
			ne = gps.gpspos(raw_bounds[1][0]/float(1e7), 
				raw_bounds[1][1]/float(1e7))
			bounds = gps.gpsrect(sw, ne)
			layer.zoom_to(bounds)

		# compute sample route
		s = 150
		t,distance = self._trace_vertex(s)

		tm = time.clock()
		
		search_algo = dijkstra(self.graph)
		path = search_algo.search(s, t)
		
		dt = time.clock() - tm
		print 'search takes: %f s (%d -> %d : %d)' % (dt, s, t, distance)

	def paint(self, painter, view_offset):
		for d in self.drawable:
			d.paint(painter, view_offset)

	def zoom_event(self, zoom):
		self.zoom = zoom

		t = time.clock()
		self.prepare_drawable_data()
		dt = time.clock() - t

		self.debug('  #osmgraph_layer.zoom_event(): %f s' % (dt, ))

	#@}

	def signed2xypos(self, spos):
		return gps.mercator.gps2xy(
			gps.gpspos(spos.lat/float(1e7), spos.lon/float(1e7)), self.zoom)

	def prepare_drawable_data(self):
		g = self.graph
		for v in g.vertices():
			vprop = g.vertex_property(v)
			for e in g.adjacent_edges(v):
				w = g.target(e)
				wprop = g.vertex_property(w)
				self.drawable.append(to_drawable_edge(vprop, wprop, self.zoom))

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
			

def to_drawable_edge(vprop, wprop, zoom):
	vpos = [vprop.position.lat/float(1e7), vprop.position.lon/float(1e7)]
	wpos = [wprop.position.lat/float(1e7), wprop.position.lon/float(1e7)]
	
	vpos_xy = gps.mercator.gps2xy(gps.gpspos(vpos[0], vpos[1]), zoom)
	wpos_xy = gps.mercator.gps2xy(gps.gpspos(wpos[0], wpos[1]), zoom)

	return drawable_edge(vpos_xy, wpos_xy);
	


class graph:
	#! \param gfile graph_file structure
	def __init__(self, gfile):
		self._gf = gfile
		self._header = self._gf.read_header()
		self._itable = self._gf.read_itable(self._header)

	def adjacent_edges(self, v):
		return [edge_prop(e) 
			for e in self._gf.read_edges(self._header, self._itable, v)]

	def vertices(self):
		return range(0, self._header['vertices'])	

	def source(self, e):
		'Neviem efektívne implementovať.'
		pass

	def target(self, e):
		return e.target

	def cost(self, e):
		return e.cost

	def vertex_property(self, v):
		return vertex_prop(self._gf.read_vertex(v))		

	def edge_property(self, e):
		return e	


class edge_prop:
	def __init__(self, raw):
		self.target = raw[0]
		self.cost = raw[1]
		self.type = raw[2]

class vertex_prop:
	def __init__(self, raw):
		self.position = signed_position(raw[0], raw[1])

class signed_position:
	def __init__(self, lat, lon):
		self.lat = lat
		self.lon = lon


class graph_file:
	def __init__(self, fname):
		self._fgraph = open(fname, 'r')

	def __del__(self):
		self._fgraph.close()

	def read_header(self):
		self._fgraph.seek(0)
		d = self._fgraph.read(32)
		unpacked = struct.unpack('<8I', d)
		return {
			'vertices': unpacked[0],
			'edges': unpacked[1],
			'bounds': ((unpacked[2], unpacked[3]), (unpacked[4], unpacked[5])),
			'edge_idx': unpacked[6],
			'itable_idx': unpacked[7]
		}

	def read_itable(self, header):
		n_verts = header['vertices']
		self._fgraph.seek(header['itable_idx'])
		d = self._fgraph.read(4*n_verts)
		itable = struct.unpack('<%dI' % n_verts, d)
		return itable

	def read_edges(self, header, itable, idx):
		if itable[idx] == 0xffffffff:
			return []

		next_offset = self._next_valid(itable, idx)
		edges_size = next_offset - itable[idx]
		if next_offset == 0xffffffff:
			edges_size = header['itable_idx'] - itable[idx]

		self._fgraph.seek(itable[idx])
		d = self._fgraph.read(edges_size)

		edges = []
		n_edges = edges_size/9
		for i in range(0, n_edges):
			e = struct.unpack('iib', d[9*i:9*i+9])
			edges.append(e)

		return edges

	def read_vertex(self, idx):
		self._fgraph.seek(32+8*idx)
		d = self._fgraph.read(8)
		return struct.unpack('ii', d)

	def _next_valid(self, itable, idx):
		while idx < len(itable)-1:
			idx += 1
			if itable[idx] != 0xffffffff:
				return itable[idx]
		return 0xffffffff


class drawable_edge:
	def __init__(self, p1, p2):
		self.set_position(p1, p2)
		
	def set_position(self, p1, p2):
		self.p1 = QtCore.QPoint(p1[0], p1[1])
		self.p2 = QtCore.QPoint(p2[0], p2[1])
			
	#@{ drawable interface implementation
	def paint(self, painter, view_offset):
		x0,y0 = view_offset		
		painter.drawLine(self.p1.x()+x0, self.p1.y()+y0, self.p2.x()+x0,
			self.p2.y()+y0)		
	#@}

class drawable_mark:
	def __init__(self, xypos, r):
		self.xypos = QtCore.QPoint(xypos[0], xypos[1])
		self.r = r

	def paint(self, painter, view_offset):
		x0,y0 = view_offset
		painter.drawEllipse(self.xypos.x()+x0-self.r/2, 
			self.xypos.y()+y0-self.r/2, self.r, self.r)



# zatial tu, v budúcnosti presuniem do vlastnej vrstvy

class dijkstra:
	def __init__(self, graph):
		self.g = graph
		self.heap = []
		self.props = {}
		self.iteration = 0

	def search(self, s, t):
		g = self.g
		heap = self.heap

		s_prop = self._property(s)[1]
		s_prop.distance = 0
		heapq.heappush(heap, (0, s))

		while len(heap) > 0:
			self.iteration += 1
			v = heapq.heappop(heap)[1]
			if v == t:
				break
			for e in g.adjacent_edges(v):
				w = g.target(e)
				isnew, w_prop = self._property(w)
				w_dist = self._distance(v) + g.cost(e)
				if w_prop.distance > w_dist:
					w_prop.distance = w_dist
					w_prop.predecessor = v
					if isnew:
						heapq.heappush(heap, (w_dist, w))
					else:
						# update value (not implemented)
						heapq.heappush(heap, (w_dist, w))

		if v == t:
			return self._construct_path(v)
		else:
			return None

	def _construct_path(self, v):
		return v  # not yet implemented

	def _property(self, v):
		try:
			return (False, self.props[v])
		except KeyError:
			prop = property_record()
			self.props[v] = prop
			return (True, prop)

	def _distance(self, v):
		return self._property(v)[1].distance



class property_record:
	def __init__(self):
		self.distance = sys.maxint
		self.predecessor = -1
	
