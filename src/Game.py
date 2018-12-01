from PyQt5.QtGui  		import QPainter

from Networking		import Network, Options
from Scene			import Scene
from SceneElements	import Base, Town, Market, Storage, Road, Speed, Train
from Player			import Player
from Strategy		import Strategy


class Game:

	# Event Consts
	EVENT_TIMER 		= 1
	EVENT_MOUSE_PRESS   = 2
	EVENT_MOUSE_RELEASE = 3
	EVENT_MOUSE_MOVE    = 5
	EVENT_MOUSE_WHEEL   = 31
	EVENT_PAINT 		= 12

	# Button Keys
	BUTTON_LEFT  = 1
	BUTTON_RIGHT = 2

	# Game Consts
	GAME_TICK  = 1000
	FRAME_TICK = 16
	WHEEL_SENSITIVITY = 1000

	def __init__(self, serverAddr, portNum, playerName, window):
		self.__initParent(window)

		self.__initNetwork(serverAddr, portNum)

		playerResp = self.net.requestLogin(playerName)
		mapResp0   = self.net.requestMap(Options.LAYER_0)
		mapResp1   = self.net.requestMap(Options.LAYER_1)

		self.__initBases(mapResp0.msg, mapResp1.msg)

		self.__initRoads(mapResp0.msg)

		self.__initAdjacencyRel(mapResp0.msg)

		self.__initTrains(playerResp.msg)

		self.__initScene()
		
		self.__initPlayer(playerResp.msg)

		self.__initStateParams()

		self.__initStrategy()


	def __initParent(self, window):
		self.window = window

	def __initNetwork(self, serverAddr, portNum):
		self.net = Network(serverAddr, portNum)

	def __initBases(self, jsonMap0, jsonMap1):
		self.bases = {}

		for base in jsonMap1['posts']:
			idx = base['point_idx']
			if base['type'] == Base.TOWN:
				self.bases[idx] = Town(base)
			elif base['type'] == Base.MARKET:
				self.bases[idx] = Market(base)
			elif base['type'] == Base.STORAGE:
				self.bases[idx] = Storage(base)

		for jsonPoint in jsonMap0['points']:
			idx  = jsonPoint['idx']
			name = 'base ' + str(idx)

			if not idx in self.bases:
				self.bases[idx] = Base(name, idx, Base.BASE)

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
			, self.window
		)

	def __initPlayer(self, jsonPlayer):
		self.player = Player(jsonPlayer)

	def __initStateParams(self):
		self.draging = False
		self.lastX = None
		self.lastY = None

	def __initStrategy(self):
		self.strategy = Strategy(self)

	# Logic
	def start(self):
		self.gameTickID  = self.window.startTimer(Game.GAME_TICK)
		self.frameTickID = self.window.startTimer(Game.FRAME_TICK)
		self._turn()

	# Update
	def update(self, event):
		if event.type() == Game.EVENT_MOUSE_PRESS:
			self.handleMousePress(event)

		elif event.type() == Game.EVENT_MOUSE_RELEASE:
			self.handleMouseRelease(event)

		elif event.type() == Game.EVENT_MOUSE_MOVE:
			self.handleMouseMove(event)

		elif event.type() == Game.EVENT_MOUSE_WHEEL:
			self.handleMouseWheel(event)

		elif event.type() == Game.EVENT_PAINT:
			self.render()

		elif event.type() == Game.EVENT_TIMER:
			self.handleTimerEvent(event)

	# Render
	def render(self):
		context = QPainter(self.window)
		self.scene.renderScene(context)
		context.end()

	# Mouse
	def handleMousePress(self, event):
		if event.button() == Game.BUTTON_LEFT:
			self.draging = True
			self.lastX   = event.x()
			self.lastY   = event.y()

	def handleMouseRelease(self, event):
		if self.draging:
			self.draging = False

	def handleMouseMove(self, event):
		if self.draging:
			x = event.x()
			y = event.y()
			dx = self.lastX - x
			dy = self.lastY - y
			self.lastX = x
			self.lastY = y
			self.scene.moveCam(dx, dy)

	def handleMouseWheel(self, event):
		self.scene.zoomCam(event.angleDelta().y() / Game.WHEEL_SENSITIVITY)

	# Timers
	def handleTimerEvent(self, event):
		if event.timerId() == self.gameTickID:
			self._gameTick()
		elif event.timerId() == self.frameTickID:
			self.window.update()

	def _gameTick(self):
		self._turn()
		self._updateState()

	def _turn(self):
		moves = self.strategy.getMoves()
		for move in moves:
			self.net.requestMove(move[0], move[1], move[2])

	def _updateState(self):
		self.net.requestTurn()
		mapLayer1 = self.net.requestMap(Options.LAYER_1)

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
