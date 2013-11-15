# -*- coding: utf-8 -*-
# \autor Adam Hlavatovic

class debug:
	debug_prints = True
	
	@staticmethod
	def layer_print(msg):
		if debug.debug_prints:
			print msg