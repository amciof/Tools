import sys
sys.path.append('../')

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel
from PyQt5.QtGui  import QIcon, QPainter, QColor, QBrush
from PyQt5.QtCore import Qt
import random

from Game.Game import Game


class App(QMainWindow):

	def __init__(self, client, player, startX, startY, width, height):
		super().__init__()

		self.title = 'WG'

		self.setGeometry(startX, startY, width, height)
		self.setFixedSize(width, height)
		self.setWindowTitle(self.title)

		self.game = Game(client, player, self)
		self.game.start()
		self.game.show()

		self.show()

	def initUI(self):
		pass