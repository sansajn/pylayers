# -*- coding: utf-8 -*-
# Implementuje vrstvu umožnujúcu zobraziť vof súbor.
# \author Adam Hlavatovič
# \version 20120403
import math
from PyQt4 import QtCore, QtGui, QtNetwork
import layers, vof_dump

class layer(layers.layer_interface):
	def __init__(self, widget):
		layers.layer_interface.__init__(self, widget)
		self.show_verts = True

	# public
	def read_dump(self, fname):
		reader = vof_dump.reader(fname)
		self.process_dump(reader.graph(), reader.path(), reader.fromto())

	# public
	def paint(self, view_offset, zoom, painter):
		self.draw_edges(self.white, view_offset, zoom, (0, 0, 0), painter)
		self.draw_edges(self.grey, view_offset, zoom, (0, 0, 0), painter)
		self.draw_white_verts(self.white_verts, view_offset, zoom, painter)
		self.draw_grey_verts(self.grey_verts, view_offset, zoom, painter)

	def key_press_event(self, e):
		if e.key() == QtCore.Qt.Key_V:
			self.show_verts = not self.show_verts
		
	def draw_edges(self, edges, view_offset, zoom, color, painter):
		brush = painter.brush()
		painter.setBrush(QtGui.QBrush(
			QtGui.QColor(color[0], color[1], color[2])))
		view_rect = self.view_geo_rect(view_offset, zoom)
		ignored = 0
		for e in edges:
			if view_rect.contains(e.source) or view_rect.contains(e.target):
				self.draw_edge(view_offset, zoom, e.source, e.target, painter)
			else:
				ignored += 1
		print 'ignored %d/%d edges' % (ignored, len(edges))
		painter.setBrush(brush)

	def draw_edge(self, view_offset, zoom, f_latlon, t_latlon, painter):
		x0,y0 = view_offset
		x_f, y_f = self.latlon2xy(f_latlon, zoom)
		x_t, y_t = self.latlon2xy(t_latlon, zoom)		
		painter.drawLine(x_f+x0, y_f+y0, x_t+x0, y_t+y0)
	
	def draw_white_verts(self, verts, view_offset, zoom, painter):
		if not self.show_verts:
			return
		brush = painter.brush()
		view_rect = self.view_geo_rect(view_offset, zoom)
		ignored = 0
		for v in verts:
			if view_rect.contains(v):
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
		print 'ignored %d/%d white vertices' % (ignored, len(verts))
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
			if view_rect.contains(v):
				self.draw_vertex(view_offset, zoom, v, painter)
			else:
				ignored += 1
		print 'ignored %d/%d grey vertices' % (ignored, len(verts))
		painter.setBrush(brush)
		
	def draw_vertex(self, view_offset, zoom, latlon, painter):
		vertex_size = 8
		x0,y0 = view_offset
		x,y = self.latlon2xy(latlon, zoom)
		x,y = (x-vertex_size/2, y-vertex_size/2)
		painter.drawEllipse(x+x0, y+y0, vertex_size, vertex_size)

	def process_dump(self, graph, path, fromto):
		self.path = self.process_path_recs(path)
		self.fromto = self.process_fromto(fromto)
		edges = self.process_graph_recs(graph)

		white, grey = self.split_graph_record_set(edges)
		white_verts = self.create_unique_vertex_list(white)
		grey_verts = self.create_unique_vertex_list(grey)

		self.white = {edge(r.source, r.target) for r in white}
		self.white_verts = white_verts
		self.grey = {edge(r.source, r.target) for r in grey}
		self.grey = self.grey.difference(self.white)
		self.grey_verts = grey_verts.difference(white_verts)

	def view_geo_rect(self, view_offset, zoom):
		w,h = self.widget.window_size()
		x0,y0 = view_offset
		xa,ya = (abs(x0), abs(y0)+h)
		a_lat,a_lon = self.xy2latlon((xa, ya), zoom)
		b_lat,b_lon = self.xy2latlon((xa+w, ya-h), zoom)
		return latlon_rect(gpspos(a_lat, a_lon), gpspos(b_lat, b_lon))

	def process_path_recs(self, path):
		return {gpspos(p[1], p[0]) for p in path}

	def process_fromto(self, fromto):
		return [gpspos(p[1], p[0]) for p in fromto]

	def process_graph_recs(self, graph):
		recs = [graph_record(gr) for gr in graph]
		return [r for r in recs if self.has_valid_gps(r)]

	def split_graph_record_set(self, records):
		white = []; grey = []
		for r in records:
			if r.color == Vertex.WHITE:
				white.append(r)
			elif r.color == Vertex.GREY:
				grey.append(r)
			else:
				print 'unknown color:%d' % r.color
		return (white, grey)

	def create_unique_vertex_list(self, edges):
		d = set()
		for e in edges:
			d.add(e.source)
			d.add(e.target)
		return d

	def latlon2xy(self, gpos, zoom):
		lat,lon = (gpos.lat, gpos.lon)
		n = 2**zoom*256
		lat_rad = math.radians(lat)
		x = int((lon+180.0)/360.0 * n)
		y = int((1.0 - math.log(math.tan(lat_rad)+(1/math.cos(lat_rad)))
			/ math.pi) / 2.0*n)
		return (x, y)

	def xy2latlon(self, xy, zoom):
		x,y = xy
		n = 2.0**zoom*256
		lon_deg = x/n*360.0 - 180.0
		lat_rad = math.atan(math.sinh(math.pi * (1 - 2*y/n)))
		lat_deg = math.degrees(lat_rad)
		return (lat_deg, lon_deg)

	def has_valid_gps(self, record):
		return record.source.is_valid() and record.target.is_valid()


class latlon_rect:
	def __init__(self, sw, ne):
		self.sw = sw
		self.ne = ne

	def contains(self, latlon):
		ll = latlon
		return self.sw.lon <= ll.lon and self.ne.lon > ll.lon and \
			self.sw.lat <= ll.lat and self.ne.lat > ll.lat


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

class Vertex:
	BLACK, GREY, WHITE, GREEN = range(0, 4)

class edge:
	def __init__(self, s, t):
		gr = graph_record
		self.source = s
		self.target = t

	def __eq__(self, b):
		return self.source == b.source and self.target == b.target

	def __hash__(self):
		return self.target.__hash__()

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


