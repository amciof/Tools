import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel
from PyQt5.QtGui  import QIcon, QPainter, QColor, QBrush
from PyQt5.QtCore import Qt
import random

from Game import Game


SERVER_ADDR = 'wgforge-srv.wargaming.net'
SERVER_PORT = 443
PLAYER = 'A.D.'


class App(QMainWindow):

	def __init__(self, startX, startY, width, height):
		super().__init__()

		self.title = 'WG'

		self.setGeometry(startX, startY, width, height)
		self.setFixedSize(width, height)
		self.setWindowTitle(self.title)

		self.game = Game(SERVER_ADDR, SERVER_PORT, PLAYER, self)
		self.game.start()
		self.game.show()

		self.show()


	def initUI(self):
		pass


if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = App(200, 200, 1280, 720)
	sys.exit(app.exec_())
		