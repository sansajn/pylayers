# -*- coding: utf-8 -*-
# Implementuje vrstvu umožnujúcu zobraziť vof súbor.
# \author Adam Hlavatovič
# \version 20120403
import math
from PyQt4 import QtCore, QtGui, QtNetwork
import layers, vof_dump


class layer(layers.layer_interface):
	def __init__(self, widget, zoom):
		layers.layer_interface.__init__(self, widget)
		self.zoom = zoom
		self.show_verts = True

	# public
	def create(self, fname):
		reader = vof_dump.reader(fname)
		self.process_dump(reader.graph(), reader.path(), reader.fromto())

	# public
	def paint(self, view_offset, painter):
		zoom = self.zoom
		self.draw_edges(self.white, view_offset, zoom, (0, 0, 0), painter)
		self.draw_edges(self.grey, view_offset, zoom, (0, 0, 0), painter)
		self.draw_white_verts(self.white_verts, view_offset, zoom, painter)
		self.draw_grey_verts(self.grey_verts, view_offset, zoom, painter)

	# public
	def key_press_event(self, e):
		if e.key() == QtCore.Qt.Key_V:
			self.show_verts = not self.show_verts

	# public
	def zoom_event(self, zoom):
		layers.layer_interface.zoom_event(self, zoom)
		self.calculate_vertices_xy(self.white_verts)
		self.calculate_vertices_xy(self.grey_verts)
		

	def draw_edges(self, edges, view_offset, zoom, color, painter):
		brush = painter.brush()
		painter.setBrush(QtGui.QBrush(
			QtGui.QColor(color[0], color[1], color[2])))
		view_rect = self.view_geo_rect(view_offset, zoom)
		ignored = 0
		
		for e in edges:
			if view_rect.contains(e.source.gpos)\
				or	view_rect.contains(e.target.gpos):
				self.draw_edge(view_offset, zoom, e.source.gpos,
					e.target.gpos, painter)
			else:
				ignored += 1
		print 'ignored %g edges' % (ignored/len(edges), )
		painter.setBrush(brush)

	def draw_edge(self, view_offset, zoom, f_latlon, t_latlon, painter):
		x0,y0 = view_offset
		x_f, y_f = mercator.gps2xy(f_latlon, zoom)
		x_t, y_t = mercator.gps2xy(t_latlon, zoom)		
		painter.drawLine(x_f+x0, y_f+y0, x_t+x0, y_t+y0)
	
	def draw_white_verts(self, verts, view_offset, zoom, painter):
		if not self.show_verts:
			return
		brush = painter.brush()
		view_rect = self.view_geo_rect(view_offset, zoom)
		ignored = 0
		for v in verts:
			if view_rect.contains(v.gpos):
				color = (255, 255, 255)
				if v == self.fromto[0]:
					color = (255, 0, 0)
				elif v == self.fromto[1]:
					color = (0, 0, 255)
				elif v in self.path:
					color = (0, 255, 0)
				painter.setBrush(QtGui.QBrush(
					QtGui.QColor(color[0], color[1],	color[2])))
				self.draw_vertex(view_offset, zoom, v, painter)
			else:
				ignored += 1
		print 'ignored %g%% white vertices' % (ignored/len(verts)*100, )
		painter.setBrush(brush)

	def draw_grey_verts(self, verts, view_offset, zoom, painter):
		if not self.show_verts:
			return
		self.draw_verts(verts, view_offset, zoom, (128, 128, 128), painter)
	
	def draw_verts(self, verts, view_offset, zoom, color, painter):
		brush = painter.brush()
		painter.setBrush(QtGui.QBrush(
			QtGui.QColor(color[0], color[1], color[2])))
		view_rect = self.view_geo_rect(view_offset, zoom)
		ignored = 0
		for v in verts:
			if view_rect.contains(v.gpos):
				self.draw_vertex(view_offset, zoom, v, painter)
			else:
				ignored += 1
		print 'ignored %g%% grey vertices' % (ignored/len(verts)*100, )
		painter.setBrush(brush)
		
	def draw_vertex(self, view_offset, zoom, v, painter):
		vertex_size = 8
		x0,y0 = view_offset
		x,y = v.xypos
		x,y = (x-vertex_size/2, y-vertex_size/2)
		painter.drawEllipse(x+x0, y+y0, vertex_size, vertex_size)

	def process_dump(self, graph, path, fromto):
		self.path = self.process_path_recs(path)
		self.fromto = self.process_fromto(fromto)
		edges = self.process_graph_recs(graph)

		white, grey = self.split_graph_record_set(edges)

		white_verts = {vertex(gpos) 
			for gpos in self.create_unique_gpos_set(white)}
		self.calculate_vertices_xy(white_verts)
		self.white_verts = white_verts

		grey_verts = {vertex(gpos)
			for gpos in self.create_unique_gpos_set(grey)}
		self.grey_verts = grey_verts.difference(white_verts)	
		self.calculate_vertices_xy(grey_verts)

		self.white = {edge(vertex(r.source), vertex(r.target)) for r in white}
		self.grey = {edge(vertex(r.source), vertex(r.target)) for r in grey}
		self.grey = self.grey.difference(self.white)


	def calculate_vertices_xy(self, verts):
		for v in verts:
			v.calculate_xy(self.zoom)

	def calculate_edges_xy(self, verts):
		for e in edge:
			e.source.calculate_xy(self.zoom)
			e.target.calculate_xy(self.zoom)

	def view_geo_rect(self, view_offset, zoom):
		w,h = self.widget.window_size()
		x0,y0 = view_offset
		xa,ya = (abs(x0), abs(y0)+h)
		a_gpos = mercator.xy2gps((xa, ya), zoom)
		b_gpos = mercator.xy2gps((xa+w, ya-h), zoom)
		return latlon_rect(a_gpos, b_gpos)

	def process_path_recs(self, path):
		return {vertex(gpspos(p[1], p[0])) for p in path}

	def process_fromto(self, fromto):
		return [vertex(gpspos(p[1], p[0])) for p in fromto]

	def process_graph_recs(self, graph):
		recs = [graph_record(gr) for gr in graph]
		return [r for r in recs if self.has_valid_gps(r)]

	def split_graph_record_set(self, records):
		white = []; grey = []
		for r in records:
			if r.color == vertex.WHITE:
				white.append(r)
			elif r.color == vertex.GREY:
				grey.append(r)
			else:
				print 'unknown color:%d' % r.color
		return (white, grey)

	def create_unique_gpos_set(self, edges):
		d = set()
		for e in edges:
			d.add(e.source)
			d.add(e.target)
		return d

	def has_valid_gps(self, record):
		return record.source.is_valid() and record.target.is_valid()


class latlon_rect:
	r'Geographical rectangle.'
	def __init__(self, sw, ne):
		self.sw = sw
		self.ne = ne

	def contains(self, gpos):
		return self.sw.lon <= gpos.lon and self.ne.lon > gpos.lon and \
			self.sw.lat <= gpos.lat and self.ne.lat > gpos.lat


class edge:
	def __init__(self, s, t):
		self.source = s
		self.target = t

	def __eq__(self, b):
		return self.source == b.source and self.target == b.target

	def __hash__(self):
		return self.target.__hash__()


class vertex:
	BLACK, GREY, WHITE, GREEN = range(0, 4)

	def __init__(self, gpos):
		self.gpos = gpos
		self.xypos = (-1, -1)

	def calculate_xy(self, zoom):
		self.xypos = mercator.gps2xy(self.gpos, zoom)

	def __eq__(self, b):
		return self.gpos == b.gpos

	def __hash__(self):
		return self.gpos.__hash__()

		
class gpspos:
	def __init__(self, lat, lon):
		self.lat = lat
		self.lon = lon

	def is_valid(self):
		return self.lat >= -180.0 and self.lat <= 180.0 and \
			self.lon >= -180.0 and self.lon <= 180.0

	def __eq__(self, b):
		return self.lat == b.lat and self.lon == b.lon

	def __hash__(self):
		a=int(self.lon*1e5); b=int(self.lat*1e5)
		return b<<32|a

class mercator:
	@staticmethod
	def gps2xy(gpos, zoom):
		r'\param gpos gpspos(lat, lon)'
		lat,lon = (gpos.lat, gpos.lon)
		n = 2**zoom*256
		lat_rad = math.radians(lat)
		x = int((lon+180.0)/360.0 * n)
		y = int((1.0 - math.log(math.tan(lat_rad)+(1/math.cos(lat_rad)))
			/ math.pi) / 2.0*n)
		return (x, y)

	@staticmethod
	def xy2gps(xypos, zoom):
		r'\param xypos (x,y)'
		x,y = xypos
		n = 2.0**zoom*256
		lon_deg = x/n*360.0 - 180.0
		lat_rad = math.atan(math.sinh(math.pi * (1 - 2*y/n)))
		lat_deg = math.degrees(lat_rad)
		return gpspos(lat_deg, lon_deg)


class graph_record:
	def __init__(self, record):
		gr = record
		self.source = gpspos(gr['lat-from'], gr['lon-from'])
		self.target = gpspos(gr['lat-to'], gr['lon-to'])
		self.road_offset = gr['road-offset']
		self.end_road_offset = gr['end-road-offset']
		self.order = gr['order']
		self.graph = gr['graph']
		self.level = gr['level']
		self.speed_cat = gr['speed-category']
		self.road_class = gr['road-class']
		self.color = gr['color']
		self.cost = gr['cost']
		self.penalty = gr['penalty']

