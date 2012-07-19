# -*- coding: utf-8 -*-
# Common layer interface.
# \author Adam Hlavatovič


# \note create() > zoom_event() > [paint()]
class layer_interface:
	def __init__(self, widget):
		self.zoom = None
		self.widget = widget		

	def create(self, uri):
		pass

	#! \param painter objekt typu QtGui.QPainter().
	def paint(self, painter):
		pass

	def key_press_event(self, event):
		pass

	def zoom_event(self, zoom):
		self.zoom = zoom

	def pan_event(self):
		pass

	# \param event QMouseEvent
	def mouse_press_event(self, event):
		pass
