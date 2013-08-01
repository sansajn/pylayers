# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui
import layers


class main_window(QtGui.QMainWindow):
	def __init__(self, args):
		QtGui.QMainWindow.__init__(self)
	
		self.map_widget = layers.layers(self, args)
		self.setCentralWidget(self.map_widget)
	
		self.resize(800, 600)

	#@{ Public interface
	def append_dock(self, dock, area=None):
		if not area:
			area = QtCore.Qt.LeftDockWidgetArea
		self.addDockWidget(area, dock)
	#@}

if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	main_win = main_window(sys.argv)
	main_win.show()
	sys.exit(app.exec_())

