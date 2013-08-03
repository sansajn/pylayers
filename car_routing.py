# -*- coding: utf-8 -*-
# Implementuje routovaciu logiku pre auta

# \note Najlepsi sposob ako sa vyhnut kontextu je, ze funkcie, [in|out]_edges() 
# budu vraciat inu implementaciu hrany.
# \note Sucastou logiky je property mapa (logika totizto urcuje, co do mapy ukladat).

import osmspec, osmgraph_bidi_graph

class graph(osmgraph_bidi_graph.graph):
	def __init__(self, gfile):
		osmgraph_bidi_graph.graph.__init__(self, gfile)
	
	def out_edges(self, v):
		edges = [e for e in osmgraph_bidi_graph.graph.out_edges(self, v) 
			if self._car_allowed(e.type)] 
		return edges
	
	def in_edges(self, v):
		return [e for e in osmgraph_bidi_graph.graph.in_edges(self, v) 
			if self._car_allowed(e.type)]
	
	def _car_allowed(self, type):
		return type < osmspec.highway.track and type != osmspec.highway.pedestrian 
