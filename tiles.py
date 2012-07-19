# -*- coding: utf-8 -*-
# \author Adam Hlavatovič
import sys, math, time, os
from PyQt4 import QtCore, QtGui, QtNetwork
import path_layer, vof_layer, transport_layer, osm_layer, edge_layer

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
		self.layers = []

		self.resize(800, 600)

		self.add_layer(osm_layer.layer(self))

	def add_layer(self, layer):
		self.layers.append(layer)
		layer.zoom_event(self.zoom)
	
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
		print '\n#zoom_event(): zoom:%d' % (self.zoom, )
		
		self.set_window_title()

		for layer in self.layers:
			layer.zoom_event(self.zoom)

	def pan_event(self, diff):
		self.view_offset = (self.view_offset[0] + diff[0], 
			self.view_offset[1] + diff[1])
		for layer in self.layers:
			layer.pan_event()

	def view_center_on_map(self):
		w,h = self.window_size()
		return (abs(self.view_offset[0]) + w/2, abs(self.view_offset[1]) + h/2)

	def double_distance(self, x):
		if x < 0:
			return -(2*x)
		else:
			return 2*x

	def set_window_title(self):
		self.setWindowTitle('PyLayers (zoom:%d)' % (self.zoom, ))
	
	def window_size(self):
		r = self.geometry()
		return (r.width(), r.height())

	#@{ Qt events
	def paintEvent(self, e):
		print '\n#paintEvent()'
		t = time.clock()
		qp = QtGui.QPainter()
		qp.begin(self)

		w,h = self.window_size()
		qp.drawRect(0, 0, w, h)
		for layer in self.layers:
			layer.paint(qp)

		qp.end()
		dt = time.clock() - t
		print '--> total: %f s' % (dt, )

	def keyPressEvent(self, e):
		if e.key() == QtCore.Qt.Key_O:
			fname = open_file_dialog(self)
			if is_vof_file(str(fname)):
				layer = vof_layer.layer(self, self.zoom)
				layer.create(fname)
				self.add_layer(layer)
			elif is_path_file(str(fname)):
				layer = path_layer.layer(self)
				layer.create(fname)
				self.add_layer(layer)
			elif is_edges_file(str(fname)):
				layer = edge_layer.layer(self)
				layer.create(str(fname))
				self.add_layer(layer)				
			else:
				layer = transport_layer.layer(self)
				layer.create(fname)
				self.add_layer(layer)
		for layer in self.layers:
			layer.key_press_event(e)
		self.update()

	def wheelEvent(self, e):
		step = 1
		if e.delta() < 0:
			step = -1
		self.zoom_event(step)

	def mousePressEvent(self, e):
		self.click_pos = (e.x(), e.y())
		for layer in self.layers:
			layer.mouse_press_event(e)

	def mouseMoveEvent(self, e):
		diff = (e.x() - self.click_pos[0], e.y() - self.click_pos[1])
		self.click_pos = (e.x(), e.y())
		self.pan_event(diff)

	def resizeEvent(self, e):
		self.update()
	#@}  Qt events



def is_vof_file(fname):
	return os.path.splitext(fname)[1] == '.vof'

def is_path_file(fname):
	return os.path.splitext(fname)[1] == '.out'

def is_edges_file(fname):
	return os.path.splitext(fname)[1] == '.edges'

def open_file_dialog(parent):
	return QtGui.QFileDialog.getOpenFileName(parent, 'Open dump file ...')
		


if __name__ == '__main__':
	main(sys.argv)

