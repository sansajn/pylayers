# -*- coding: utf-8 -*-
# Common layer interface.
# \author Adam Hlavatovič


# \note create() > zoom_event() > [paint()]
class layer_interface:
	def __init__(self, parent):
		self.debug_prints = True

	def create(self, uri):
		pass

	#! \param painter objekt typu QtGui.QPainter().
	def paint(self, painter, view_offset):
		pass

	def key_press_event(self, event):
		pass

	def zoom_event(self, zoom):
		pass		

	def pan_event(self):
		pass

	# \param event QMouseEvent
	def mouse_press_event(self, event):
		pass
	
	def debug(self, msg):
		if self.debug_prints:
			print msg
