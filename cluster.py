# -*- coding: utf-8 -*-

import position

class base_cluster:
	def __init__(self):
		self.elems = set()

	def position(self):
		pass

	def intersection(self, x):
		return False

	def insert(self, x):
		self.elems.add(x)

	def __len__(self):
		return len(self.elems)

	# iterable interface
	def __iter__(self):
		return self.elems.__iter__()

	def next(self):
		return self.elems.__next__()
		

class spatial_cluster(base_cluster):
	def __init__(self, xypos, radius):
		base_cluster.__init__(self)
		self.r = radius
		self.pos = xypos

	def intersection(self, x):
		return position.distance(self.pos, x.position()) < self.r

	def position(self):
		return self.pos
