import sqlite3
from PyQt4 import QtCore, QtGui
import layer_interface, gps

class layer(layer_interface.layer):
	def __init__(self, widget):
		self.stops = []  # our journey as [(stop, code)]
		self.location = []  # stop locations
		self.drawables = []
		self.zoom = 0

	def create(self, uri):
		'''\param uri journey database file'''
		sql3 = sqlite3.connect(uri)
		cur = sql3.cursor()

		line = 'U1'
		direction = 'A'
		result = cur.execute('SELECT stop_name_public, stop_number_infotainment_direction_0 FROM stops WHERE line_name=? AND direction=?',
			(line, direction))
		self.stops = result.fetchall()

		cur.close()
		sql3.close()

		for (stop, code) in self.stops:
			print(stop)

		# dummy data
		self.location = [
			(53.7083916, 9.992326694419697),
			(53.6957725, 9.9897878),
			(53.6844739, 9.9860415),
			(53.6780751, 10.0018152),
			(53.6749843, 10.0161807),
			(53.6609764, 10.0175721),
			(53.6488888, 10.0172131),
			(53.6392522, 10.0166781),
			(53.6323399, 10.0233695),
			(53.6280261, 10.0332975),
			(53.6215437, 10.0377601),
			(53.6093178, 10.02204),
			(53.6105412, 10.0038889),
			(54.52979405000001, 9.529477464246366),
			(53.5945497, 9.9961041),
			(53.58877715, 9.990776246165055),
			(53.5816738, 9.988216),
			(49.0728763, 9.5100571),
			(53.5587463, 9.9893053),
			(53.5520952, 9.9933974),
			(49.9128727, 9.6906155),
			(53.5492731, 10.0062431),
			(53.5521608, 10.0093336),
			(53.5565393, 10.0188852),
			(53.5597781, 10.0287328),
			(53.5646508, 10.0354076),
			(53.5676565, 10.04668),
			(53.5696668, 10.0600205),
			(53.5716636, 10.0667414),
			(53.5820205, 10.0678807),
			(53.5862016, 10.0649307),
			(53.5923256, 10.0743469),
			(53.598434, 10.1028727),
			(53.607222, 10.1177994),
			(53.61287, 10.1469662),
			(46.9482713, 7.4514512),
			(53.6386437, 10.1559218),
			(53.6485554, 10.1647514),
			(53.6485554, 10.1647514),
			(37.3487019, -83.4762961),
			(53.6777026, 10.1478672),
			(53.6942752, 10.1371187),
			(53.6529577, 10.1850709),
			(53.6646389, 10.219403),
			(53.6613469, 10.2422404),
			(53.6533879, 10.2601856),
			(53.6530231, 10.2802566),
			(53.6635561, 10.2835977)]
		
	def paint(self, painter, view_offset):
		for d in self.drawables:
			d.paint(painter, view_offset)

	def zoom_event(self, zoom):
		self.zoom = zoom
		self._prepare_drawables()

	def _prepare_drawables(self):
		for loc in self.location:
			self.drawables.append(to_drawable_mark(loc, self.zoom))
		print('we have %d drawables to draw' % len(self.drawables))




def to_drawable_mark(latlon, zoom):
	vpos = latlon
	vpos_xy = gps.mercator.gps2xy(gps.gpspos(vpos[0], vpos[1]), zoom)
	return drawable_mark(vpos_xy, 5)


class drawable_mark:
	def __init__(self, xypos, r):
		self.xypos = QtCore.QPoint(xypos[0], xypos[1])
		self.r = r

	def paint(self, painter, view_offset):
		painter.save()
		
		black_solid_pen = QtGui.QPen(QtGui.QColor(0, 0, 0))
		black_solid_pen.setStyle(QtCore.Qt.SolidLine)
		black_solid_pen.setWidth(5)

		red_brush = QtGui.QBrush(QtGui.QColor(222, 0, 0))

		painter.setPen(black_solid_pen)
		painter.setBrush(red_brush)		

		x0,y0 = view_offset
		painter.drawEllipse(self.xypos.x()+x0-self.r, 
			self.xypos.y()+y0-self.r, 2*self.r, 2*self.r)

		painter.restore()
