# -*- coding: utf-8 -*-
# Allows to reads vof files.
# \author Adam Hlavatovič
# \version 20120322
import re

integer_expr = r'-?\d+'
float_expr = r'-?(?:\d+\.\d+|\d*\.\d+)'
scient_expr = r'-?\d(?:\.\d+|)[Ee][+\-]?\d\d*'
real_expr = r'(?:' + scient_expr + '|' + float_expr + '|' \
	+ integer_expr + r')'

class reader:  
	r'Visitor output file reader.'
	# vof sections
	UNKNOWN, DESCRIPTION, FROM_TO, GRAPH, PATH = range(1, 6)

	def __init__(self, fname):
		self._line = 0
		self._section = reader.UNKNOWN
		self._desc = None
		self._fromto = None
		self._path = None
		self._path = None		
		self._readvof(fname)

	# public 
	def description(self):
		return self._desc

	# public
	def fromto(self):
		r'Vráti dvojicu lonlat pozícii (počiatočnú a koncovú).'
		return self._fromto

	# public
	def graph(self):
		r'Vráti zoznam hrán s grafovej sekcie.'
		return self._graph

	# public
	def path(self):
		r'Vráti zoznam lonlat pozícii vrcholou tvoriacich cestu.'
		return self._path

	def _readvof(self, fname):
		vof = open(fname, 'r')
		self._voflines = vof.readlines()

		while self._line < len(self._voflines):
			ln = self._next_line()
			if self._section_header(ln):
				self._section = self._parse_section_header(ln)
			
			if self._section == reader.DESCRIPTION:
				self._desc = self._read_description_sec()
			elif self._section == reader.FROM_TO:
				self._fromto = self._read_fromto_sec()
			elif self._section == reader.GRAPH:
				self._graph = self._read_graph_sec()
			elif self._section == reader.PATH:
				self._path = self._read_path_sec()

		self._voflines = []
		vof.close()

	def _read_graph_sec(self):
		edges = []
		for ln in self._voflines[self._line:]:
			if self._section_header(ln):
				break

			ge = self._parse_graph_line(ln)
			if ge != None:
				edges.append(ge)
			else:
				print "line '%s' ignored" % ln

			self._line += 1

		self._section = reader.UNKNOWN
		return edges
					
	def _parse_graph_line(self, ln):
		vertex_expr = r'(%s) (%s) (%s) (%s) (%s) (%s) (%s) (%s) (%s) (%s) '\
			'(%s) (%s) (%s) (%s)' % (float_expr, float_expr, float_expr, 
				float_expr, integer_expr, integer_expr, integer_expr, 
				integer_expr, integer_expr, integer_expr, integer_expr, 
				integer_expr, float_expr, float_expr)

		ma = re.match(vertex_expr, ln)
		if ma != None:
			return {
				'lon-from': float(ma.group(1)), 
				'lat-from': float(ma.group(2)), 
				'lon-to': float(ma.group(3)),
				'lat-to': float(ma.group(4)),
				'road-offset': int(ma.group(5)),
				'end-road-offset': int(ma.group(6)),
				'order': int(ma.group(7)),
				'graph': int(ma.group(8)),
				'level': int(ma.group(9)),
				'speed-category': int(ma.group(10)),
				'road-class': int(ma.group(11)),
				'color': int(ma.group(12)),
				'cost': float(ma.group(13)),
				'penalty': float(ma.group(14))
			}
		else:						
			return None

	def _read_description_sec(self):
		desc = self._parse_description_line(self._voflines[self._line])
		self._line += 1
		if desc == None:
			raise Exception('Bad description section format.')
		else:
			self._section = reader.UNKNOWN
			return desc

	def _read_fromto_sec(self):
		r'''Vráti dvojicu (<from>, <to>), kde <from> a <to> sú dvojica
			(<lng>, <lat>).'''
		expr = r'(%s) (%s)' % (float_expr, float_expr)
		
		ln = self._next_line()
		ma = re.match(expr, ln)
		if ma == None:
			raise Exception('Bad from-to section format')
		from_coord = (float(ma.group(1)), float(ma.group(2)))
		
		ln = self._next_line()
		ma = re.match(expr, ln)
		if ma == None:
			raise Exception('Bad from-to section format')
		to_coord = (float(ma.group(1)), float(ma.group(2)))

		self._section = reader.UNKNOWN
		return (from_coord, to_coord)

	def _read_path_sec(self):
		path = []
		for ln in self._voflines[self._line:]:
			if self._section_header(ln):
				break
			self._line += 1

			expr = r'(%s) (%s)' % (float_expr, float_expr)
			ma = re.match(expr, ln)
			if ma != None:
				path.append((float(ma.group(1)), float(ma.group(2))))
			else:
				print "line '%s' ignored" % ln

		self._section = reader.UNKNOWN
		return path

	def _section_header(self, ln):
		expr = r'# \w+.*'	
		ma = re.match(expr, ln)
		if ma == None:
			return None
		else:
			return 1

	def _parse_section_header(self, ln):
		expr = r'# (description|from-to|graph|path)'		
		ma = re.match(expr, ln)
		if ma != None:
			sec = ma.group(1)
			if sec == 'description':
				return reader.DESCRIPTION
			elif sec == 'from-to':
				return reader.FROM_TO
			elif sec == 'graph':
				return reader.GRAPH
			elif sec == 'path':
				return reader.PATH
		else:
			raise Exception("Unknown section '%s'." % (ln,))

	def _next_line(self):
		self._line += 1
		return self._voflines[self._line-1]

