# -*- coding: utf-8 -*-
from PyQt4 import QtCore
import gps


def qrect_to_grect(qrect):
	'skonvertuje qtrect na gps.gpsrect'
	r = qrect
	sw = r.topLeft()
	ne = r.bottomRight()
	return gps.georect(gps.gpspos(sw.x(), sw.y()), gps.gpspos(ne.x(), ne.y()))
		