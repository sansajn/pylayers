# -*- coding: utf-8 -*-
# Implmentuje obojsmerný dikstrov algoritmus.
import sys, time, heapq


class search:
	def __init__(self, graph):
		self._graph = graph
		
		# stats
		self._forward_iteration = 0
		self._forward_path_edges = -1		
		self._backward_iteration = 0
		self._backward_path_edges = -1
		self._common_vertex = -1
		self._takes = -1  # in ms 
	
	def find_path(self, s, t):
		t_start = time.clock()
		
		g = self._graph
		fwd = forward_step(s, t)
		bwd = backward_step(t, s)
		
		while not self._target_reached(fwd, bwd, t, s):
			self._forward_iteration += 1
			if not fwd.step(g):
				return None
			
			self._backward_iteration += 1
			if not bwd.step(g):
				return None
			
		self._takes = time.clock() - t_start
		
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
		
		self._common_vertex = common_vert
		self._backward_path_edges = len(backward_path)
		self._forward_path_edges = len(forward_path) - self._backward_path_edges
		
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

		self.props = {}
		
	def step(self, g):
		heap = self._heap
		
		if self._v != -1:  
			if len(heap) == 0:
				return False
			self._v = heapq.heappop(heap)[1]
		else:  # first iteration
			self._v = self._s
			s_prop = self._property(self._s)[0]
			s_prop.distance = 0
			s_prop.color = vertex_color.GRAY
			
		v = self._v		
		if v == self._t:
			return True
		
		v_prop = self._property(v)[0]
		v_prop.color = vertex_color.WHITE
		
		for e in self.adjacent_edges(g, v):
			w = g.target(e)
			w_prop, isnew = self._property(w)			
			w_dist = self._distance(v) + g.cost(e)
			if w_prop.distance > w_dist:
				assert w_prop.color != vertex_color.WHITE, 'logic-error: dorazil som do uz navstiveneho vrcholu rychlejsie ako ked som ho prvy krat navstivil'
				w_prop.color = vertex_color.GRAY
				w_prop.distance = w_dist
				w_prop.predecessor = v
				if isnew:
					heapq.heappush(heap, (w_dist, w))
				else:
					heapq.heappush(heap, (w_dist, w))  # update value (not yet implemented)
		
		return True

	def last_visited(self):
		return self._v
	
	def adjacent_edges(self, g, v):
		'Vrati mnozinu susednych hran (v konkretnej implementacii treba implementovat).'
		assert False, 'not yet implemented'

	def _property(self, v):
		'Vráti dvojicu (property_record, bool).'
		try:
			return (self.props[v], False)
		except KeyError:
			prop = property_record()
			self.props[v] = prop
			return (prop, True)
		
	def _distance(self, v):
		return self._property(v)[0].distance


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

