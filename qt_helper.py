# -*- coding: utf-8 -*-
from PyQt4 import QtCore
import gps


def qrect_to_grect(qrect):
	'skonvertuje qtrect na gps.georect'
	r = qrect
	sw = r.topLeft()
	ne = r.bottomRight()
	return gps.georect(gps.gpspos(sw.x(), sw.y()), gps.gpspos(ne.x(), ne.y()))

def grect_to_qrect(grect):
	'skonvertuje gps.georect na qrect'
	r = grect
	return QtCore.QRectF(QtCore.QPointF(r.sw.lat, r.sw.lon), 
		QtCore.QPointF(r.ne.lat, r.ne.lon))
