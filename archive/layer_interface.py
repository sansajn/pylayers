# -*- coding: utf-8 -*-
# Common layer interface.
# \author Adam Hlavatovič

import debug_helper

# \note create() > zoom_event() > [paint()]
class layer:
	def __init__(self):
		self.debug_prints = True
		self.name = 'none'
		self.category = 'none'

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
		'Posun vrstvy.'
		pass
	
	# \param event QMouseEvent
	def mouse_move_event(self, event):
		pass

	# \param event QMouseEvent
	def mouse_press_event(self, event):
		pass

	# \param event QMouseEvent
	def mouse_release_event(self, event):
		pass

	def debug(self, msg):
		if self.debug_prints:
			debug_helper.debug.layer_print(msg)
