# -*- coding: utf-8 -*-
import sys, math, time, os
from PyQt4 import QtCore, QtGui, QtNetwork

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

		self.network = QtNetwork.QNetworkAccessManager()
		self.connect(self.network, QtCore.SIGNAL(
			'finished(QNetworkReply *)'),	self.tile_reply_event)
		self.disk_cache = QtNetwork.QNetworkDiskCache()
		self.disk_cache.setCacheDirectory(os.path.join(temp_directory(), 'tiles'))
		self.network.setCache(self.disk_cache)
	
	def paintEvent(self, e):
		t = time.clock()
		qp = QtGui.QPainter()
		qp.begin(self)

		if self.paint_reason.reason == Form.paint_reason.TILE_CHANGED:
			self.draw_tile(self.paint_reason.data, qp)
		else:
			self.draw_map(qp)

		qp.end()
		dt = time.clock() - t
		print 'paint event: %f' % (dt, )

	def draw_map(self, qp):
		print '#draw_map()'
		y,x = self.visible_tiles()
		print y,x
		for i in range(y[0], y[1]):
			for j in range(x[0], x[1]):
				tile = self.load_tile_from_image_cache(j, i)
				if tile == None:
					tile = self.load_tile_from_disk_cache(j, i)
					if tile:
						self.insert_tile_to_image_cache(tile, j, i)
				if tile:
					self.draw_tile(tile, j, i, qp)
		print 'x0:%d, y0:%d' % self.view_offset
		print 'visible tiles:%s' % ((y,x), )

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
			print 'tile z:%d, x:%d, y:%d loaded from disk cache' % (
				self.zoom, x, y)
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
		print '  tiles not in cache: %s' % (tiles, )
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
		print '\n#tile_request()'
		print 'network request for tile z:%d, x:%d, y:%d' % (z, x, y)

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
			return []
		else:
			if x0 < 0:
				n = ( abs(x0)/w_t, min(int(math.ceil((abs(x0)+w)/float(w_t))), N-1)+1 )
			else:
				n = ( 0, min(int(math.ceil((w-x0)/float(w_t))), N-1)+1 )
			if y0 < 0:
				m = ( abs(y0)/h_t, min(int(math.ceil((abs(y0)+h)/float(h_t))), M-1)+1 )
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
		print '\n#tile_list_from_range(): len(tile_range)=%d' % (
			len(tile_range), )
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
		self.zoom = max(self.zoom+step, 0) % 16
		print '\n#zoom_event(): zoom event, zoom:%d' % (self.zoom, )
		self.clear_image_cache()
		self.map_changed()

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


def is_intersection_empty(r1, r2):
	a1,b1 = r1;	a2,b2 = r2
	return not ( (b2[0] > a1[0]) and (a2[0] < b1[0]) and (a2[1] > b1[1]) and 
		(b2[1] < a1[1]) )

def temp_directory():
	return os.environ['TEMP']



if __name__ == '__main__':
	main(sys.argv)

