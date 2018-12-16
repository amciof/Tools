import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel
from PyQt5.QtGui  import QIcon, QPainter, QColor, QBrush
from PyQt5.QtCore import Qt
import random

from GUI.Application import App
from Networking.Networking import Network
from Game.Game import Game


SERVER_ADDR = 'wgforge-srv.wargaming.net'
SERVER_PORT = 443
PLAYER = 'A.D.'

if __name__ == '__main__':
	client = Network(SERVER_ADDR, SERVER_PORT)
	app    = QApplication(sys.argv)
	resp   = client.requestLogin(PLAYER, PLAYER)
	ex     = App(client, PLAYER, 200, 200, 1280, 720)
	sys.exit(app.exec_())

	resp   = client.requestLogout()
		