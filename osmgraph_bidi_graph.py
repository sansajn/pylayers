# -*- coding: utf-8 -*-
'''Implementácia obojsmerného grafu pre podporu obojsmerného
dijkstrovho algoritmu.'''
import gps

class graph:
	'''Implementuje koncept vertex-list-graph.'''
	
	def __init__(self, gfile):
		'''\param gfile graph_file structure'''
		self._gf = gfile
		self._header = self._gf.read_header()
		self._vtable = self._gf.read_vtable(self._header)

	# incidence-graph
	def out_edges(self, v):
		return [edge_prop(e) for e in self._gf.read_edges(self._header, 
			self._vtable, v) if self._output(e)]
	
	def source(self, e):
		'\note Neviem efektívne implementovať.'
		pass

	def target(self, e):
		return e.target
	
	def out_degree(self, v):
		'\note neviem efektivne implementovat'
		pass
	
	# bidirectional-graph
	def in_edges(self, v):
		return [edge_prop(e) for e in self._gf.read_edges(self._header,
			self._vtable, v) if self._input(e)]
		
	def in_degree(self, v):
		'\note neviem efektivne implementovat'
		pass
	
	def degree(self, v):
		return self._gf.num_edges(self._header, self._vtable, v)

	# adjacency-graph
	def adjacent_vertices(self, v):
		return [e.target for e in self._gf.read_edges(self._header,
			self._vtable, v)]

	# vertex-list-graph
	def vertices(self):
		return range(0, self._header['vertices'])	
	
	def num_vertices(self):
		return self._header['vertices']
	
	# custom
	def adjacent_edges(self, v):  # nepremenovat to na incident_edges ?
		return [edge_prop(e) for e in self._gf.read_edges(self._header,
			self._vtable, v)]
	
	def cost(self, e):
		'\note toto by sa malo volat na hranu, nie na graf.'
		return e.cost

	def vertex_property(self, v):
		return vertex_prop(self._gf.read_node(v))		

	def edge_property(self, e):
		return e
	
	def _output(self, e):
		return e.direction == 0
	
	def _input(self, e):
		return e.direction == 1


class edge_prop:
	def __init__(self, raw):
		self.target = raw[0]
		self.cost = raw[1]
		self.type = raw[2]

class vertex_prop:
	def __init__(self, raw):
		self.position = gps.signed_position(raw[0], raw[1])

