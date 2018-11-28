import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel
from PyQt5.QtGui  import QIcon, QPainter, QColor, QBrush
from PyQt5.QtCore import Qt
import random

from Game import Game


SERVER_ADDR = 'wgforge-srv.wargaming.net'
SERVER_PORT = 443
PLAYER = 'Waifu'


class App(QMainWindow):

	def __init__(self):
		super().__init__()

		self.title = 'Anime kills'
		self.left   = 100
		self.top    = 100
		self.width  = 1280
		self.height = 720


		self.initUI()

		self.show()

	def initUI(self):
		#will be reworked
		self.setGeometry(self.left, self.top, self.width, self.height)
		self.setFixedSize(self.width, self.height)

		self.game = Game(SERVER_ADDR, SERVER_PORT, PLAYER, self)

		self.setWindowTitle(self.title)
		

	def event(self, event):
		self.game.update(event)
		return QMainWindow.event(self, event)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = App()
	sys.exit(app.exec_())