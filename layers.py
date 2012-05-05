# -*- coding: utf-8 -*-
# Common layer interface.
# \author Adam Hlavatovič

class layer_interface:
	def __init__(self, widget):
		self.widget = widget
		self.zoom = None

	def read_data(self, fname):
		r'Reads layer data, before zoom_event and paint is called.'
		pass

	def paint(self, view_offset, painter):
		pass

	def key_press_event(self, event):
		pass

	def zoom_event(self, zoom):
		self.zoom = zoom

