# -*- coding: utf-8 -*-
# Implementuje rôzne interpretácie pozície v priestore.
# \author Adam Hlavatovič
# \version 20120422

import math

class base_pos:
	def distance(self, b):
		pass

	def components(self):
		pass

class xypos(base_pos):
	r'Pozícia na rovine.'
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def distance(self, b):
		return math.sqrt((self.x - b.x)**2 + (self.y - b.y)**2)

	def components(self):
		return (self.x, self.y)
		

def distance(a, b):
	return a.distance(b)
	

