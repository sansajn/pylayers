# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui
import layers


class main_window(QtGui.QMainWindow):
	def __init__(self, args):
		QtGui.QMainWindow.__init__(self)		
		self.args = args
		self.layers = None
		self.docks = []
		self.docks_state = True
		self.resize(800, 600)

		#self.layers = layers.layers(self, self.args)
		#self.setCentralWidget(self.layers)

	def resizeEvent(self, event):
		QtGui.QMainWindow.resizeEvent(self, event)
		r = self.geometry()
		print('resizeEvent():%d,%d' % (r.width(), r.height()))

	def showEvent(self, event):
		QtGui.QMainWindow.showEvent(self, event)
		r = self.geometry()
		print('showEvent():%d,%d' % (r.width(), r.height()))
		if self.layers is None:
			self.layers = layers.layers(self, self.args)
			self.setCentralWidget(self.layers)

	#@{ Public interface
	def append_dock(self, dock, area=None):
		if not area:
			area = QtCore.Qt.LeftDockWidgetArea
		self.addDockWidget(area, dock)		
		self.docks.append((dock, area))
		
	def hide_docks(self):
		for dock in self.docks:
			self.removeDockWidget(dock[0])
			
	def show_docks(self):
		for dock in self.docks:
			self.addDockWidget(dock[1], dock[0])
			
	def toggle_docks(self):
		if self.docks_state:
			self.docks_state = False
			self.hide_docks()
		else:
			self.docks_state = True
			self.show_docks()
	#@}

if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	main_win = main_window(sys.argv)
	main_win.show()
	sys.exit(app.exec_())

