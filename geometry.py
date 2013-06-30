# -*- coding: utf-8 -*-
# Geometry routines.
# \author Adam Hlavatovič

r'''Bod je definovany ako ľubovolný objekt p, pre ktory platia vyrazy 
p[0], p[1] a v pripade bodu v priestore aj p[2].'''

class line_segment:
	r'Usecka je definovana dvojicou bodou a, b.'
	def __init__(self, a, b):
		self.a = a
		self.b = b		

	def contains(self, x):
		r'''Vrati pravdu ak x lezi na usecke.
		Ak x lezi na priamke urcenej bodmi a, b, potom na zaklade podobnosti 
		trojuholnikou plati
			(x_x - a_x)/(b_x - a_x) = (x_y - a_y)/(b_y - a_y)   (1)
		dalej ak x lezi na usecke urcenej bodmi a, b potom prava (lava) strana 
		rovnice (1) bude v intervale <0, 1> (parametricke vyjadrenie priamky).'''
		a, b = self.a, self.b
		px = (x[0] - a[0])/float(b[0] - a[0])
		py = (x[1] - a[1])/float(b[1] - a[1])
		return px == py and 0.0 <= px <= 1.0	

	def intersects(self, l):
		r'Vrati pravdu ak l pretina usecku.'
		a1 = (self.b[1] - self.a[1])/float(self.b[0] - self.a[0])
		a2 = (l.b[1] - l.a[1])/float(l.b[0] - l.a[0])
		b1 = self.a[1] - a1*self.a[0]
		b2 = l.a[1] - a2*l.a[0]
		if a1 == a2:
			return b1 == b2
		else:
			x = (b2-b1)/(a1-a2)  # v tomto bode sa usecky pretnu
			return self.a[0] <= x <= self.b[0]

	def intersect(self, l):
		r'Vrati bod v ktorom l pretina usecku.'		
		a1 = (self.b[1] - self.a[1])/float(self.b[0] - self.a[0])
		a2 = (l.b[1] - l.a[1])/float(l.b[0] - l.a[0])
		b1 = self.a[1] - a1*self.a[0]
		b2 = l.a[1] - a2*l.a[0]

		if a1 == a2:
			# zatial ignorujem tuto moznost
			return (None, None)
		else:
			x = (b2-b1)/(a1-a2)  # v tomto bode sa usecky pretnu
			if self.a[0] <= x <= self.b[0]:
				y = a1*x+b1
				return (x,y)
			else:
				return (None, None)

	def subsegment(self, l):
		r'Vrati pravdu ak je l sucastou usecky.'
		pass
	
	
class rectangle:
	r'Stvorec je definovany lavym-dolnym bodom a a pravym-hornym bodom b.'
	def __init__(self, p1=(None, None), p2=(None, None)):
		self._set(p1, p2)
		
	def width(self):
		return abs(self.a[0] - self.b[0])
	
	def height(self):
		return abs(self.a[1] - self.b[1])
	
	def area(self):				
		return self.width() * self.height()
	
	def empty(self):
		r'Vrati pravdu, ak je stvorec prazdny.'
		return self.a == (None, None) or self.b == (None, None)
	
	def center(self):
		r'Vrati stred stvorca ako bod.'
		return (self.a[0]+self.width()/2.0, self.a[1]+self.height()/2.0)
	
	def contains(self, p):
		r'Vrati pravdu ak je bod p ohraniceny stvorcom.'
		return self.a[0] <= p[0] <= self.b[0] and self.a[1] <= p[1] <= self.b[1]
	
	def intersects(self, r):
		r'Vrati pravdu ak je prienik zo stvorcom r neprazdny.'
		return not (abs(r.b[0] - self.a[0]) > self.width() + r.width() 
			or abs(self.b[1] - r.a[1]) > self.height() + r.height())
	
	def unite(self, r):
		r'Zjednotenie so stvorcom r.'
		self.expand(r.a)
		self.expand(r.b)				
	
	def unite_copy(self, r):
		s = rectangle(self.a, self.b)
		s.unite(r)
		return s
	
	def intersect(self, r):
		r'Prienik so stvorcom r.'
		if self.intersects(r):
			p1, p2 = self._intersect(self, r)
			self._set(p1, p2)
		else:
			self._set((None,None), (None,None))
	
	def intersect_copy(self, r):
		r'Vrati prienik so stvorcom r.'
		s = rectangle(self.a, self.b)
		s.intersect(r)
		return s
	
	def adjust(self, dx1, dy1, dx2, dy2):
		r'Posunie hranice strvorca.'
		self.a[0] += dx1
		self.a[1] += dy1
		self.b[0] += dx1+dx2
		self.b[1] += dy1+dy2
	
	def adjust_copy(self, dx1, dy1, dx2, dy2):
		s = rectangle(self.a, self.b)
		s.adjust(dx1, dy1, dx2, dy2)
		return s
	
	def expand(self, p):
		r'Rozsiry stvorec tak, ze bod p bude lezat vo stvorci.'
		if p[0] < self.a[0]:
			self.a[0] = p[0]
		if p[1] < self.a[1]:
			self.a[1] = p[1]
		if p[0] > self.b[0]:
			self.b[0] = p[0]
		if p[1] > self.b[1]:
			self.b[1] = p[1]	
	
	def expand_copy(self, p):
		r = rectangle(self.a, self.b)
		r.expand(p)
		return r
	
	def subset(self, r):
		r'True ak r je podmnozina stvorca.'
		return r.a[0] >= self.a[0] and r.a[1] >= self.a[1] and \
			r.b[0] <= self.b[0] and r.b[1] <= self.b[1]
		
	def _intersect(self, r1, r2):
		p1 = (max(r1.a[0], r2.a[0]), max(r1.a[1], r2.a[1]))
		p2 = (min(r1.b[0], r2.b[0]), min(r1.b[1], r2.b[1]))
		return (p1, p2)
	
	def _set(self, p1, p2):		
		self.a = [min(p1[0], p2[0]), min(p1[1], p2[1])]
		self.b = [max(p1[0], p2[0]), max(p1[1], p2[1])]
	
	def __eq__(self, other):
		return self.a == other.a and self.b == other.b


class polygon:
	def __init__(self):
		self.vertices = []

	def append_vertex(self, v):
		self.vertices.append(v)

	def insert_vertex(self, pos, v):
		pass

	def insert_vertex_shortest(self, v):
		r'''Do polygónu vloží vrchol v, na takú pozíciu, že obvod polygónu zostane
		inimálny.''' 
		pass

	def contains(self, p):
		r'''V smere x-ovej osi vytvor úsečku, tak aby bol jej koniec mimo
		polygonu. Potom spočítaj počet pretnutí úsečky a polygónu. Ak je nepárny
		bod, bod leží v polygóne, inak mimo.'''
		a = p

		by = a[1]

		bx = a[0]
		for v in self.vertices:
			bx = max(bx, v[0]) + 1

		line = line_segment(a, (bx, by))
		
		ncrossings = 0

		i = 1
		while i < len(self.vertices):
			poly_line = line_segment(self.vertices[i-1], self.vertices[i])
			if line.intersect(poly_line):
				ncrossings += 1
			i += 1

		# closing edge
		poly_line = line_segment(self.vertices[-1], self.vertices[0])
		if line.intersect(poly_line):
			ncrossings += 1

		return ncrossings % 2

	def area(self):
		r'Vráti plochu polygónu.'
		pass




	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
