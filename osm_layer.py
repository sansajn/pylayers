# -*- coding: utf-8 -*-
# Open Street Map layer
# \author Adam Hlavatovič
import os, time, math
from PyQt4 import QtCore, QtGui, QtNetwork
import layers, gps

class layer(layers.layer_interface):
	def __init__(self, parent):
		layers.layer_interface.__init__(self, parent)
		self.parent = parent
		self.name = 'open-street-map'
		self.category = 'map'
		self.zoom = None
		self.hide = False
		self.requested_tiles = set()
		self.tile_ram_cache = {}
		
		self.tile_disk_cache = QtNetwork.QNetworkDiskCache()
		self.tile_disk_cache.setCacheDirectory(
			os.path.join(temp_directory(), 'tiles'))
		self.tile_disk_cache.setMaximumCacheSize(500*2**20)

		self.network = QtNetwork.QNetworkAccessManager()
		self.network.setCache(self.tile_disk_cache)
		
		parent.connect(self.network, QtCore.SIGNAL('finished(QNetworkReply *)'),
			self.tile_reply_event)

	#@{ layer_interface implementation
	def paint(self, painter, view_offset):
		if self.hide:
			return
		t = time.clock()
		self.draw_map(painter)
		dt = time.clock() - t
		self.debug('  #osm_layer.paint(): %f s' % (dt, ))

	def zoom_event(self, zoom):
		self.zoom = zoom
		t = time.clock()
		self.clear_tile_ram_cache()
		self.change_map()
		dt = time.clock() - t
		self.debug('  #osm_layer.zoom_event(): %f s' % (dt, ))

	def pan_event(self):
		self.change_map()

	# \param event QMouseEvent
	def mouse_press_event(self, event):
		pass

	def resize_event(self, event):
		self.change_map()
		
	def key_press_event(self, event):
		if event.key() == QtCore.Qt.Key_M:
			self.hide = not self.hide
	#@}

	def zoom_to(self, georect):
		w,h = self.parent.window_size()
		zoom = 0
		for zoom in range(0, self.parent.MAX_ZOOM):
			sw = gps.mercator.gps2xy(georect.sw, zoom)
			ne = gps.mercator.gps2xy(georect.ne, zoom)
			if abs(ne[0] - sw[0]) > w or abs(ne[1] - sw[1]) > h:
				break
		zoom = max(0, zoom-1)
		self.parent.set_zoom(zoom)
		self.parent.center_to(gps.mercator.gps2xy(georect.center(), zoom))
		

	def change_map(self):
		self.debug('\n#osm_layer.change_map()')
		tiles = self.tiles_not_in_cache(self.visible_tiles())
		for t in tiles:
			self.tile_request(t[1], t[0], self.zoom)
		self.standard_update()

	def standard_update(self):
		self.parent.update()

	def draw_map(self, painter):
		r'Nakreslí mapu s dlaždíc v pamäti, alebo na disku.'
		y,x = self.visible_tiles()
		for i in range(y[0], y[1]):
			for j in range(x[0], x[1]):
				tile = self.load_tile_from_image_cache(j, i)
				if tile == None:
					tile = self.load_tile_from_disk_cache(j, i)
					if tile:
						self.insert_tile_to_ram_cache(tile, j, i)
				if tile:
					self.draw_tile(tile, j, i, painter)

	def draw_tile(self, tile, x, y, painter):
		x0,y0 = self.parent.view_offset
		painter.drawImage(QtCore.QPoint(x*256+x0, y*256+y0), tile)

	def load_tile_from_image_cache(self, x, y):
		return self.find_in_ram_cache(x, y, self.zoom)

	def load_tile_from_disk_cache(self, x, y):
		url = QtCore.QUrl(self.construct_tile_url(x, y, self.zoom))
		cache_item = self.tile_disk_cache.data(url)
		if cache_item:
			tile = QtGui.QImage()
			tile.load(cache_item, 'PNG')#m
			return tile
		else:
			return None

	def insert_tile_to_ram_cache(self, tile, x, y):
		if y in self.tile_ram_cache:
			self.tile_ram_cache[y][x] = tile
		else:
			self.tile_ram_cache[y] = {x:tile}

	def tiles_not_in_cache(self, visible_tile_range):
		tiles = []
		visible_tile_list = self.tile_list_from_range(visible_tile_range)
		for t in visible_tile_list:
			if self.find_in_ram_cache(t[1], t[0], self.zoom) == None:
				if self.find_in_disk_cache(t[1], t[0], self.zoom) == None:
					tiles.append(t)
		return tiles

	def find_in_ram_cache(self, x, y, z):
		if z != self.zoom:
			return None
		row = self.tile_ram_cache.get(y)
		if row:
			return row.get(x)
		else:
			return None

	def find_in_disk_cache(self, x, y, z):
		url = QtCore.QUrl(self.construct_tile_url(x, y, z))
		return self.tile_disk_cache.data(url)

	def visible_tiles(self):
		w,h = self.parent.window_size()
		x0,y0 = self.parent.view_offset
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

	def tile_list_from_range(self, tile_range):
		tiles = []
		m,n = tile_range
		for y in range(m[0], m[1]):
			for x in range(n[0], n[1]):
				tiles.append((y, x))
		return tiles

	def tile_request(self, x, y, z):
		if (x, y, z) in self.requested_tiles:
			return
		url = QtCore.QUrl(self.construct_tile_url(x, y, z))
		request = QtNetwork.QNetworkRequest()		
		request.setUrl(url)
		request.setRawHeader('User-Agent', 'PyLayers OSM layer')
		request.setAttribute(QtNetwork.QNetworkRequest.CacheLoadControlAttribute,
			QtNetwork.QNetworkRequest.PreferCache)
		request.setAttribute(
			QtNetwork.QNetworkRequest.HttpPipeliningAllowedAttribute, True)
		request.setAttribute(QtNetwork.QNetworkRequest.User, (x, y, z))
		self.requested_tiles.add((x, y, z))
		self.network.get(request)

	def tile_reply_event(self, reply):
		if reply.error():
			print '#osm_layer.tile_reply_event(): error=%d' % (reply.error(),)
			return

		tile_id = reply.request().attribute(
			QtNetwork.QNetworkRequest.User).toPyObject()

		source = 'network'
		from_cache = reply.attribute(
			QtNetwork.QNetworkRequest.SourceIsFromCacheAttribute).toBool()
		if from_cache:
			source = 'disk cache'
		self.debug('#osm_layer.tile_reply_event()')
		self.debug('  tile %s received from %s' % (tile_id, source))

		self.change_map()


	def construct_tile_url(self, x, y, z):		
		return 'http://tile.openstreetmap.org/%d/%d/%d.png' % (z, x, y)

	def clear_tile_ram_cache(self):
		self.tile_ram_cache = {}


def is_intersection_empty(r1, r2):
	a1,b1 = r1;	a2,b2 = r2
	return not ( (b2[0] > a1[0]) and (a2[0] < b1[0]) and (a2[1] > b1[1]) and 
		(b2[1] < a1[1]) )

def temp_directory():
	if os.name == 'nt':
		return os.environ['TEMP']
	else:
		return '/tmp'

