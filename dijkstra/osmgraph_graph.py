# -*- coding: utf-8 -*-
import gps, osmgraph_file

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
		self.position = gps.signed_position(raw[0], raw[1])

