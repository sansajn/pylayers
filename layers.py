# -*- coding: utf-8 -*-
# Common layer interface.
# \author Adam Hlavatovič


# \note create() > zoom_event() > [paint()]
class layer_interface:
	def __init__(self, widget):
		self.widget = widget
		self.zoom = None

	def create(self, uri):
		pass

	def paint(self, view_offset, painter):
		pass

	def key_press_event(self, event):
		pass

	def zoom_event(self, zoom):
		self.zoom = zoom

	def mouse_press_event(self, event):
		pass

