import sys
import random
from queue import Queue

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel
from PyQt5.QtGui  import QIcon, QPainter, QColor, QBrush
from PyQt5.QtCore import Qt

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
		self.outQueue = Queue()
		self.client   = Network(SERVER_ADDR, SERVER_PORT)
		self.client.start()


	def run(self):
		print("PEPE SOFT©                         ")
		print("           .--._.--.               ")
		print("          ( O     O )              ")
		print("          /   . .   \              ")
		print("         .`._______.'.             ")
		print("        /(           )\            ")
		print("      _/  \  \   /  /  \_          ")
		print("   .~   `  \  \ /  /  '   ~.       ")
		print("  {    -.   \  V  /   .-    }      ")
		print("_ _`.    \  |  |  |  /    .'_ _    ")
		print(">_________} |  |  | {_________<    ")
		print()

		while True:
			print('Enter command')
			command = input()

			if command == Command.LOGIN:
				if self.__login():
					break;

			elif command == Command.GAMES:
				self.__games()

			elif command == Command.HELP:
				self.__help()

			elif command == Command.END:
				break

			else:
				self.__invalid()
			print()

		self.client.terminate()


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
				if self.__login_join(nickname, password):
					return True
				else:
					return False

			elif option == 'new':
				if self.__login_new(nickname, password):
					return True
				else:
					return False

			else:
				print('Bad input. Try again')

	def __login_join(self, nickname, password):
		print('Choose game to connect:')
		self.__games()

		game = input()

		token = self.client.requestLogin(self.outQueue, nickname, password, game)
		token, resp = self.outQueue.get(True)

		app = QApplication(sys.argv)
		ex  = App(self.client, nickname, 200, 200, 1280, 720)
		app.exec_()

		token = self.client.requestLogout(self.outQueue)
		token, resp = self.outQueue.get(True)

		return True;

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


		token = self.client.requestLogin(self.outQueue, nickname, password, None, num_turns, num_players)
		token, resp = self.outQueue.get(True)

		app = QApplication(sys.argv)
		ex  = App(self.client, nickname, 200, 200, 1280, 720)
		app.exec_()

		token = self.client.requestLogout(self.outQueue)
		token, resp = self.outQueue.get(True)

		return True

	
	def __games(self):
		print('**Available games**')
		token = self.client.requestGames(self.outQueue)
		token, resp = self.outQueue.get(True)

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