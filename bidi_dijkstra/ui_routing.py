__author__ = 'Adam Hlavatovic'
from PyQt4 import QtCore, QtGui

class ui:
	'Implementuje ui pre hladanie v grafe'

	def __init__(self, layer):
		self._layer = layer  # toto je ako parent ?
		self._ui = None
		self._source_widget = None  # QLineEdit()
		self._target_widget = None  # QLineEdit()
		self._search_widget = None  # QPushButton()

		self._create()

	def source_vertex(self):
		return self._source_widget.text().toLong()[0]

	def target_vertex(self):
		return self._target_widget.text().toLong()[0]

	def on_search_connect(self, handler):
		self._search_widget.clicked.connect(handler)

	def reference(self):
		'Gets reference to routing ui (dock).'
		return self._ui

	def _create(self):
		vlayout = QtGui.QVBoxLayout()

		# source
		label = QtGui.QLabel('Source vertex:')
		edit = QtGui.QLineEdit()
		hlayout = QtGui.QHBoxLayout()
		hlayout.addWidget(label)
		hlayout.addWidget(edit)
		vlayout.addLayout(hlayout)
		self._source_widget = edit

		# target
		label = QtGui.QLabel('Target vertex :')
		edit = QtGui.QLineEdit()
		hlayout = QtGui.QHBoxLayout()
		hlayout.addWidget(label)
		hlayout.addWidget(edit)
		vlayout.addLayout(hlayout)
		self._target_widget = edit

		# search
		search_btn = QtGui.QPushButton('Search')
		hlayout = QtGui.QHBoxLayout()
		hlayout.addWidget(search_btn)
		vlayout.addLayout(hlayout)
		self._search_widget = search_btn

		dock = QtGui.QDockWidget('Routing', self._layer.widget)
		dock.setAllowedAreas(
			QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea)

		child_widget = QtGui.QWidget()
		child_widget.setLayout(vlayout)
		child_widget.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

		dock.setWidget(child_widget)

		self._ui = dock
