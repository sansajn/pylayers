# -*- coding: utf-8 -*-
# \author Adam Hlavatovič
import sys, math, time, os
from PyQt4 import QtCore, QtGui, QtNetwork
import path_layer, vof_layer, transport_layer, osm_layer, edge_layer, \
	osmgraph_layer


def main(args):
	app = QtGui.QApplication(args)
	form = Form(args)
	form.show()
	app.exec_()


class Form(QtGui.QMainWindow):
	def __init__(self, args):
		QtGui.QMainWindow.__init__(self, None)
		self.MAX_ZOOM = 17  # max osm zoom
		self.view_offset = (0, 0)
		self.click_pos = (0, 0)
		self.zoom = 2
		self.mouse_move = False
		self.layers = []

		self.resize(800, 600)

		self.add_layer(osm_layer.layer(self))

		if len(args) > 1:
			self._open_file(args[1])

	#{@ Public interface
	def add_layer(self, layer):
		self.layers.append(layer)
		layer.zoom_event(self.zoom)

	def get_layer(self, category, name=None):
		for layer in self.layers:
			if layer.category == category:
				if name != None:
					if layer.name == name:
						return layer
				else:
					return layer
		return None

	def center_to(self, xypos):
		w,h = self.window_size()
		self.view_offset = (-xypos[0]+w/2, -xypos[1]+h/2)

	def set_zoom(self, zoom):
		if zoom == self.zoom:
			return
		diff = zoom - self.zoom
		center = self.view_center_on_map()
		if diff > 0:
			center = (self.scale_distance(center[0], 2*diff),
				self.scale_distance(center[1], 2*diff))
		else:
			scale = max(2, 2*diff)
			center = (center[0]/scale, center[1]/scale)

		self.zoom = zoom
		self.center_to(center)

		for layer in self.layers:
			layer.zoom_event(self.zoom)

	def to_world_coordinates(self, xypos):
		return (xypos[0]-self.view_offset[0], xypos[1]-self.view_offset[1])
	#}@ Public interface

	def zoom_event(self, step):
		new_zoom = max(min(self.zoom+step, self.MAX_ZOOM), 0)
		print '\n#zoom_event(): zoom:%d' % (new_zoom, )
		self.set_zoom(new_zoom)
		self.set_window_title()

	def pan_event(self, diff):
		self.view_offset = (self.view_offset[0] + diff[0], 
			self.view_offset[1] + diff[1])
		for layer in self.layers:
			layer.pan_event()

	def view_center_on_map(self):
		w,h = self.window_size()
		return (abs(self.view_offset[0]) + w/2, abs(self.view_offset[1]) + h/2)

	def scale_distance(self, dist, n):
		if dist < 0:
			return -abs(n*dist);
		else:
			return n*dist

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
			layer.paint(qp, self.view_offset)

		qp.end()
		dt = time.clock() - t
		print '--> total: %f s' % (dt, )

	def keyPressEvent(self, e):
		if e.key() == QtCore.Qt.Key_O:
			fname = open_file_dialog(self)
			self._open_file(fname)

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

	def mouseReleaseEvent(self, e):
		if not self.mouse_move:
			for layer in self.layers:
				layer.mouse_release_event(e)
		else:
			self.mouse_move = False

	def mouseMoveEvent(self, e):
		self.mouse_move = True
		diff = (e.x() - self.click_pos[0], e.y() - self.click_pos[1])
		self.click_pos = (e.x(), e.y())
		self.pan_event(diff)

	def resizeEvent(self, e):
		self.update()
	#@}  Qt events

	def _open_file(self, fname):
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
		elif is_osmgraph_file(str(fname)):
			layer = osmgraph_layer.layer(self)
			layer.create(str(fname))
			self.add_layer(layer)
		else:
			layer = transport_layer.layer(self)
			layer.create(fname)
			self.add_layer(layer)

		self.update()




def is_vof_file(fname):
	return os.path.splitext(fname)[1] == '.vof'

def is_path_file(fname):
	return os.path.splitext(fname)[1] == '.out'

def is_edges_file(fname):
	return os.path.splitext(fname)[1] == '.edges'

def is_osmgraph_file(fname):
	return os.path.splitext(fname)[1] == '.grp'

def open_file_dialog(parent):
	return QtGui.QFileDialog.getOpenFileName(parent, 'Open dump file ...')
		


if __name__ == '__main__':
	main(sys.argv)

