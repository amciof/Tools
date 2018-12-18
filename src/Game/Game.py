import sys
sys.path.append('../')

from queue import Queue

from PyQt5.QtGui     import QPainter
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel
from PyQt5.QtGui     import QIcon, QPainter, QColor, QBrush
from PyQt5.QtCore    import Qt

from Networking.Networking import Network, Options, Action

from Render.Scene import Scene

from Game.GameElements import BaseType, Base, Town, Market, Storage, Road, Speed, Train
from Game.Player	   import Player

from Strategy.SingleTrainStrategy    import SingleTrainStrategy
from Strategy.MultipleTrainsStrategy import ItJustWorks


class Game(QWidget):
	# Button Keys
	BUTTON_LEFT  = 1
	BUTTON_RIGHT = 2

	# Game Consts
	GAME_TICK  = 5000
	FRAME_TICK = 17

	POLL_TICK  = 750
	
	WHEEL_SENSITIVITY = 1000

	#init methods
	def __init__(self, client, playerName, window):
		self.__initWindow(window)

		self.__initAsyncInfo()

		self.__initNetwork(client, playerName)


		self.net.requestPlayer(self.primary)
		token, playerResp = self.primary.get(True)

		self.net.requestMap(self.primary, Options.LAYER_0)
		token, mapResp0 = self.primary.get(True)

		self.net.requestMap(self.primary, Options.LAYER_1)
		token, mapResp1 = self.primary.get(True)


		self.__initBases(mapResp0.msg, mapResp1.msg)

		self.__initRoads(mapResp0.msg)

		self.__initAdjacencyRel(mapResp0.msg)

		self.__initTrains(playerResp.msg)

		self.__initScene()
		
		self.__initPlayer(playerResp.msg)

		self.__initStateParams()

		self.__initStrategy()


	def __initWindow(self, window):
		QWidget.__init__(self, window)

		self.setGeometry(0, 0, window.size().width(), window.size().height())

	def __initNetwork(self, client, playerName):
		self.playerName = playerName
		self.net = client

	def __initBases(self, jsonMap0, jsonMap1):
		self.bases = {}

		for base in jsonMap1['posts']:
			idx = base['point_idx']
			if base['type'] == BaseType.TOWN:
				self.bases[idx] = Town(base)
			elif base['type'] == BaseType.MARKET:
				self.bases[idx] = Market(base)
			elif base['type'] == BaseType.STORAGE:
				self.bases[idx] = Storage(base)

		for jsonPoint in jsonMap0['points']:
			idx  = jsonPoint['idx']
			name = 'base ' + str(idx)

			if not idx in self.bases:
				self.bases[idx] = Base(name, idx, BaseType.BASE)

	def __initRoads(self, jsonMap):
		self.roads = {}

		for jsonLine in jsonMap['lines']:
			idx          = jsonLine['idx']
			base1, base2 = jsonLine['points']

			self.roads[idx] = Road(jsonLine, self.bases[base1], self.bases[base2])
	
	def __initAdjacencyRel(self, jsonMap):
		self.adjacencyRel = {idx : {} for idx in self.bases}

		for road in self.roads.values():
			u, v = road.getAdjacentIdx()

			self.adjacencyRel[u][v] = road
			self.adjacencyRel[v][u] = road

	def __initTrains(self, jsonLogin):
		self.trains = {}

		for jsonTrain in jsonLogin['trains']:
			idx     = jsonTrain['idx']
			roadIdx = jsonTrain['line_idx']

			self.trains[idx] = Train(jsonTrain, self.roads[roadIdx])

	def __initScene(self):
		self.scene = Scene(
			self.bases
			, self.roads
			, self.trains
			, (self.size().width(), self.size().height())
		)

	def __initPlayer(self, jsonPlayer):

		self.player = Player(jsonPlayer)

	def __initStateParams(self):
		self.draging = False
		self.lastX = None
		self.lastY = None

	def __initStrategy(self):
		
		self.strategy = ItJustWorks(self)

	def __initAsyncInfo(self):
		self.primary   = Queue()
		self.secondary = Queue()

		self.primaryExpect   = set()
		self.secondaryExpect = set()

		self.shouldTurn = False


	#logic
	def start(self):
		self.gameTickID  = self.startTimer(Game.GAME_TICK)
		self.frameTickID = self.startTimer(Game.FRAME_TICK)
		self.pollTickID  = self.startTimer(Game.POLL_TICK)
		self._turn()


	#events
	def paintEvent(self, event):
		context = QPainter(self)
		self.scene.renderScene(context)
		context.end()


	def mousePressEvent(self, event):
		if event.button() == Game.BUTTON_LEFT:
			self.draging = True
			self.lastX   = event.x()
			self.lastY   = event.y()

	def mouseReleaseEvent(self, event):
		if self.draging:
			self.draging = False

	def mouseMoveEvent(self, event):
		if self.draging:
			x = event.x()
			y = event.y()
			dx = self.lastX - x
			dy = self.lastY - y
			self.lastX = x
			self.lastY = y
			self.scene.moveCam(dx, dy)

	def wheelEvent(self, event):

		self.scene.zoomCam(event.angleDelta().y() / Game.WHEEL_SENSITIVITY)


	def timerEvent(self, event):
		if event.timerId() == self.gameTickID:
			self.shouldTurn = True
			self._gameTick()

		elif event.timerId() == self.frameTickID:
			self.update()

		elif event.timerId() == self.pollTickID:
			self.__tryPollSecondary()
			self.__tryPollPrimary()

			if self.shouldTurn:
				self._gameTick()

			
	#polling methods
	def __tryPollPrimary(self):
		#MAP
		while not self.primary.empty():
			token, resp = self.primary.get()

			if token in self.primaryExpect:
				self.primaryExpect.remove(token)

				action = resp.action
				if action == Action.MAP:
					print('Map: ', token)
					self._updateState(resp)

	def __tryPollSecondary(self):
		#MOVE TURN UPGRADE
		while not self.secondary.empty():
			token, resp = self.secondary.get()

			if token in self.secondaryExpect:
				self.secondaryExpect.remove(token)

				action = resp.action
				if action == Action.MOVE:
					print('Move: ', token)
				elif action == Action.TURN:
					print('Turn: ', token)
				elif action == Action.UPGRADE:
					print('Upgrade: ', token)


	#called from timer
	def _gameTick(self):
		if len(self.primaryExpect) != 0 or len(self.secondaryExpect) != 0:
			return

		self.shouldTurn = False

		print('$$$ Game tick $$$')
		token = self.net.requestTurn(self.secondary)
		print('turn token is ', token)
		self.secondaryExpect.add(token)

		token = self.net.requestMap(self.primary, Options.LAYER_1)
		print('map token is ', token)
		self.primaryExpect.add(token)

		self._turn()

	#called from gametick & start
	def _turn(self):
		actions = self.strategy.getActions()

		for idx, action in actions[Action.MOVE].items():
			token = self.net.requestMove(self.secondary, action[0], action[1], action[2])
			print('train %i move token is %i' % (idx, token))
			self.secondaryExpect.add(token)
		
		token = self.net.requestUpgrade(
			self.secondary
			, actions[Action.UPGRADE]['posts']
			, actions[Action.UPGRADE]['trains']
		)
		print('upgrade token is ', token)
		self.secondaryExpect.add(token)


	#called from pollRequests
	def _updateState(self, mapLayer1):
		self._updateBases(mapLayer1)
		self._updateTrains(mapLayer1)

	def _updateBases(self, mapLayer1):
		for jsonBase in mapLayer1.msg['posts']:
			idx = jsonBase['point_idx']

			self.bases[idx].update(jsonBase)
	
	def _updateTrains(self, mapLayer1):
		for jsonTrain in mapLayer1.msg['trains']:
			roadIdx = jsonTrain['line_idx']
			road    = self.roads[roadIdx]

			idx = jsonTrain['idx']

			train = self.trains[idx]

			# print('---Before---')
			# train.printStats()

			train.update(jsonTrain, {'road' : road})

			# print('---After---')
			# train.printStats()

			self.scene.updateTrain(train)
