# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui


def main(args):
	app = QtGui.QApplication(args)
	wnd = main_window()
	wnd.show()
	return app.exec_()


class vertex_item(QtGui.QGraphicsItem):
	def __init__(self):
		QtGui.QGraphicsItem.__init__(self)
		self.edges = []
		self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)

	# public
	def add_edge(self, e):
		self.edges.append(e)

	def paint(self, painter, option, widget):
		painter.setBrush(QtCore.Qt.white)
		painter.drawEllipse(0, 0, 10, 10)

	def boundingRect(self):
		return QtCore.QRectF(0, 0, 10, 10)


class edge_item(QtGui.QGraphicsItem):
	def __init__(self, s, t):
		QtGui.QGraphicsItem.__init__(self)
		s.add_edge(self)
		t.add_edge(self)
		self.source = s
		self.target = t

	def paint(self, painter, option, widget):
		a,b = self.from_to_points()
		painter.drawLine(a[0], a[1], b[0], b[1])	

	def boundingRect(self):
		a,b = self.from_to_points()
		return QtCore.QRectF(a[0], b[1], b[0]-a[0], a[1]-b[1])

	def from_to_points(self):
		rc = self.source.boundingRect()
		a = (rc.left()+rc.width()/2, rc.bottom()-rc.heigth()/2)
		rc = self.target.boundingRect()
		b = (rc.left()+rc.width()/2, rc.bottom()-rc.heigth()/2)
		return (a, b)



class view_widget(QtGui.QGraphicsView):
	def __init__(self, parent):
		QtGui.QGraphicsView.__init__(self)
		scene = QtGui.QGraphicsScene(self)
		self.setScene(scene)

		vertex1 = vertex_item(11, parent)
		vertex2 = vertex_item(22, parent)
		edge1 = edge_item(vertex1, vertex2)

		vertex.setPos(100, 100)
		vertex2.setPos(200, 150)


		scene.addItem(vertex)
		scene.addItem(vertex2)


class main_window(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		self.view = view_widget(self)
		self.setCentralWidget(self.view)
		self.resize(800, 600)


if __name__ == '__main__':
	main(sys.argv)
	


