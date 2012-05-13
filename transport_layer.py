# -*- coding: utf-8 -*-
# \author Adam Hlavatovič
from PyQt4 import QtCore, QtGui
import gps, layers


class layer(layers.layer_interface):
	def __init__(self, widget):
		layers.layer_interface.__init__(self, widget)
		self.stops = []
		self.drawable = []

	#@{ layer_interface implementation
	def create(self, transport_pack):
		fstops = open(transport_pack, 'r')
		field_map = read_header(fstops)
		stops_table = read_records(fstops)
		stops = extract_stops_pos(stops_table, field_map['stop_lat'],
			field_map['stop_lon'])
		self.stops = stops
		
	def paint(self, painter):
		view_offset = self.widget.view_offset
		old_pen = painter.pen()
		old_brush = painter.brush()
		painter.setPen(QtGui.QPen(QtCore.Qt.black))
		painter.setBrush(QtGui.QBrush(QtCore.Qt.white))
		for d in self.drawable:
			d.paint(view_offset, painter)
		painter.setPen(old_pen)
		painter.setBrush(old_brush)

	def zoom_event(self, zoom):
		layers.layer_interface.zoom_event(self, zoom)
		self.prepare_drawable_data()

	def mouse_press_event(self, event):
		pass
	#@}

	def prepare_drawable_data(self):
		self.drawable = [drawable_stop(gps.mercator.gps2xy(
			gps.gpspos(stop[0], stop[1]), self.zoom))	for stop in self.stops]


def read_header(fstops):
	field_map = dict()
	ln = fstops.readline()
	fields = ln.split(',')
	for k,v in enumerate(fields):
		field_map[v] = k
	return field_map

def read_records(fstops):
	return [ln.split(',') for ln in fstops]
		
def extract_stops_pos(table, lat_idx, lon_idx):
	return [(float(rec[lat_idx]), float(rec[lon_idx])) for rec in table]


class drawable_stop:
	def __init__(self, pos):
		self.r = 8
		self.pos = QtCore.QPoint(pos[0], pos[1])

	def paint(self, view_offset, painter):
		x0,y0 = view_offset
		painter.drawEllipse(self.pos.x()+x0, self.pos.y()+y0, self.r, self.r)

