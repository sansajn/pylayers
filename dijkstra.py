# -*- coding: utf-8 -*-
# Implmentuje jednosmerný dikstrov algoritmus.
import sys, heapq

#! \saa Pozri 'osmgraph_graph.py' pre implementáciu grafu.
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
		path = []
		while v != -1:
			path.append(v)
			v = self._property(v)[1].predecessor
		path.reverse()
		return path

	#! Vráti dvojicu (bool, property_record).
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

