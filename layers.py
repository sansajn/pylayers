# -*- coding: utf-8 -*-
# Implementuje spoločné rozhranie pre vrstvy.
# \author Adam Hlavatovič

class layer_interface:
	def __init__(self, widget):
		self.widget = widget
		self.zoom = None

	def read_dump(self, fname):
		pass

	def paint(self, view_offset, zoom, painter):
		pass

	def key_press_event(self, e):
		pass

	def zoom_event(self, zoom):
		self.zoom = zoom

