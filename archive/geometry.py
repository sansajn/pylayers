# -*- coding: utf-8 -*-
# Geometry routines.
# \author Adam Hlavatovič

r'''Bod je definovany ako akykolvek objekt p, pre ktory platia vyrazy 
p[0], p[1] a v pripade bodu v priestore aj p[2].'''

class rectangle:
	r'Stvorec je definovany lavym-dolnym bodom a a pravym-hornym bodom b.'
	def __init__(self, p1, p2):
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
		
	def _intersect(self, r1, r2):
		p1 = (max(r1.a[0], r2.a[0]), max(r1.a[1], r2.a[1]))
		p2 = (min(r1.b[0], r2.b[0]), min(r1.b[1], r2.b[1]))
		return (p1, p2)
	
	def _set(self, p1, p2):
		self.a = [min(p1[0], p2[0]), min(p1[1], p2[1])]
		self.b = [max(p1[0], p2[0]), max(p1[1], p2[1])]
	
	def __eq__(self, other):
		return self.a == other.a and self.b == other.b


if __name__ == '__main__':  # simple tests
	r = rectangle((5, 0), (15, 10))
	s = rectangle((8, 8), (15, 18))
	t = rectangle((20, 20), (30, 25))
	
	print('width() %s' % ('passed' if r.width() == 10 else 'failed'))
	print('height() %s' % ('passed' if r.height() == 10 else 'failed'))
	print('empty() %s' % ('passed' if r.empty() == False else 'failed'))
	print('center() %s' % ('passed' if r.center() == (10, 5) else 'failed'))
	print('contains() %s' % ('passed' if r.contains((8, 8)) == True 
		and r.contains((15, 15)) == False else 'failed'))
	print('intersects() %s' % ('passed' if r.intersects(s) == True 
		and r.intersects(t) == False else 'failed'))
		
	print('intersect() %s' % ('passed' 
		if r.intersect_copy(s) == rectangle((8,8), (15,10)) 
			and r.intersect_copy(t) == rectangle((None,None), (None,None)) 
		else 'failed'))
	
	print('unite() %s' % ('passed' 
		if r.unite_copy(s) == rectangle((5, 0), (15, 18)) else 'failed'))
	
	print('expand() %s' % ('passed' 
		if s.expand_copy((-2, 30)) == rectangle((-2, 8), (15, 30)) else 'failed'))
	
	print('adjust() %s' % ('passed' 
		if r.adjust_copy(5, 3, 10, 10) == rectangle((10, 3), (30, 23)) else 'failed'))
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	