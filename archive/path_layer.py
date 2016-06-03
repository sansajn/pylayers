# -*- coding: utf-8 -*-
# Implementuje vrstvu umožnujúcu zobraziť path_dump súbory.
# \author Adam Hlavatovič
# \version 20120403
import math, threading
from PyQt4 import QtCore, QtGui, QtNetwork
import layers, path_dump


RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
VIOLET = (111, 89, 255)
YELLOW = (255, 239, 20)

def MakeColor(c):
	return QtGui.QColor(c[0], c[1], c[2])

COLOR = {
	'standard' : MakeColor(BLACK),
	'diff' : MakeColor(RED),
	'alternative' : MakeColor(VIOLET),
	'source' : MakeColor(GREEN),
	'target' : MakeColor(BLUE),
	'common' : MakeColor(YELLOW),
	'primary' : MakeColor(WHITE),
	'black' : MakeColor(BLACK)
}

PEN = {
	'standard' : QtGui.QPen(COLOR['standard']),
	'diff' : QtGui.QPen(COLOR['diff']),
	'alternative' : QtGui.QPen(COLOR['alternative']),
	'source' : QtGui.QPen(COLOR['source']),
	'target' : QtGui.QPen(COLOR['target']),
	'common' : QtGui.QPen(COLOR['common']),
	'primary' : QtGui.QPen(COLOR['standard']),
	'black' : QtGui.QPen(COLOR['black'])
}

BRUSH = {
	'standard' : QtGui.QBrush(COLOR['standard']),
	'diff' : QtGui.QBrush(COLOR['diff']),
	'alternative' : QtGui.QBrush(COLOR['alternative']),
	'source' : QtGui.QBrush(COLOR['source']),
	'target' : QtGui.QBrush(COLOR['target']),
	'common' : QtGui.QBrush(COLOR['common']),
	'primary' : QtGui.QBrush(COLOR['primary'])
}


class layer(layers.layer_interface):
	def __init__(self, widget):
		layers.layer_interface.__init__(self, widget)
		self.paths = []
		self.path_idx = 0
		self.diff_paths = {}  #!< zoznam rozdielnych ciest
		self.diff_paths_avail = False
		self.ndiff_edges = 0  #!< for filtered path iteration
		self.diff_primary_alter = []  #!< for draw_path() function
		self.edges = drawable_group()
		self.verts = drawable_vertices()
		self.view_offset = (0, 0)

	#@{ layer_interface

	# public
	def create(self, fname):
		reader = path_dump.reader()
		self.paths = reader.read(fname)		

		# compute dump stats in another thread
		self.dump_stats_thread = dump_stats(fname)
		self.widget.connect(self.dump_stats_thread, QtCore.SIGNAL('done'),
			self.stats_processed)
		self.dump_stats_thread.start()

	# public
	def paint(self, painter):
		self.view_offset = self.widget.view_offset
		self.draw_scene(self.view_offset, painter)

	# public
	def key_press_event(self, e):
		if e.key() == QtCore.Qt.Key_N:
			self.next_path()			
		elif e.key() == QtCore.Qt.Key_P:
			self.prev_path()
		else:
			return
		self.create_drawable_data()

	# public
	def zoom_event(self, zoom):
		layers.layer_interface.zoom_event(self, zoom)
		self.create_drawable_data()

	# public
	def mouse_press_event(self, event):
		print '#path_layer::mouse_press_event()'
		if event.buttons() & QtCore.Qt.LeftButton:
			x0,y0 = self.view_offset
			self.verts.down_event((event.x()-x0, event.y()-y0))

	#@} layer_interface

	def draw_scene(self, view_offset, painter):
		# edges
		old_pen = painter.pen()
		painter.setPen(PEN['black'])
		self.edges.paint(view_offset, painter)

		# verts
		painter.setPen(PEN['black'])
		old_brush = painter.brush()
		painter.setBrush(BRUSH['primary'])
		self.verts.primary.paint(view_offset, painter)
		
		painter.setBrush(BRUSH['common'])
		self.verts.common.paint(view_offset, painter)

		painter.setBrush(BRUSH['diff'])
		self.verts.diff.paint(view_offset, painter)

		painter.setBrush(BRUSH['alternative'])
		self.verts.alternative.paint(view_offset, painter)

		painter.setBrush(BRUSH['source'])
		self.verts.source.paint(view_offset, painter)

		painter.setBrush(BRUSH['target'])
		self.verts.target.paint(view_offset, painter)

		self.draw_legend((5, 5), painter)

		painter.setPen(old_pen)
		painter.setBrush(old_brush)


	def draw_item_set(self, items, view_offset, painter):
		for item in items:
			item.paint(view_offset, painter)


	def create_drawable_data(self):
		self.verts.clear()
		self.edges.clear()
		self.process_path(0)
		if self.path_idx > 0:
			self.process_path(self.path_idx)

		# stats
		print '#path_layerc::reate_drawable_data()'
		print 'primary:%d' % (len(self.verts.primary), )
		print 'common:%d' % (len(self.verts.common), )
		print 'diff:%d' % (len(self.verts.diff), )
		print 'alternative:%d' % (len(self.verts.alternative), )
		print 'edges:%d' % (len(self.edges), )
		

	def process_path(self, idx):
		path = self.paths[idx]
		diffs = self.diff_primary_alter
		
		is_alternative_subpath = False
		alternative_from, alternative_to = ([], [])
		if idx > 0:
			alternatives = alternative_subpaths(self.paths[0],	self.paths[idx])
			if len(alternatives) > 0:
				alternative_from, alternative_to = split_collumns(alternatives)
		
		i = 0
		while i < len(path)-1:
			u = path[i]
			v = path[i+1]

			vtype = VERTEX_TYPE.UNKNOWN

			if i in alternative_from:
				is_alternative_subpath = True
			elif i in alternative_to:
				is_alternative_subpath = False
			
			if i == 0:		
				vtype = VERTEX_TYPE.SOURCE
			elif i+1 == len(path)-1:
				vtype = VERTEX_TYPE.TARGET
			elif idx > 0:
				if is_alternative_subpath:
					vtype = VERTEX_TYPE.ALTERNATIVE
				elif i in diffs:  # difs
					vtype = VERTEX_TYPE.DIFF
				else:  # common vetrices
					vtype = VERTEX_TYPE.COMMON
			else:
				vtype = VERTEX_TYPE.PRIMARY
				
			if i == 0:
				self.append_drawable_vertex(u, VERTEX_TYPE.SOURCE)
			else:
				self.append_drawable_vertex(v, vtype)

			self.edges.append(
				drawable_edge(self.latlon2xy(self.ap2gp(u), self.zoom),
					self.latlon2xy(self.ap2gp(v), self.zoom)))
			
			i += 1

	def append_drawable_vertex(self, v, vert_type):
		vert = drawable_vertex(self.latlon2xy(self.ap2gp(v), self.zoom), 3)
		if vert_type == VERTEX_TYPE.PRIMARY:
			self.verts.primary.append(vert)
		elif vert_type == VERTEX_TYPE.COMMON:
			self.verts.common.append(vert)
		elif vert_type == VERTEX_TYPE.DIFF:
			self.verts.diff.append(vert)
		elif vert_type == VERTEX_TYPE.ALTERNATIVE:
			self.verts.alternative.append(vert)
		elif vert_type == VERTEX_TYPE.SOURCE:
			self.verts.source.append(vert)
		elif vert_type == VERTEX_TYPE.TARGET:
			self.verts.target.append(vert)
		else:
			print 'Unknown vertex type!'

				
	def draw_legend(self, pos, qp):
		text = 'Keys: N=next, P=previous\n'
		text += 'Path:%d/%d\n' % (self.path_idx, len(self.paths)-1)

		ndiffs = len(find_diffs(self.paths, self.path_idx))
		nedges = len(self.paths[self.path_idx])-1
		text += 'Edges:%d (diffs:%d, length:%d)' % (
			nedges, ndiffs, (len(self.paths[0])-1) - nedges)

		if self.diff_paths_avail:
			text += '\nDiff paths: %d %s'  % (len(self.diff_paths),
				self.most_diffs_paths())
		
		old_font = qp.font()
		font = QtGui.QFont('Arial', 10)
		frect = QtGui.QFontMetrics(font).boundingRect(text)
		qp.setFont(font)
		qp.drawText(QtCore.QRect(5, 5, frect.width(), 4*frect.height()), 
			0, text)
		qp.setFont(old_font)

	def next_path(self):
		if self.ndiff_edges == 0:
			self.path_idx = (self.path_idx+1) % len(self.paths)
			self.widget.standard_update()
		else:
			i = self.path_idx+1
			while i < len(self.paths):
				ndiffs = find_diffs(self.paths, i)
				if len(ndiffs) >= self.ndiff_edges:
					self.path_idx = i
					self.widget.standard_update()
					return
				i += 1
		self.diff_primary_alter = find_diffs(self.paths, self.path_idx)
				
	def prev_path(self):
		if self.ndiff_edges == 0:
			if self.path_idx == 0:
				self.path_idx = len(self.paths)
			self.path_idx -= 1
			self.widget.standard_update()
		else:
			i = self.path_idx-1
			while i > 0:
				ndiffs = self.find_diffs(i)
				if len(ndiffs) >= self.ndiff_edges:
					self.path_idx = i
					self.widget.standard_update()
					return
				i -= 1
		self.diff_primary_alter = find_diffs(self.paths, self.path_idx)			

	def most_diffs_paths(self):
		if len(self.diff_paths):
			text = ' ['
			items = dict_sort_by_val(self.diff_paths)
			items.reverse()
			if len(items) > 5:
				items = items[0:5]
			for k,v in items[0:-1]:
				text += '%d:%d, ' % (k,v)
			text += '%d:%d' % (items[len(items)-1][0], items[len(items)-1][1])
			if len(self.diff_paths) > 5:
				text += ', ...]'
			else:
				text += ']'
			return text
		else:
			return ''

	def latlon2xy(self, gpos, zoom):
		lat,lon = gpos
		n = 2**zoom*256
		lat_rad = math.radians(lat)
		x = int((lon+180.0)/360.0 * n)
		y = int((1.0 - math.log(math.tan(lat_rad)+(1/math.cos(lat_rad)))
			/ math.pi) / 2.0*n)
		return (x, y)

	def ap2gp(self, apos):
		return [apos[0]/1e5, apos[1]/1e5]

	def stats_processed(self):
		self.diff_paths_avail = True
		self.diff_paths = self.dump_stats_thread.diff_paths
		self.widget.standard_update()


class dump_stats(QtCore.QObject, threading.Thread):
	def __init__(self, filename):
		QtCore.QObject.__init__(self)
		threading.Thread.__init__(self)
		self.diff_paths = {}
		self.filename = filename

	def run(self):
		reader = path_dump.reader()
		paths = reader.read(self.filename)
		self.find_diff_paths(paths)
		self.emit(QtCore.SIGNAL('done'))	
		print 'Dump statistics (dump_stats thread) done, %d paths analyzed!'\
			% (len(paths), )

	def find_diff_paths(self, paths):
		i = 1
		while i < len(paths):
			diffs = find_diffs(paths, i)
			if len(diffs) > 0:
				self.diff_paths[i] = len(diffs)
			i += 1


def find_diffs(paths, path_idx):
	r'Najde rozdielne hrany v ceste v porovnaní s referenčnou cestou.'
	diffs = []
	ref_path = paths[0]
	path = paths[path_idx]
	nedges = len(path)-1		
	i = 0
	last_found = -1
	while i < nedges:
		e = (path[i], path[i+1])
		idx = list_find(ref_path, last_found+1, e[0])
		if idx == len(ref_path)-1:
			diffs.extend(range(i, nedges))
			break
		elif idx != None and ref_path[idx+1] == e[1]:
			last_found = idx
		else:
			diffs.append(i)
		i += 1
	return diffs

def list_find(lst, pos, val):
	i = pos
	while i < len(lst):
		if lst[i] == val:
			return i;
		i += 1
	return None

def dict_sort_by_val(d):
	items = d.items()
	swapped = [swap_pair(i) for i in items]
	swapped.sort()
	return [swap_pair(i) for i in swapped]

def swap_pair(p):
	return [p[1], p[0]]


# alternatives

def alternative_subpaths(a, b):
	alternatives = []
	c = common_points(a, b)
	for i in range(0, len(c)-1):
		couple = (c[i], c[i+1])
		subpath = middle_points(b, couple)
		if len(subpath) > small_enough(b):
			alternatives.append(couple)
	return alternatives

def common_points(a, b):
	c = []
	last_idx = -1
	for p in a:
		idx = find(b, p, last_idx+1)
		if idx != None:
			c.append(idx)
			last_idx = idx
	return c

def middle_points(a, bounds):
	return a[bounds[0]+1:bounds[1]]

def small_enough(what):
	return max(5, len(what)/10)

def almoust_all(where, what):
	count = 0
	for x in where:
		if x == what:
			count += 1
	k = count/float(len(where))
	return (k > 0.8, k)

def append_if_not_none(where, what):
	if what != None:
		where.append(what)

def find(where, what, offset):
	idx = None
	for i in range(offset, len(where)):
		if where[i] == what:
			idx = i
	return idx

def count_values(where, what):
	count = 0
	for x in where:
		if x == what:
			count += 1
	return count

def split_collumns(t):
	colls = []
	for i in range(0, len(t[0])):
		colls.append([])
	for r in range(0, len(t)):
		for c in range(0, len(t[r])):
			colls[c].append(t[r][c])
	return colls
		

# drawable

class drawable_vertex:
	def __init__(self, center, r):
		self.r = r
		self.center = QtCore.QPoint(center[0], center[1])
		self.down = False

	def is_down(self):
		return self.down

	def set_down(self, state):
		self.down = state

	def contains(self, pos):
		d = math.sqrt((self.center.x() - pos[0])**2 + 
			(self.center.y() - pos[1])**2)
		return d < self.r

	def down_event(self):
		self.down = not self.down
		print 'I was clicked!'
		
	def paint(self, view_offset, painter):
		x0,y0 = view_offset
		c = QtCore.QPoint(self.center.x()+x0, self.center.y()+y0)
		painter.drawEllipse(c, self.r, self.r)


class drawable_edge:
	def __init__(self, s, t):
		self.s = s
		self.t = t

	def paint(self, view_offset, painter):
		x0,y0 = view_offset
		painter.drawLine(self.s[0]+x0, self.s[1]+y0, 
			self.t[0]+x0, self.t[1]+y0)



class drawable_vertices:
	def __init__(self):
		self.init()

	def init(self):
		self.primary = drawable_group()
		self.common = drawable_group()
		self.diff = drawable_group()
		self.alternative = drawable_group()
		self.source = drawable_group()
		self.target = drawable_group()
		self.group = [self.primary, self.common, self.diff, self.alternative,
			self.source, self.target]

	def down_event(self, pos):
		for drawables in self.group:
			if drawables.down_event(pos):
				return

	def clear(self):
		self.init()


class drawable_group:
	def __init__(self):
		self.group = []

	# \param drawable must implment drawable_interface.
	def append(self, drawable):
		self.group.append(drawable)

	def clear(self):
		self.group = []

	def paint(self, view_offset, painter):
		for elem in self.group:
			elem.paint(view_offset, painter)

	def down_event(self, pos):
		for elem in self.group:
			if elem.contains(pos):
				elem.down_event()
				return True
		return False

	def __len__(self):
		return len(self.group)


class VERTEX_TYPE:
	UNKNOWN = -1
	PRIMARY, COMMON, DIFF, ALTERNATIVE, SOURCE, TARGET = range(0, 6)

