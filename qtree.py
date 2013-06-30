# -*- coding: utf-8 -*-

class qtree:
	r'rekurzivna implementacia quad-tree'	
	def __init__(self, bounds):
		self._size = 0
		self._root = quad_node(bounds, 0)

	def insert(self, point, value):
		self._size += 1
		self._root.insert(point, value)

	def lookup(self, bounds):
		return self._root.lookup(bounds)
	
	def leafs(self, bounds):
		r'Vrati listy stromu.'
		return self._root.leafs(bounds)
	
	def bounds(self):
		return self._root.bounds()


class quad_node:
	NELEMS = 32
	def __init__(self, bounds, level):
		self._bounds = boundary(bounds.a, bounds.b)
		self._children = []
		self._data = []
		self._level = level

	def insert(self, point, value):
		if self._leaf():
			if self._has_space():
				self._data.append((point, value))
				return
			else:
				self._subdivide()

		p = point
		w,h = (self._bounds.width(), self._bounds.height())
		x,y = self._bounds.a	

		if p[0] >= x and p[0] <= x+w/2.0:  # 1 or 3
			if p[1] >= y and p[1] <= y+h/2.0:
				self._children[0].insert(point, value)
			else:
				self._children[2].insert(point, value)
		else: # 2 or 4
			if p[1] >= y and p[1] <= y+h/2.0:
				self._children[1].insert(point, value)
			else:
				self._children[3].insert(point, value)

	def lookup(self, bounds):
		if not self._bounds.intersect(bounds):
			return []
		else:
			elems = []
			if self._leaf():
				if bounds.subset(self.bounds()):
					elems.extend([p[1] for p in self._data])
				else:
					for p in self._data:
						if bounds.contains(p[0]):
							elems.append(p[1])
					return elems
			else:
				for ch in self._children:
					elems.extend(ch.lookup(bounds))
				return elems

	def leafs(self, bounds):
		if not self._bounds.intersect(boundary(bounds.a, bounds.b)):
			return []
		else:
			if not self._leaf():
				leafs = []
				for ch in self._children:
					leafs.extend(ch.leafs(bounds))
				return leafs
			else:
				return [self]
			
	def bounds(self):
		return self._bounds
	
	def level(self):
		return self._level
	
	def data(self):
		return self._data

	def _subdivide(self):
		x,y = self._bounds.a
		w,h = (self._bounds.width(), self._bounds.height())
		self._children.append(
			quad_node(boundary((x, y), (x+w/2.0, y+h/2.0)), self._level+1))
		self._children.append(
			quad_node(boundary((x+w/2.0, y), (x+w, y+h/2.0)), self._level+1))
		self._children.append(
			quad_node(boundary((x, y+h/2.0), (x+w/2.0, y+h)), self._level+1))
		self._children.append(
			quad_node(boundary((x+w/2.0, y+h/2.0), (x+w, y+h)), self._level+1))

		# preusporiadaj prvky
		data = self._data				
		for d in data:
			self.insert(d[0], d[1])
		self._data = []
		
	def _leaf(self):
		return len(self._children) == 0

	def _has_space(self):
		return len(self._data) < quad_node.NELEMS


class boundary:
	'''Hranica, štvorcová oblasť definovaná pravým-dolným a a
	ľavím-horným b bodom.'''
	def __init__(self, a, b):
		self._set(a, b)

	def _set(self, a, b):
		self.a = ((min(a[0], b[0])), (min(a[1], b[1])))
		self.b = ((max(a[0], b[0])), (max(a[1], b[1])))

	def width(self):
		return self.b[0] - self.a[0]
	
	def height(self):
		return self.b[1] - self.a[1]

	def intersect(self, bounds):
		r = bounds
		return not (abs(r.b[0] - self.a[0]) > (self.width() + r.width())) or (
			abs(r.b[1] - self.a[1]) > (self.height() + r.height()))
		
	def subset(self, bounds):
		'True ak bounds je podmnozina self-boundary.'
		r = bounds
		return r.a[0] >= self.a[0] and r.a[1] >= self.a[1] and \
			r.b[0] <= self.b[0] and r.b[1] <= self.b[1]

