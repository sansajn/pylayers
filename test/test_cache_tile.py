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
		self.view_offset = (0, 0)
		self.click_pos = (0, 0)
		self.zoom = 2
		self.resize(800, 600)

		self.network = QtNetwork.QNetworkAccessManager()
		self.connect(self.network, QtCore.SIGNAL(
			'finished(QNetworkReply *)'),	self.tile_reply_event)
		self.disk_cache = QtNetwork.QNetworkDiskCache()
		self.disk_cache.setCacheDirectory(os.path.join(temp_directory(),
			'test_tiles'))
		self.network.setCache(self.disk_cache)

		self.tile_request(4, 0, 2)
		self.tile_request(1, 0, 2)
		self.tile_request(4, 1, 2)

		self.tile_request(4, 0, 2)
		self.tile_request(4, 1, 2)


	def tile_request(self, x, y, z):
		url = QtCore.QUrl(self.construct_tile_url(x, y, z))
		request = QtNetwork.QNetworkRequest()		
		request.setUrl(url)
		request.setRawHeader('User-Agent', 'PySlippyMap client')
		request.setAttribute(QtNetwork.QNetworkRequest.CacheLoadControlAttribute,
			QtNetwork.QNetworkRequest.PreferCache)
		request.setAttribute(
			QtNetwork.QNetworkRequest.HttpPipeliningAllowedAttribute, True)
		request.setAttribute(QtNetwork.QNetworkRequest.User, (x, y, z))
		self.network.get(request)
		print '\n#tile_request()'
		print '  network request for tile z:%d, x:%d, y:%d' % (z, x, y)

	def tile_reply_event(self, reply):
		if reply.error():
			print 'error occured code:%d' % (reply.error(), )
		tile_id = reply.request().attribute(
			QtNetwork.QNetworkRequest.User).toPyObject()		
		from_cache = reply.attribute(
			QtNetwork.QNetworkRequest.SourceIsFromCacheAttribute).toBool()
		source = 'network'
		if from_cache:
			source = 'disk cache'
		print '\n#tile_reply_event()'
		print '  tile %s received from %s' % (tile_id, source)

	def construct_tile_url(self, x, y, z):		
		return 'http://tile.openstreetmap.org/%d/%d/%d.png' % (z, x, y)


def temp_directory():
	return os.environ['TEMP']


if __name__ == '__main__':
	main(sys.argv)

