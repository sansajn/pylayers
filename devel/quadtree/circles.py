# -*- coding: utf-8 -*-
import sys, math, random, time
from PyQt4 import QtCore, QtGui
import quadtree


def main(args):
	app = QtGui.QApplication(args)
	form = Form()
	form.show()
	app.exec_()

class Form(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self, None)
		self.resize(800, 600)
		self.drawable = []
		self.qtree = None
		self.prepare_data()
		self.cursor_pos = (0,0)
		self.setMouseTracking(True)
		self.lookup_method = 0  # 0 - linear, 1 - quad tree
		self.set_title()

	def paintEvent(self, e):		
		painter = QtGui.QPainter()
		painter.begin(self)
		self.draw_window(painter)
		if self.lookup_method == 0:
			self.draw_circles_linear(painter)
		else:
			self.draw_circles_qtree(painter)
		painter.end()
		

	def mouseMoveEvent(self, e):
		self.cursor_pos = (e.x(), e.y())
		self.update()
		
	def keyPressEvent(self, e):
		if e.key() == QtCore.Qt.Key_L:
			self.lookup_method = (self.lookup_method+1)%2
		self.set_title()		

	def draw_window(self, painter):
		x,y = self.cursor_pos
		painter.drawPolyline(
			QtCore.QPoint(x-50, y+25),
			QtCore.QPoint(x+50, y+25),
			QtCore.QPoint(x+50, y-25),
			QtCore.QPoint(x-50, y-25),
			QtCore.QPoint(x-50, y+25))

	def draw_circles_linear(self, painter):
		t = time.time()
		r = QtCore.QRectF(self.cursor_pos[0]-50, self.cursor_pos[1]-25,
			100, 50)
		for d in self.drawable:
			if r.contains(d.pos[0], d.pos[1]):
				d.draw(painter)
		dt = time.time() - t
		print 'linear:%.5fs' % (dt, )

	def draw_circles_qtree(self, painter):
		t = time.time()
		r = QtCore.QRectF(self.cursor_pos[0]-50, self.cursor_pos[1]-25,
			100, 50)
		for idx in self.qtree.lookup(r):
			self.drawable[idx].draw(painter)
		dt = time.time() - t
		print 'quad-tree:%.5fs' % (dt, )
			
	def prepare_data(self):
		w,h = (self.width(), self.height())
		self.drawable = [drawable((w*random.random(), h*random.random()))
			for i in	range(0, 15000)]
		# quad tree
		qtree = quadtree.quad_tree(QtCore.QRectF(0, 0, w, h))
		for k,v in enumerate(self.drawable):
			qtree.insert(v.pos, k)
		self.qtree = qtree
		
	def set_title(self):
		title = ''
		if self.lookup_method == 0:
			title = 'Circles [linear]'
		else:
			title = 'Circes [quad-tree]'
		self.setWindowTitle(title) 


class drawable:
	def __init__(self, xypos):
		self.pos = xypos

	def draw(self, painter):
		x,y = self.pos
		painter.drawEllipse(x, y, 5, 5)



if __name__ == '__main__':
	main(sys.argv)

