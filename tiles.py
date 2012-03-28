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
		self.disk_cache.setCacheDirectory(os.path.join(temp_directory(), 
			'tiles'))
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
		x,y = self.visible_tiles()
		for i in range(y[0], y[1]+1):
			for j in range(x[0], x[1]+1):
				tile = self.load_tile_from_image_cache(j, i)
				if tile == None:
					tile = self.load_tile_from_disk_cache(j, i)
					if tile:
						self.insert_tile_to_image_cache(tile, j, i)
				if tile:
					self.draw_tile(tile, j, i. qp)

	def draw_tile(tile, x, y, qp):
		x0,y0 = self.view_offset()
		qp.drawImage(QtCore.QPoint(x*256+x0, y*256+y0), tile)

	def load_tile_from_image_cache(self, x, y):
		return self.image_cache.get(y).get(x)

	def load_tile_from_disk_cache(self, x, y):
		url = QtCore.QUrl('http://tile.openstreetmap.org/%d/%d/%d.png' % (
			self.zoom, x, y))
		cache_item = self.disk_cache(url)
		if cache_item:
			return QtCore.QImage(cache_item, 'PNG')
		else:
			return None

	def insert_tile_to_image_cache(self, tile, x, y):
		if y in self.image_cache:
			self.image_cache[y][x] = tile
		else:
			self.image_cache[y] = {x:tile}

	def map_changed(self):
		tiles = self.tiles_not_in_cache(self.visible_tiles())
		for t in tiles:
			self.tile_request(t[0], t[1], self.zoom)		
		self.standard_update()

	def tile_request(self, x, y, z):
		if (x,y,z) in self.requested_set:
			return
		url = QtCore.QUrl(self.construct_tile_url(x, y, z))
		request = QtNetwork.QNetworkRequest()		
		request.setUrl(url)
		request.setRawHeader('User-Agent', 'PySlippyMap client')
		request.setAttribute(QtNetwork.QNetworkRequest.CacheLoadControlAttribute,
			QtNetwork.QNetworkRequest.PreferCache)
		request.setAttribute(QNetworkRequest.HttpPipeliningAllowedAttribute,	True)
		request.setAttribute((x, y, z))
		self.requested_tiles.add((x, y, z))
		self.network.get(request)

	def tile_reply_event(self, reply):
		self.disk_cache.insert(reply)
		id = reply.attribute(QtNetwor.QNetworkRequest.User).toPyObject()
		self.requested_tiles.remove(id)
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
		rc_map = ((x0, N*h_t+y0), (M*w_t+x0)) 

		if is_intersection_empty(rc_map, rc_view):
			return []
		else:
			if x0 < 0:
				n = ( abs(x0)/w_t, math.min((abs(x0)+w)/w_t, N) )
			else:
				n = ( 0, math.min((w-x0)/w_t), N )
			if y0 < 0:
				m = ( abs(y0)/h_t, min((abs(y0)+h)/h_t, M) )
			else:
				m = ( 0, math.min((h-y0)/h_t, M) )
		return (m, n)

	def tiles_not_in_cache(self, visible_tiles):
		tiles = []
		for t in visible_tiles:
			if self.find_in_image_cache(t[0], t[1], self.zoom) == None:
				if self.find_in_disk_cache(t[0], t[1], self.zoom) == None:
					tiles.append(t)							
		return tiles

	def find_in_image_cache(self, x, y, z):
		if z != self.zoom:
			return None
		row = self.get(y)
		if row != None:
			return row.get(x)
		else:
			return None

	def find_in_disk_cache(self, x, y, z):
		url = QtCore.QUrl(self.construct_tile_url(x, y, z))
		return self.disk_cache(url)

	def construct_tile_url(self, x, y, z):		
		return 'http://tile.openstreetmap.org/%d/%d/%d.png' % (z, x, y)

	def zoom_event(self, step):
		self.zoom = max(self.zoom+step, 0) % 16
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
		pan_event(diff)


def is_intersection_empty(r1, r2):
	a1,b1 = r1;	a2,b2 = r2
	return not ( (b2[0] > a1[0]) and (a2[0] < b1[0]) and (a2[1] > b1[1]) and 
		(b2[1] < a1[1]) )

def temp_directory():
	return os.environ['TEMP']



if __name__ == '__main__':
	main(sys.argv)

