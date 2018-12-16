
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


class Command:
	END   = 'end'
	LOGIN = 'login'
	GAMES = 'games'
	HELP  = 'help'

class Shell:
	STATES = {
		  1: 'initializing'
		, 2: 'running'
		, 3: 'finished'
	}

	def __init__(self):

		self.client  = Network(SERVER_ADDR, SERVER_PORT)

	def run(self):
		while True:
			print('Enter command')
			command = input()

			if command == Command.LOGIN:
				self.__login()

			elif command == Command.GAMES:
				self.__games()

			elif command == Command.HELP:
				self.__help()

			elif command == Command.END:
				break

			else:
				self.__invalid()
			print()


	#commands
	def __login(self):
		print('Enter nickname: ')
		nickname = input()

		print('Enter password: ')
		password = input()

		while True:
			print('Join game or create new?(join/new)')

			option = input()

			if option == 'join':
				self.__login_join(nickname, password)
				break

			elif option == 'new':
				self.__login_new(nickname, password)
				break

			else:
				print('Bad input. Try again')

	def __login_join(self, nickname, password):
		print('Choose game to connect:')
		self.__games()

		game = input()

		resp = self.client.requestLogin(nickname, password, game)

		app = QApplication(sys.argv)
		ex  = App(self.client, nickname, 200, 200, 1280, 720)
		app.exec_()

		resp = self.client.requestLogout()

	def __login_new(self, nickname, password):
		print('Enter number of players: ')
		num_players = input()
		try:
			num_players = int(num_players)
			if num_players > 4 or num_players < 0:
				print('Setting to default value 1: ')
				num_players = 1
		except ValueError as e:
			print('Setting to default value 1: ')
			num_players = 1

		print('Enter number of turns(game duration)')
		num_turns = input()
		try:
			num_turns = int(num_turns)
		except ValueError as e:
			print('Setting to default value -1: ')
			num_turns = -1


		resp = self.client.requestLogin(nickname, password, None, num_turns, num_players)

		app = QApplication(sys.argv)
		ex  = App(self.client, nickname, 200, 200, 1280, 720)
		app.exec_()

		resp = self.client.requestLogout()

	
	def __games(self):
		print('**Available games**')
		resp = self.client.requestGames()
		print('[RESULT: %i]' % (resp.result))
		for game in resp.msg['games']:
			print('Name   : ', game['name'])
			print('Players: ', game['num_players'])
			print('Turns  : ', game['num_turns'])
			print('State  : ', Shell.STATES[game['state']])
			print()


	def __help(self):
		print('---Commands---')
		print('help')
		print('login')
		print('games')
		print('end')


	def __invalid(self):

		print('Invalid command')


if __name__ == '__main__':
	shell = Shell()
	shell.run()		