# -*- coding: utf-8 -*-
import re

class reader:
	# public
	def read(self, filename):
		r'''Vráti cesty ako zoznam pozícii [(y,x), ...], kde x a y sú celé
		čísla lat*1e5, lon*1e5.'''
		dump = open(filename, 'r')
		paths = []
		for ln in dump:
			path = self.parse_path(ln)
			if len(path) > 0:
				paths.append(path)
		dump.close()
		return paths

	def parse_path(self, ln):
		integer_expr = r'-?\d+'
		float_expr = r'-?(?:\d+\.\d+|\d*\.\d+)'
		scient_expr = r'-?\d(?:\.\d+|)[Ee][+\-]?\d\d*'
		real_expr = r'(?:' + scient_expr + '|' + float_expr + '|' \
			+ integer_expr + r')'

		ilatlon_expr = integer_expr + ' ' + integer_expr
		expr = r'(%s),?' % (ilatlon_expr, )
		
		path = []
		last_index = 0
		while True:
			m = re.search(expr, ln[last_index:])
			if m == None:
				break
			lat, lon = m.group(1).split(' ')
			path.append((int(lat), int(lon)))
			last_index += m.end(0)

		return path

