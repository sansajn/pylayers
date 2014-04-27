# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
import geometry
import layer_interface
import text_helper
import gps
import layers_manip

class layer(layer_interface.layer):
	'Zobrazi GPS log.'

	def __init__(self, widget):
		layer_interface.layer.__init__(self)
		self.name = 'location_layer'
		self._widget = widget
		self._zoom = None
		self._base_points = []
		self._times = []  # in ms
		self._edges = []
		self._vertex_id_under_cursor = None
		self._selected_vertices_id = []

	def create(self, uri):
		# precitaj gps log
		rows = text_helper.textread(uri, ',', [int, float, float, float, float])
		t_start = rows[0][0]
		for r in rows:
			self._times.append(r[0]-t_start)
			self._base_points.append(gps.mercator.gps2xybase((r[1], r[2])))

		# nastav pohlad
		layers_manip.zoom(self._widget).to_baserect(self._points_bounds())

	def paint(self, painter, view_offset):
		# path
		painter.setPen(QtCore.Qt.black)
		for e in self._edges:
			e.paint(painter, view_offset)

		# vertex under cursor
		if self._vertex_id_under_cursor is not None:
			self._draw_vertex_under_cursor(self._vertex_id_under_cursor, painter)

		# selected vertices
		for vid in self._selected_vertices_id:
			self._draw_selected_vertex(vid, painter)

	def zoom_event(self, zoom):
		self._zoom = zoom
		self._prepare_drawable_data()

	def mouse_move_event(self, event):
		vid = self._find_vertex_under_cursor(self._cursor_xy_to_xybase(event.pos()))
		if vid != self._vertex_id_under_cursor:
			self._vertex_id_under_cursor = vid
			self._update()

	def mouse_release_event(self, event):
		vid = self._find_vertex_under_cursor(self._cursor_xy_to_xybase(event.pos()))
		if vid is None:
			return

		if vid in self._selected_vertices_id:
			self._selected_vertices_id.remove(vid)
		else:
			self._selected_vertices_id.append(vid)

		# netreba robit update (o to sa postara mouse_move)

	def _cursor_xy_to_xybase(self, cursor_pos):
		# (?) <> jak toto moze fungovat, ked pozicia mysi je od laveho horneho rohu ?
		point_local = (cursor_pos.x(), cursor_pos.y())
		point_world = self._widget.to_world_coordinates(point_local)
		return gps.mercator.xy2xybase(point_world, self._zoom)

	def _prepare_drawable_data(self):
		edges = []
		verts = self._base_points
		for i in range(1, len(verts)):
			edges.append(to_drawable_edge(verts[i-1], verts[i], self._zoom))
		self._edges = edges

	def _find_vertex_under_cursor(self, cursor_xybase):
		verts = self._base_points
		dists = []
		for v in verts:
			dists.append(point_distance(v, cursor_xybase))

		min_idx = min_val_idx(dists)
		min_dist = dists[min_idx]*(gps.mercator.zoom_scale(self._zoom)**2)
		if min_idx != -1 and min_dist < 500:
			return min_idx

		return None

	def _update(self):
		self._widget.update()

	def _draw_vertex_under_cursor(self, vid, painter):
		v = self._base_points[vid]
		v_xy = layers_manip.window_coordinate(self._widget).from_xybase(v, self._zoom)
		painter.save()
		# vertex
		painter.setBrush(QtGui.QBrush(QtCore.Qt.red))
		painter.drawRect(v_xy[0]-2, v_xy[1]-2, 4, 4)
		# id, time
		v_text = 'v:%d, t:%.2fs' % (vid, self._times[vid]/1000.0)
		if self._vertex_selected() and vid != self._selected_vertices_id[0]:
			v_text += ' (%.2fs)' % (
				(self._times[vid] - self._times[self._selected_vertices_id[0]])/1000.0, )
		font = painter.font()
		fm = QtGui.QFontMetricsF(font)
		rc_text = fm.boundingRect(v_text)
		painter.setPen(QtCore.Qt.black)
		painter.drawText(QtCore.QPointF(v_xy[0], v_xy[1]) +
			QtCore.QPointF(-rc_text.width()/2.0, -5), v_text)
		painter.restore()

	def _draw_selected_vertex(self, vid, painter):
		self._draw_vertex_under_cursor(vid, painter)

	def _points_bounds(self):
		verts = self._base_points
		r = geometry.rectangle(verts[0], verts[1])
		for v in verts:
			r.expand(v)
		return r
	
	def _vertex_selected(self):
		return len(self._selected_vertices_id) > 0

	VERTEX_UPDER_CURSOR = 1


class edge:
	def __init__(self, a, b):
		'a,b su body, vyraz a[0], a[1] musi platit'
		self.a = a
		self.b = b

	def paint(self, painter, view_offset):
		x0,y0 = view_offset
		s = (self.a[0]+x0, self.a[1]+y0)
		t = (self.b[0]+x0, self.b[1]+y0)
		painter.drawLine(s[0], s[1], t[0], t[1])
		if point_distance(s, t) > (1.5*edge.RECT_SIZE)**2:
			painter.drawRect(s[0]-edge.RECT_SIZE_HALF, s[1]-edge.RECT_SIZE_HALF,
				edge.RECT_SIZE, edge.RECT_SIZE)
			painter.drawRect(t[0]-edge.RECT_SIZE_HALF, t[1]-edge.RECT_SIZE_HALF,
				edge.RECT_SIZE, edge.RECT_SIZE)

	RECT_SIZE = 6
	RECT_SIZE_HALF = RECT_SIZE/2


def to_drawable_edge(s, t, zoom):
	return edge(
		gps.mercator.apply_zoom(s, zoom), gps.mercator.apply_zoom(t, zoom)
	)

def min_val_idx(seq):
	first = True
	min_idx, min_val = (-1, None)
	for k,v in enumerate(seq):
		if not first:
			if v < min_val:
				min_idx = k
				min_val = v
		else:
			min_idx = k
			min_val = v
			first = False
	return min_idx

def point_distance(a, b):
		return (b[0] - a[0])**2 + (b[1] - a[1])**2