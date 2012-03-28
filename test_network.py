# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtNetwork

def main(args):
	app = test_network(args)
	app.main()
	app.exec_()

class test_network(QtCore.QCoreApplication):
	def __init__(self, args):
		QtCore.QCoreApplication.__init__(self, args)

	def main(self):
		self.network = QtNetwork.QNetworkAccessManager()
		self.connect(self.network, 
			QtCore.SIGNAL('finished(QNetworkReply *)'), self.finished_reply)
		request = QtNetwork.QNetworkRequest(QtCore.QUrl(
			'http://www.google.com'))
		self.network.get(request)

	def finished_reply(self, reply):
		print reply.read(reply.size())
		self.exit()

if __name__ == '__main__':
	main(sys.argv)

	
