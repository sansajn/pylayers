# -*- coding: utf-8 -*-
import sys, math, time, os
from PyQt4 import QtCore, QtGui, QtNetwork

def main(args):
	app = QtGui.QApplication(args)
	form = Form()
	form.show()
	app.exec_()


class Form(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self, None)
		self._view_offset = (0, 0)
		self._click_pos = (0, 0)
		self._zoom = 2
		self.resize(800, 600)
		self._tiles = {self._zoom: self._read_tiles(self._zoom)}

		#self._network = QtNetwork.QNetworkAccessManager()
		#self.connect(self._network, QtCore.SIGNAL(
		#	'finished(QNetworkReply *)'),	self._finished_reply)
		#self._disk_cache = QtNetwork.QNetworkDiskCache()
		#self._disk_cache.setCacheDirectory(os.path.join(temp_directory, 
		#	'tiles'))
		#self._network.setCache(self._disk_cache)

	def paintEvent(self, e):
		t = time.clock()
		qp = QtGui.QPainter()
		qp.begin(self)
		self._draw_map(qp)
		qp.end()
		dt = time.clock() - t
		print 'paint event: %f' % (dt, )

	def _draw_map(self, qp):
		z = self._zoom
		m = n = 2**z
		w,h = self._window_size()
		x0,y0 = self._view_offset
		x0tile, y0tile = (0, 0)
		if x0 < 0:
			x0tile = min(abs(x0)/256, n-1)
		ymtile = m
		if y0 > 0:
			ymtile = min((max(h-y0, 0)+255)/256, m)
		xntile = min(x0tile + (w+255)/256 + 1, n)

		for x in range(x0tile, xntile):
			for y in range(y0tile, ymtile):
				qp.drawImage(QtCore.QPoint(x*256+x0, y*256+y0), 
					self._tiles[z][x][y])

		print 'x0=%d, y0=%d' % (x0, y0)	
		print 'x0tile=%d > xntile=%d, y0tile=%d > ymtile=%d' % (x0tile,
			xntile, y0tile, ymtile)
		print self.visible_tiles()
	

	def wheelEvent(self, e):
		prev_zoom = self._zoom
		if e.delta() > 0:
			self._zoom = min(self._zoom+1, 2)
		else:
			self._zoom = max(self._zoom-1, 0)
		self.on_zoom_change(prev_zoom)

	def on_zoom_change(self, prev_zoom):
		if self._zoom not in self._tiles:
			self._tiles[self._zoom] = self._read_tiles(self._zoom)
		k = 2**(self._zoom - prev_zoom)
		self._view_offset = (int(self._view_offset[0]*k),
			int(self._view_offset[1]*k))
		self.update()
	
	def mousePressEvent(self, e):
		self._click_pos = (e.x(), e.y())

	def mouseMoveEvent(self, e):
		diff = (e.x() - self._click_pos[0], e.y() - self._click_pos[1])
		self._view_offset = (self._view_offset[0] + diff[0], 
			self._view_offset[1] + diff[1])
		self._click_pos = (e.x(), e.y())
		self.update()

	def _read_tiles(self, zoom):
		tiles = []
		for x in range(0, 2**zoom):
			tile_coll = []
			for y in range(0, 2**zoom):
				tile = QtGui.QImage('tiles/%d_%d_%d.png' % (zoom, x, y))
				tile_coll.append(tile)
			tiles.append(tile_coll)
		return tiles

	def finished_reply(self, reply):
		self._disk_cache.insert(reply)
		self.emit('disk_cache_updated', reply.url())

	def disk_cache_updated(self, url):
		self.load_tile(url)

	def _window_size(self):
		r = self.geometry()
		return (r.width(), r.height())

	def visible_tiles(self):
		r'''Vráti horizontálny a vertikálny rozsah vymedzujúci vyditeľné
			dlaždice.'''
		w,h = self._window_size()
		x0,y0 = self._view_offset
		n = ( int(math.ceil(abs(x0)/256.0)), int(math.ceil(
			(abs(x0)+w)/256.0)) )
		m = ( int(math.ceil(abs(y0)/265.0)), int(math.ceil(
			(abs(y0)+h)/256.0)) )
		return (m, n)

def temp_directory():
	return os.environ['TEMP']



if __name__ == '__main__':
	main(sys.argv)
