import sys, math, re
from PyQt4 import QtCore, QtGui


class Form(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self, None)

	def mousePressEvent(self, e):
		fname = QtGui.QFileDialog.getOpenFileName(self, 'Open path dump file ...')
		if fname:
			print fname
		else:
			print 'nothing choosen'

def main(args):
	app = QtGui.QApplication(args)
	form = Form()
	form.show()
	app.exec_()


if __name__ == '__main__':
	main(sys.argv)
