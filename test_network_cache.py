# -*- coding: utf-8 -*-
import sys, random
from PyQt4 import QtCore, QtNetwork

def main(args):
	app = test_network(args)
	app.main()
	app.exec_()

class test_network(QtCore.QCoreApplication):
	def __init__(self, args):
		QtCore.QCoreApplication.__init__(self, args)
		self.targets = ['http://www.google.com', 'http://www.bing.com',
			'http://www.yahoo.com']
		self.request_count = 0

	def main(self):
		self.network = QtNetwork.QNetworkAccessManager()
		self.connect(self.network, QtCore.SIGNAL('finished(QNetworkReply *)'), 
			self.finished_reply)
		self.cache = QtNetwork.QNetworkDiskCache()
		self.cache.setCacheDirectory('/tmp/cache_temp')
		self.network.setCache(self.cache)

		self.timer = QtCore.QTimer()
		self.connect(self.timer, QtCore.SIGNAL('timeout()'),
			self.on_request_timer)
		self.timer.start(300)

	def on_request_timer(self):
		self.send_request(QtCore.QUrl(self.targets[random.randint(0,
			len(self.targets)-1)]))

	def send_request(self, url):
		if self.request_count > 50:
			self.exit()
		cache_item = self.cache.data(url)
		if cache_item:
			self.request_count += 1
			print "%dB from '%s'" %	(
				len(cache_item.read(cache_item.size())), url)
		else:
			request = QtNetwork.QNetworkRequest(url)
			self.network.get(request)

	def finished_reply(self, reply):
		self.cache.insert(reply)
		self.emit('cache_updated', reply.url())

	def cache_updated(self, url):
		self.send_request(url)

if __name__ == '__main__':
	main(sys.argv)

	
