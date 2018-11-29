
from Networking import Network, Action, Options
from Scene         import Scene
from SceneElements import Base, Town, Market, Storage, Road, Speed, Train
from Player     import Player

from PyQt5.QtGui  import QPainter
from PyQt5.QtCore import QTimer

import numpy as np

import json

class Game:
	
	EVENT_TIMER       = 1
	EVENT_MOUSE_PRESS = 2
	EVENT_PAINT       = 12

	BUTTON_LEFT  = 1
	BUTTON_RIGHT = 2

	GAME_SLICE = 1000


	##init section
	def __init__(self, serverAddr, portNum, playerName, window):
		self.__initParent(window)

		self.__initNetwork(serverAddr, portNum)

		playerResp = self.net.requestLogin(playerName)
		mapResp0   = self.net.requestMap(Options.LAYER_0)
		mapResp1   = self.net.requestMap(Options.LAYER_1)

		#with open('Examples/Login.txt') as file:
		#	playerResp = json.load(file)
		#with open('Examples/Map0.txt')  as file:
		#	mapResp0   = json.load(file)
		#with open('Examples/Map1.txt')  as file:
		#	mapResp1   = json.load(file)

		self.__initBases(mapResp0.msg, mapResp1.msg)
		#self.__initBases(mapResp0, mapResp1)

		self.__initRoads(mapResp0.msg)
		#self.__initRoads(mapResp0)

		self.__initAdjacencyRel(mapResp0.msg)
		#self.__initAdjacencyRel(mapResp0)

		self.__initTrains(playerResp.msg)
		#self.__initTrains(playerResp)

		##---init scene---
		self.__initScene()
		
		##player
		self.__initPlayer(playerResp.msg)
		#self.__initPlayer(playerResp)

		##state params
		self.selectedTrain = None

	def __initParent(self, window):

		self.window = window

	def __initNetwork(self, serverAddr, portNum):

		self.net = Network(serverAddr, portNum)

	def __initBases(self, jsonMap0, jsonMap1):
		self.bases = {}

		for base in jsonMap1['posts']:
			#can be a fact here
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


	##logic
	def start(self):

		self.__startGameSlice()

	#update
	def update(self, event):
		if event.type() == Game.EVENT_MOUSE_PRESS:
			self.handleMousePress(event)

		elif event.type() == Game.EVENT_PAINT:
			self.render()

		elif event.type() == Game.EVENT_TIMER:
			self.handleTimerEvent(event)


	#render
	def render(self):
		context = QPainter(self.window)

		self.scene.renderScene(context)

		context.end()


	#handlers
	def handleMouseMove(self):

		pass

	def handleMouseRelease(self):

		pass


	def handleMousePress(self, event):
		if event.button() == Game.BUTTON_RIGHT:
			print('Turn command from player')
			self.__turn()
			return

		winCoords = np.int32([event.x(), event.y()])

		if not self.selectedTrain is None:
			self.__moveTrain(winCoords)
		else:
			self.__selectTrain(winCoords)

		self.window.update()

	def __selectTrain(self, winCoords):
		print('Train not selected')

		for idx in self.player.getAllIdx():
			moved = self.trains[idx].isMoved() 
			if not moved and self.scene.hitsTrain(idx, winCoords):
				self.selectedTrain = self.trains[idx]
				self.scene.setTrainColor(idx, Scene.TRAIN_SELECTED)

				train = self.selectedTrain
				train.setSpeed(Speed.STOP)
				resp  = self.net.requestMove(train.road.getIdx(), train.getSpeed(), train.getIdx())
				print('Result:', resp.result)
				print('Msg   :', resp.msg)
				train.printStats()

				self.__offerChoice()
				break		

	def __moveTrain(self, winCoords):
		train = self.selectedTrain

		print('Selected train: ', train.getIdx())

		pos    = train.getPosition()
		road   = train.getRoad()
		length = road.getLength()

		idx1, idx2 = road.getAdjacentIdx()

		if pos == 0 or pos == length:
			print('Train in base')

			check = idx1 if pos == 0 else idx2

			for idx, road in self.adjacencyRel[check].items():
				print('Hit test ', idx)
				if self.scene.hitsBase(idx, winCoords):
					print('Success')
					idx1, idx2 = road.getAdjacentIdx()

					speed = Speed.FORWARD if check == idx1 else Speed.BACKWARD

					print('=Before')
					train.printStats()

					train.setRoad(road)
					train.setSpeed(speed)
					train.move()

					print('=After')
					train.printStats()

					resp = self.net.requestMove(road.getIdx(), speed, train.getIdx())
					print('Result:', resp.result)
					print('Msg   :', resp.msg)
					break
		else:
			print('Train in way')

			hit1 = self.scene.hitsBase(idx1, winCoords)
			hit2 = self.scene.hitsBase(idx2, winCoords)
			if hit1 or hit2:
				speed = Speed.BACKWARD if hit1 else Speed.FORWARD

				print('=Before')
				train.printStats()

				train.setSpeed(speed)
				train.move()
			
				print('=After')
				train.printStats()

				road = train.getRoad()
				resp = self.net.requestMove(road.getIdx(), speed, train.getIdx())
				print('Result:', resp.result)
				print('Msg   :', resp.msg)
			
		self.scene.updateTrain(train)
		self.__resetTrain()
		self.__removeOffered()

	def __resetTrain(self):
		self.scene.setTrainColor(self.selectedTrain.idx, Scene.TRAIN_DEFAULT)
		self.selectedTrain = None


	def __offerChoice(self):

		pass

	def __removeOffered(self):

		pass


	#key handlers
	def handleKeyPress(self):

		pass

	def handleKeyRelease(self):

		pass


	#timers
	def handleTimerEvent(self, event):
		print('-----Timeout-----')
		self.__turn()

	def __startGameSlice(self):

		self.turnTimerID = self.window.startTimer(Game.GAME_SLICE)

	def __resetGameSlice(self):

		self.window.killTimer(self.turnTimerID)
		self.__startGameSlice()


	def __turn(self):
		print('turn')

		self.net.requestTurn()
		mapLayer1 = self.net.requestMap(Options.LAYER_1)

		self.__updateBases(mapLayer1)
		self.__updateTrains(mapLayer1)

		self.__resetGameSlice()
		print('end turn')

		self.window.update()

	def __updateBases(self, mapLayer1):
		for jsonBase in mapLayer1.msg['posts']:
			idx = jsonBase['point_idx']

			self.bases[idx].update(jsonBase)
	
	def __updateTrains(self, mapLayer1):
		for jsonTrain in mapLayer1.msg['trains']:
			roadIdx = jsonTrain['line_idx']
			road    = self.roads[roadIdx]

			idx = jsonTrain['idx']

			train = self.trains[idx]

			print('---Before---')
			train.printStats()
			train.update(jsonTrain, {'road' : road})
			print('---After---')
			train.printStats()

			self.scene.updateTrain(train)

			