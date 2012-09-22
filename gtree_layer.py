# -*- coding: utf-8 -*-
# Určené pre vyzualizáciu stromu grafu v doprednom a spetnom smere a ich
# porovnanie.
# \author Adam Hlavatovič

from PyQt import QtCore, QtGui
import gps, layers, vof_dump

# \note create() > zoom_event() > [paint()]
class layer(layers.layer_interface):
	def __init__(self, widget):
		layers.layer_interface.__init__(self, widget)

	#@{ layer_interface implementation
	def create(self, uri):
		reader = vof_dump.reader(uri)
		pass

	def paint(self, painter):
		pass

	def key_press_event(self, event):
		pass

	def zoom_event(self, zoom):
		self.zoom = zoom

	def pan_event(self):
		pass

	# \param event QMouseEvent
	def mouse_press_event(self, event):
		pass

	#@}



# * prečítaj vof
# * vyfiltruj ho
# * vykresli celý strom v doprednom smere
# * prejdi strom v spetnom smere (čo mi dá možnosť získať významné úseky cestnej
# sieťe v prehľadanej oblasti)


def main():
	vof_data = read_vof()
	forward = create_graph(vof_data)
	draw_graph(graph)
	significant_graph_parts = backward_graph_traverse(forward)


def read_vof():
	reader = vof_dump.reader('data/hannover_dortmund.vof')
	return reader.get_graph()
	
def create_graph(data):
	edges = set()
	verts_map = {}
	unique_verts = []

	for d in data:
		s = vertex(gps.gpspos(d['lat-from'], d['lon-from']))
		sit = insert_if_unique(verts_map, unique_verts, s)
		
		t = vertex(gps.gpspos(d['lat-to'], d['lon-to']))
		tit = insert_if_unique(verts_map, unique_verts, t)

		edges.add(edge(sit, tit))

	return graph([e for e in edges], unique_verts)

def draw_graph():	
	pass

def backward_graph_traverse():
	pass


def insert_if_unique(verts_map, verts, v):
	vidx = verts_map.get(v, -1)
	if vidx == -1:
		verts.append(v)
		vidx = len(verts)-1
		verts_map[v] = vidx
		return vidx
	else:
		return vidx

class graph:
	def __init__(self, edges, verts):
		self.edges = edges
		self.vertices = verts

class edge:
	def __init__(self, sit, tit):
		self.source_iter = sit
		self.target_iter = tit

	def __eq__(self, b):
		return self.source_iter == b.source_iter and 
			self.target_iter == b.target_iter

	def __hash__(self):
		return self.target_iterator

class vertex:
	BLACK, GREY, WHITE, GREEN = range(0, 4)

	def __init__(self, gpos):
		self.gpos = gpos
		self.xypos = (-1, -1)

	def calculate_xy(self, zoom):
		self.xypos = mercator.gps2xy(self.gpos, zoom)

	def __eq__(self, b):
		return self.gpos == b.gpos

	def __hash__(self):
		return self.gpos.__hash__()



def load_graph(fname, g):
	gvof = create_vof_graph(read_vof())
	



class dijkstra_search:
	class vertex_property:
		def __init__(self, dist, pred):
			self.distance = dist
			self.predecessor = pred

	def __init__(self):
		self.props = {}

	def search(s, t, g):
		v = None
		while len(pq):
			priority, counter, dist, v = heappop(pq)
			if v == t:
				break
			for w in adjacent_vertices(v, g):
				wdist = dist + cost(v, w, g)
				if self.distance(w) > wdist:
					self.props[w] = vertex_property(wdist, v)
					heappush([wdist, next(counter), w])
		if v == t:
			return self.construct_path(v, s)
		return []

	def construct_path(self, v, s):
		path = []
		while v != s:
			path.append(v)
			v = self.props[v].predecessor
		path.append(s)
		return [i for i in reversed(path)]

	def distance(self, v):		
		return self.props.get(v, sys.maxint)



def adjacent_vertices(v, g):
	return g.adjacent_vertices(v)

def cost(v, w, g):
	return g.cost(v, w)

def set_property(v, data, g):
	return g.set_property(v, data)


class graph:
	r'Implementuje planarny graf.'
	def __init__(self):
		self.verts = {}
		self.props = {}

	def add_vertex(self, v):
		if v not in verts:
			self.verts[v] = {}

	def add_edge(self, e):
		self.add_vertex(e.source)
		self.verts[e.source][e.target] = (e.cost, )

	def adjacent_vertices(self, v):
		return self.verts[v]

	def cost(self, v, w):
		return self.verts[v][w][0]

	def set_property(self, v, data):
		self.props[v] = data

	def get_property(self, v):
		return self.props[v]


	





if __name__ == '__main__':
	main()
