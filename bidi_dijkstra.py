# -*- coding: utf-8 -*-
# Implmentuje obojsmerný dikstrov algoritmus.
import sys, heapq


class search:
	def __init__(self, graph):
		self._graph = graph
	
	def find_path(self, s, t):
		g = self._graph
		fwd = forward_step(s, t)
		bwd = backward_step(t, s)
		while not self._target_reached(fwd, bwd, t, s):
			if not fwd.step(g):
				return None
			if not bwd.step(g):
				return None
		return self._construct_path(fwd, bwd, t, s)
	
	def _target_reached(self, fwd, bwd, t_fwd, t_bwd):
		fwd_last, bwd_last = (fwd.last_visited(), bwd.last_visited())
		
		if fwd_last == t_fwd or bwd_last == t_bwd:
			return True
				
		value = bwd.props.get(fwd_last)
		if value != None:
			return value.color == vertex_color.WHITE
			
		value = fwd.props.get(bwd_last)
		if value != None:
			return value.color == vertex_color.WHITE
				
		return False
	
	def _construct_path(self, fwd, bwd, t_fwd, t_bwd):
		fwd_last, bwd_last = (fwd.last_visited(), bwd.last_visited())

		if fwd_last == t_fwd:
			return self._forward_construct(fwd, t_fwd)
		elif bwd_last == t_bwd:
			return self._backward_construct(bwd, t_bwd)
		
		if fwd_last in bwd.props:
			common_vert = fwd_last
		else:
			common_vert = bwd_last
			
		forward_path = self._forward_construct(fwd, common_vert)
		backward_path = self._backward_construct(bwd, common_vert)		
		forward_path.extend(backward_path)
		
		return forward_path
			
		
	def _forward_construct(self, fwd, v):
		props = fwd.props

		path = []
		while v != -1:
			path.append(v)
			v = props[v].predecessor
		path.reverse()
		
		return path
	
	def _backward_construct(self, bwd, v):
		props = bwd.props
				
		path = []
		while v != -1:
			path.append(v)
			v = props[v].predecessor
					
		return path


class search_step_base:
	def __init__(self, s, t):
		self._v = -1
		self._s = s
		self._t = t
		self._heap = []		
		self._iteration = 0
		
		self.props = {}
		
	def step(self, g):					
		heap = self._heap
		
		if self._v != -1:  
			if len(heap) == 0:
				return False
			self._v = heapq.heappop(heap)[1]
		else:  # first iteration
			self._v = self._s
			s_prop = self._property(self._s)[1]
			s_prop.distance = 0
			s_prop.color = vertex_color.GRAY
			heapq.heappush(heap, (0, self._s))
			
		v = self._v
		if v == self._t:
			return True
		
		for e in self.adjacent_edges(g, v):
			w = g.target(e)
			isnew, w_prop = self._property(w)			
			assert w_prop.color != vertex_color.WHITE, 'logic-error: dorazil som do uz navstiveneho vrcholu rychlejsie ako ked som ho prvy krat navstivil'				
			w_prop.color = vertex_color.GRAY
			w_dist = self._distance(v) + g.cost(e)
			if w_prop.distance > w_dist:
				w_prop.distance = w_dist
				w_prop.predecessor = v
				if isnew:
					heapq.heappush(heap, (w_dist, w))
				else:
					heapq.heappush(heap, (w_dist, w))  # update value (not yet implemented)
		
		self._iteration += 1
		
		return True

	def last_visited(self):
		return self._v
	
	def adjacent_edges(self, g, v):
		'Vrati mnozinu susednych hran (v konkretnej implementacii treba implementovat).'
		assert False, 'not yet implemented'

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


class forward_step(search_step_base):
	def __init__(self, s, t):
		search_step_base.__init__(self, s, t)
		
	def adjacent_edges(self, g, v):
		return g.out_edges(v)
	

class backward_step(search_step_base):
	def __init__(self, s, t):
		search_step_base.__init__(self, s, t)
	
	def adjacent_edges(self, g, v):
		return g.in_edges(v)


class vertex_color:
	BLACK = 0
	GRAY = 1
	WHITE = 2

class property_record:
	def __init__(self):
		self.distance = sys.maxint
		self.predecessor = -1
		self.color = vertex_color.BLACK 

