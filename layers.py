# -*- coding: utf-8 -*-
# Implementuje spoločné záležitosti pre vrstvy.
# \author Adam Hlavatovič
# \version 20120403

class layer_interface:
	def __init__(self, widget):
		self.widget = widget

	def read_dump(self, fname):
		pass

	def paint(self, view_offset, zoom, painter):
		pass

	def key_press_event(self, e):
		pass

