# -*- coding: utf-8 -*-
from PyQt4 import QtCore

class qtree:	
	r'Rekurzivna implementacia quad-tree, zalozena na QRectF a QPointF.'	
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
	NELEMS = 16
	def __init__(self, bounds, level):
		self._bounds = bounds
		self._children = None
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
		x,y = (self._bounds.topLeft().x(), self._bounds.topLeft().y())

		if p.x() >= x and p.x() <= x+w/2.0:  # 1 or 3
			if p.y() >= y and p.y() <= y+h/2.0:
				self._children[0].insert(point, value)
			else:
				self._children[2].insert(point, value)				
		else: # 2 or 4
			if p.y() >= y and p.y() <= y+h/2.0:
				self._children[1].insert(point, value)
			else:
				self._children[3].insert(point, value)
	
	def lookup(self, bounds):
		if not self._bounds.intersects(bounds):
			return []
		else:			
			if self._leaf():
				if bounds.contains(self.bounds()):
					return [p[1] for p in self._data]
				else:
					elems = []
					for p in self._data:
						if bounds.contains(p[0]):
							elems.append(p[1])
					return elems
			else:
				elems = []
				for ch in self._children:
					elems.extend(ch.lookup(bounds))
				return elems
				
	def leafs(self, bounds):
		if not self._bounds.intersects(bounds):
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
		x,y = (self._bounds.x(), self._bounds.y())
		w,h = (self._bounds.width(), self._bounds.height())
		
		self._children = []
		self._children.append(
			quad_node(QtCore.QRectF(x, y, w/2.0, h/2.0), self._level+1))
		self._children.append(
			quad_node(QtCore.QRectF(x+w/2.0, y, w/2.0, h/2.0), self._level+1))
		self._children.append(
			quad_node(QtCore.QRectF(x, y+h/2.0, w/2.0, h/2.0), self._level+1))
		self._children.append(
			quad_node(QtCore.QRectF(x+w/2.0, y+h/2.0, w/2.0, h/2.0), self._level+1))

		# preusporiadaj prvky
		data = self._data
		for d in data:
			self.insert(d[0], d[1])
		self._data = []
		
	def _leaf(self):
		return self._children == None 

	def _has_space(self):
		return len(self._data) < quad_node.NELEMS

