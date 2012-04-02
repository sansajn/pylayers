# -*- coding: utf-8 -*-
# \author Adam Hlavatovič
# \version 20120330
import sys, math, time, os
from PyQt4 import QtCore, QtGui, QtNetwork
import path_dump, vof_dump


def main(args):
	app = QtGui.QApplication(args)
	form = Form()
	form.show()
	app.exec_()


class Form(QtGui.QMainWindow):
	class paint_reason:
		TILE_CHANGED = 0
		STANDARD_REDRAW = 1
		def __init__(self):
			self.data = 0
			self.reason = self.STANDARD_REDRAW

	def __init__(self):
		QtGui.QMainWindow.__init__(self, None)
		self.view_offset = (0, 0)
		self.click_pos = (0, 0)
		self.zoom = 2
		self.resize(800, 600)
		self.image_cache = {}
		self.requested_tiles = set()
		self.paint_reason = Form.paint_reason()
		self.layers = []

		self.network = QtNetwork.QNetworkAccessManager()
		self.connect(self.network, QtCore.SIGNAL(
			'finished(QNetworkReply *)'),	self.tile_reply_event)
		self.disk_cache = QtNetwork.QNetworkDiskCache()
		self.disk_cache.setCacheDirectory(os.path.join(temp_directory(), 
			'tiles'))
		self.disk_cache.setMaximumCacheSize(500*2**20)
		self.network.setCache(self.disk_cache)

	
	def paintEvent(self, e):
		t = time.clock()
		qp = QtGui.QPainter()
		qp.begin(self)

		if self.paint_reason.reason == Form.paint_reason.TILE_CHANGED:
			self.draw_tile(self.paint_reason.data, qp)
		else:
			self.draw_map(qp)

		for layer in self.layers:
			layer.paint(self.view_offset, self.zoom, qp)

		qp.end()
		dt = time.clock() - t
		print 'paint event: %f' % (dt, )


	def draw_map(self, qp):
		y,x = self.visible_tiles()
		for i in range(y[0], y[1]):
			for j in range(x[0], x[1]):
				tile = self.load_tile_from_image_cache(j, i)
				if tile == None:
					tile = self.load_tile_from_disk_cache(j, i)
					if tile:
						self.insert_tile_to_image_cache(tile, j, i)
				if tile:
					self.draw_tile(tile, j, i, qp)

	def draw_tile(self, tile, x, y, qp):
		x0,y0 = self.view_offset
		qp.drawImage(QtCore.QPoint(x*256+x0, y*256+y0), tile)

	def load_tile_from_image_cache(self, x, y):
		return self.find_in_image_cache(x, y, self.zoom)

	def load_tile_from_disk_cache(self, x, y):
		url = QtCore.QUrl(self.construct_tile_url(x, y, self.zoom))
		cache_item = self.disk_cache.data(url)
		if cache_item:
			tile = QtGui.QImage()
			tile.load(cache_item, 'PNG')
			return tile
		else:
			return None

	def insert_tile_to_image_cache(self, tile, x, y):
		if y in self.image_cache:
			self.image_cache[y][x] = tile
		else:
			self.image_cache[y] = {x:tile}

	def map_changed(self):
		print '#map_changed()'
		tiles = self.tiles_not_in_cache(self.visible_tiles())
		for t in tiles:
			self.tile_request(t[1], t[0], self.zoom)
		self.standard_update()

	def tile_request(self, x, y, z):
		if (x, y, z) in self.requested_tiles:
			return
		url = QtCore.QUrl(self.construct_tile_url(x, y, z))
		request = QtNetwork.QNetworkRequest()		
		request.setUrl(url)
		request.setRawHeader('User-Agent', 'PySlippyMap client')
		request.setAttribute(QtNetwork.QNetworkRequest.CacheLoadControlAttribute,
			QtNetwork.QNetworkRequest.PreferCache)
		request.setAttribute(
			QtNetwork.QNetworkRequest.HttpPipeliningAllowedAttribute, True)
		request.setAttribute(QtNetwork.QNetworkRequest.User, (x, y, z))
		self.requested_tiles.add((x, y, z))
		self.network.get(request)

	def tile_reply_event(self, reply):
		if reply.error():
			print '\n#tile_reply_event(): error=%d' % (reply.error(),)
			return

		tile_id = reply.request().attribute(
			QtNetwork.QNetworkRequest.User).toPyObject()

		source = 'network'
		from_cache = reply.attribute(
			QtNetwork.QNetworkRequest.SourceIsFromCacheAttribute).toBool()
		if from_cache:
			source = 'disk cache'
		print '\n#tile_reply_event()'
		print '  tile %s received from %s' % (tile_id, source)

		self.map_changed()


	def standard_update(self):
		self.paint_reason.reason = Form.paint_reason.STANDARD_REDRAW
		self.update()

	def window_size(self):
		r = self.geometry()
		return (r.width(), r.height())

	def visible_tiles(self):
		w,h = self.window_size()
		x0,y0 = self.view_offset
		N = M = 2**self.zoom
		w_t = h_t = 256
		rc_view = ((0, h), (w, 0)) 
		rc_map = ((x0, N*h_t+y0), (M*w_t+x0, y0)) 

		if is_intersection_empty(rc_map, rc_view):
			return ((N-1, N-1), (M-1, M-1))
		else:
			if x0 < 0:
				n = ( abs(x0)/w_t, min(int(math.ceil((abs(x0)+w)/float(w_t))), 
					N-1)+1 )
			else:
				n = ( 0, min(int(math.ceil((w-x0)/float(w_t))), N-1)+1 )
			if y0 < 0:
				m = ( abs(y0)/h_t, min(int(math.ceil((abs(y0)+h)/float(h_t))), 
					M-1)+1 )
			else:
				m = ( 0, min(int(math.ceil((h-y0)/float(h_t))), M-1)+1 )
		return (m, n)

	def tiles_not_in_cache(self, visible_tile_range):
		tiles = []
		visible_tile_list = self.tile_list_from_range(visible_tile_range)
		for t in visible_tile_list:
			if self.find_in_image_cache(t[1], t[0], self.zoom) == None:
				if self.find_in_disk_cache(t[1], t[0], self.zoom) == None:
					tiles.append(t)
		return tiles

	def tile_list_from_range(self, tile_range):
		tiles = []
		m,n = tile_range
		for y in range(m[0], m[1]):
			for x in range(n[0], n[1]):
				tiles.append((y, x))
		return tiles

	def find_in_image_cache(self, x, y, z):
		if z != self.zoom:
			return None
		row = self.image_cache.get(y)
		if row:
			return row.get(x)
		else:
			return None

	def find_in_disk_cache(self, x, y, z):
		url = QtCore.QUrl(self.construct_tile_url(x, y, z))
		return self.disk_cache.data(url)

	def construct_tile_url(self, x, y, z):		
		return 'http://tile.openstreetmap.org/%d/%d/%d.png' % (z, x, y)

	def clear_image_cache(self):
		self.image_cache = {}

	def zoom_event(self, step):
		new_zoom = max(min(self.zoom+step, 17), 0)
		if new_zoom == self.zoom:
			return
		center = self.view_center_on_map()
		if step > 0:
			center = (self.double_distance(center[0]), 
				self.double_distance(center[1]))
		else:
			center = (center[0]/2, center[1]/2)
		w,h = self.window_size()
		self.view_offset = (-center[0]+w/2, -center[1]+h/2)
		self.zoom = new_zoom
		print '\n#zoom_event(): zoom event, zoom:%d' % (self.zoom, )
		
		self.clear_image_cache()
		self.set_window_title()
		self.map_changed()

	def keyPressEvent(self, e):
		if e.key() == QtCore.Qt.Key_O:
			fname = open_file_dialog(self)
			if is_vof_file(str(fname)):
				layer = vof_layer()
				layer.read_dump(fname)
				self.layers.append(layer)
			else:
				layer = path_layer()
				layer.read_dump(fname)
				self.layers.append(layer)
		self.standard_update()


	def double_distance(self, x):
		if x < 0:
			return -(2*x)
		else:
			return 2*x

	def view_center_on_map(self):
		w,h = self.window_size()
		return (abs(self.view_offset[0]) + w/2, abs(self.view_offset[1]) + h/2)

	def set_window_title(self):
		self.setWindowTitle('PySlippyMap client (zoom:%d)' % (
			self.zoom, ))

	def pan_event(self, diff):
		self.view_offset = (self.view_offset[0] + diff[0], 
			self.view_offset[1] + diff[1])
		self.map_changed()

	def wheelEvent(self, e):
		step = 1
		if e.delta() < 0:
			step = -1
		self.zoom_event(step)

	def mousePressEvent(self, e):
		self.click_pos = (e.x(), e.y())

	def mouseMoveEvent(self, e):
		diff = (e.x() - self.click_pos[0], e.y() - self.click_pos[1])
		self.click_pos = (e.x(), e.y())
		self.pan_event(diff)

	def resizeEvent(self, e):
		print '#resizeEvent()'
		self.map_changed()



def is_vof_file(fname):
	return os.path.splitext(fname)[1] == '.vof'

def is_intersection_empty(r1, r2):
	a1,b1 = r1;	a2,b2 = r2
	return not ( (b2[0] > a1[0]) and (a2[0] < b1[0]) and (a2[1] > b1[1]) and 
		(b2[1] < a1[1]) )

def temp_directory():
	if os.name == 'nt':
		return os.environ['TEMP']
	else:
		return '/tmp'

def open_file_dialog(parent):
	return QtGui.QFileDialog.getOpenFileName(parent, 'Open dump file ...')
		

class layer:
	def __init__(self):
		pass

	def read_dump(self, fname):
		pass

	def paint(self, view_offset, zoom, painter):
		pass


class path_layer(layer):
	def __init__(self):
		layer.__init__(self)
		self.paths = []

	def read_dump(self, fname):
		reader = path_dump.reader()
		self.paths = reader.read(fname)		

	def paint(self, view_offset, zoom, qp):
		WHITE = (255, 255, 255)
		if len(self.paths) == 0:
			return
		i = 1
		path = self.paths[0]
		u = path[0]
		while i < len(path):
			v = path[i]
			self.draw_edge(view_offset, zoom, self.ap2gp(u), self.ap2gp(v), 
				WHITE, qp)
			self.draw_vertex(view_offset, zoom, self.ap2gp(u), WHITE, qp)
			self.draw_vertex(view_offset, zoom, self.ap2gp(v), WHITE, qp)
			u = v
			i += 1

	def draw_vertex(self, view_offset, zoom, latlon, color, qp):
		x0,y0 = view_offset
		x,y = self.latlon2xy(latlon, zoom)
		x,y = (x-12/2, y-12/2)
		old_brush = qp.brush()
		qp.setBrush(QtGui.QBrush(QtGui.QColor(color[0], color[1], color[2])))
		qp.drawEllipse(x+x0, y+y0, 12, 12)
		qp.setBrush(old_brush)

	def draw_edge(self, view_offset, zoom, f_latlon, t_latlon, color, qp):
		x0,y0 = view_offset
		x_f, y_f = self.latlon2xy(f_latlon, zoom)
		x_t, y_t = self.latlon2xy(t_latlon, zoom)
		qp.drawLine(x_f+x0, y_f+y0, x_t+x0, y_t+y0)

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


class vof_layer(layer):
	def __init__(self):
		layer.__init__(self)

	# public
	def read_dump(self, fname):
		reader = vof_dump.reader(fname)
		self.process_dump(reader.graph(), reader.path(), reader.fromto())

	# public
	def paint(self, view_offset, zoom, painter):
		self.draw_edges(self.white, view_offset, zoom, (0, 0, 0), painter)
		self.draw_edges(self.grey, view_offset, zoom, (0, 0, 0), painter)
		self.draw_white_verts(self.white_verts, view_offset, zoom, painter)
		self.draw_verts(self.grey_verts, view_offset, zoom, (128, 128, 128), 
			painter)
		
	def draw_edges(self, edges, view_offset, zoom, color, painter):
		brush = painter.brush()
		painter.setBrush(QtGui.QBrush(
			QtGui.QColor(color[0], color[1], color[2])))
		for e in edges:
			self.draw_edge(view_offset, zoom, e.source, e.target, painter)
		painter.setBrush(brush)
	
	def draw_edge(self, view_offset, zoom, f_latlon, t_latlon, painter):
		x0,y0 = view_offset
		x_f, y_f = self.latlon2xy(f_latlon, zoom)
		x_t, y_t = self.latlon2xy(t_latlon, zoom)		
		painter.drawLine(x_f+x0, y_f+y0, x_t+x0, y_t+y0)
	
	def draw_white_verts(self, verts, view_offset, zoom, painter):
		brush = painter.brush()
		for v in verts:
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

	def draw_grey_verts(self, verts, view_offset, zoom, painter):
		self.draw_verts(verts, view_offset, zoom, (128, 128, 128), painter)
	
	def draw_verts(self, verts, view_offset, zoom, color, painter):
		brush = painter.brush()
		painter.setBrush(QtGui.QBrush(
			QtGui.QColor(color[0], color[1], color[2])))
		for v in verts:
			self.draw_vertex(view_offset, zoom, v, painter)
		painter.setBrush(brush)
			
	def draw_vertex(self, view_offset, zoom, latlon, painter):
		x0,y0 = view_offset
		x,y = self.latlon2xy(latlon, zoom)
		x,y = (x-12/2, y-12/2)
		painter.drawEllipse(x+x0, y+y0, 12, 12)

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

	def has_valid_gps(self, record):
		return record.source.is_valid() and record.target.is_valid()

class Vertex:
	BLACK, GREY, WHITE, GREEN = range(0, 4)

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


if __name__ == '__main__':
	main(sys.argv)

