# -*- coding: utf-8 -*-
# Rekurzívna implementácia 'quad tree' štruktúry
from PyQt4 import QtCore

class quad_tree:
	def __init__(self, area):
		self.size = 0
		self.root = quad_node(area)

	def insert(self, xypos, value):
		self.size += 1
		self.root.insert(xypos, value)

	def lookup(self, area):
		return self.root.lookup(area)


class quad_node:
	MAX_NODE_ELEMS = 16
	def __init__(self, area):
		self.elems = []
		self.children = []
		self.area = area

	def insert(self, xypos, value):
		if len(self.elems) == quad_node.MAX_NODE_ELEMS:
			if len(self.children) == 0:
				self.subdivide()
			for ch in self.children:
				if ch.contains(xypos):
					ch.insert(xypos, value)
					return
			raise Exception('error: lost data (%g, %g)!' % xypos)			
		else:
			self.elems.append((xypos, value))

	def lookup(self, area):
		if not self.area.intersect(area):
			return []
		else:
			elems = []
			for e in self.elems:
				pos = e[0]
				if area.contains(pos[0], pos[1]):
					elems.append(e[1])
			for ch in self.children:
				elems.extend(ch.lookup(area))
			return elems

	def subdivide(self):
		x,y = (self.area.x(), self.area.y())
		w,h = (self.area.width(), self.area.height())
		self.children.append(quad_node(QtCore.QRectF(x, y, w/2.0, h/2.0)))
		self.children.append(quad_node(QtCore.QRectF(x+w/2.0, y, w/2.0, h/2.0)))
		self.children.append(quad_node(QtCore.QRectF(x, y+h/2.0, w/2.0, h/2.0)))
		self.children.append(quad_node(QtCore.QRectF(x+w/2.0, y+h/2.0, w/2.0, h/2.0)))

	def contains(self, xypos):
		return self.area.contains(xypos[0], xypos[1])

		
