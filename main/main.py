#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import json
import networkx as nx

from screeninfo import get_monitors

from PyQt5.QtWidgets import qApp, QMainWindow, QAction, QFileDialog, QSizePolicy, QApplication, QVBoxLayout
from PyQt5.QtGui import QIcon

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


DEFAULT_DPI = 100
MENU_SHIFT  = 20

class Application(QApplication):

	def __init__(self, args):
		QApplication.__init__(self, args)


	def mouseMoveEvent(self, event):
		print('FUCK YEAH')
		QApplication.mouseMoveEvent(self, event)

	def mousePressEvent(self, event):
		print('FUCK YEAH')
		QApplication.mousePressEvent(self, event)

class MainWindow(QMainWindow):

	def __init__(self, width, height):
		QMainWindow.__init__(self)
		self.initUI(width, height )

	#UI
	def initUI(self, width, height):
		self.initMainWindow(width, height)

		self.initCanvas(width, height)
		
		self.initMenu()


	def initMainWindow(self, width, height):
		self.setFixedSize(width * DEFAULT_DPI, height * DEFAULT_DPI + MENU_SHIFT)
		self.setWindowTitle('WG Forge')
		self.setWindowIcon(QIcon('logo.png')) 

	def initCanvas(self, width, height):
		self.canvas = CustomCanvas(self, width, height)
		self.canvas.move(0, MENU_SHIFT)

	def initMenu(self):
		open_action = QAction('Open', self)
		open_action.triggered.connect(self.open)

		save_action = QAction('Save', self)
		save_action.triggered.connect(self.save)

		exit_action = QAction(QIcon('exit.png'), 'Exit', self)
		exit_action.triggered.connect(qApp.quit)

		self.menu_bar = self.menuBar()
		self.file_menu = self.menu_bar.addMenu('File')
		self.file_menu.addAction(open_action)
		self.file_menu.addAction(save_action)
		self.file_menu.addAction(exit_action)


	#actions
	def open(self):
		filename = QFileDialog.getOpenFileName(self, 'Select file', '', 'Json (*.json)')
		if filename[0]:
			with open(filename[0], 'r') as file:
				graph = json.load(file)
				self.canvas.plot(graph)

	def save(self):
		filename = QFileDialog.getSaveFileName(self, 'Select file', '', 'Png (*.png)')
		if filename[0]:
			self.canvas.figure.savefig(filename[0])


#matplotlib canvas
class CustomCanvas(FigureCanvas):

	def __init__(self, parent, width, height):
		figure = Figure(figsize=(width, height), dpi=DEFAULT_DPI)
		FigureCanvas.__init__(self, figure)

		self.setParent(parent)
		#FigureCanvas.setSizePolicy(self,
		#	QSizePolicy.Expanding,
		#	QSizePolicy.Expanding
		#)
		FigureCanvas.updateGeometry(self)


	def plot(self, graph):
		G = nx.Graph()

		for line in graph['lines']:
			G.add_edge(line['points'][0], line['points'][1], weight=line['length'])

		for point in graph['points']:
			G.add_node(point['idx'])

		pos = nx.spring_layout(G, iterations=200)
		edge_labels = {(u, v): d['weight'] for u, v, d in G.edges(data=True)}

		self.figure.clear()
		axes = self.figure.add_subplot(111)
		
		options = {
			'node_color': 'yellow',
			'node_size': 100,
			'width': 1,
			'with_labels': True
		}

		nx.draw(G, pos, ax=axes, alpha=1, **options)
		nx.draw_networkx_edge_labels(G, pos, ax=axes, edge_labels=edge_labels, **options)

		self.draw()

		

if __name__ == '__main__':
	monitors = get_monitors()
	width  = min(monitors, key = lambda x: x.width).width
	height = min(monitors, key = lambda x: x.height).height
	width  //= 2
	width  //= DEFAULT_DPI
	height //= 2
	height //= DEFAULT_DPI

	#app = QApplication(sys.argv)
	app = Application(sys.argv)
	main_window = MainWindow(width, height)
	main_window.show()
	sys.exit(app.exec_())
