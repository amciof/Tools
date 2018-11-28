
from Networking import Network, Action, Options
from Scene         import Scene
from SceneElements import Base, Town, Market, Storage, Road, Speed, Train
from Player     import Player

from PyQt5.QtGui  import QPainter

import numpy as np

import json

class Game:
	
	EVENT_MOUSE_PRESS = 2
	EVENT_PAINT       = 12

	##init section
	def __init__(self, serverAddr, portNum, playerName, window):
		##---main window
		self.window = window

		##---init network---
		#self.__initNetwork(serverAddr, portNum)

		##--init all entities---
		#playerResp = self.net.requestLogin(playerName)
		#mapResp0 = self.net.requestMap(Options.LAYER_0)
		#mapResp1 = self.net.requestMap(Options.LAYER_1)

		with open('Examples/Login.txt') as file:
			playerResp = json.load(file)
		with open('Examples/Map0.txt')  as file:
			mapResp0   = json.load(file)
		with open('Examples/Map1.txt')  as file:
			mapResp1   = json.load(file)

		#self.__initBases(mapResp0.msg, mapResp1.msg)
		self.__initBases(mapResp0, mapResp1)

		#self.__initRoads(mapResp0.msg)
		self.__initRoads(mapResp0)

		#self.__initAdjacencyRel(mapResp0.msg)
		self.__initAdjacencyRel(mapResp0)

		#self.__initTrains(playerResp.msg)
		self.__initTrains(playerResp)

		##---init scene---
		self.__initScene()
		
		##player
		#self.__initPlayer(playerResp.msg)
		self.player = Player(playerResp)
		self.__initPlayer(playerResp)

		##state params
		self.selectedTrain = None


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


	##events
	#update logic(main method)
	def update(self, event):
		if event.type() == Game.EVENT_MOUSE_PRESS:
			self.handleMousePress(event)

		elif event.type() == Game.EVENT_PAINT:
			self.render()


	#render
	def render(self):
		context = QPainter(self.window)

		self.scene.renderScene(context)

		context.end()


	#mouse handlers
	def handleMouseMove(self):
		pass

	def handleMouseRelease(self):
		pass


	def handleMousePress(self, event):
		#should be reworked
		#train = self.selectedTrain
		#winCoords = np.int32([event.x(), event.y()])

		#if not train is None:
		#	if train.position == 0 or train.position == train.road.length:
				
		#		if train.position == train.road.length:
		#			pass
				
		#		if not base is None:
		#			if base != base2.idx:
		#				if base == base2.idx:
		#					pass
		#				else:
		#					pass
		#	else:
		#		if self.scene.hitsBase(base1, winCoords):
		#			pass
		#		if self.scene.hitsBase(base2, winCoords):
		#			pass

		#	self.__resetTrain()

		#else:
		#	for trainIdx in self.player.trains:
		#		if self.scene.hitsTrain(trainIdx, winCoords):
		#			self.__selectTrain(trainIdx)
		#			break

		train = self.selectedTrain
		winCoords = np.int32([event.x(), event.y()])

		if not train is None:
			pos    = train.getPosition()
			road   = train.getRoad()
			length = road.getLength()

			idx1, idx2 = road.getAdjacentIdx()

			if pos == 0 or pos == length:
				check = idx1 if pos == 0 else idx2

				for idx, road in self.adjacencyRel[check].items():
					if self.scene.hitsBase(idx, winCoords):
						self.__moveTrain(False, road, idx)
						break
			else:
				if self.scene.hitsBase(idx1, winCoords):
					dir = idx1
				elif self.scene.hitsBase(idx2, winCoords):
					dir = idx2	
				self.__moveTrain(True, None, dir)

			self.scene.updateTrain(train)
			self.__resetTrain()
			self.__removeOffered()
		else:
			for idx in self.player.getAllIdx():
				if self.scene.hitsTrain(idx, winCoords):
					self.__selectTrain(idx)
					self.__offerChoice()
					break

		self.window.update()

	def __moveTrain(self, same, road, base):
		if not same:
			self.selectedTrain.setRoad(road)

		self.selectedTrain.setDir(base)
		self.selectedTrain.move()

	def __resetTrain(self):
		self.scene.setTrainColor(self.selectedTrain.idx, Scene.TRAIN_DEFAULT)
		self.selectedTrain = None

	def __selectTrain(self, idx):
		self.selectedTrain = self.trains[idx]
		self.scene.setTrainColor(idx, Scene.TRAIN_SELECTED)

	def __offerChoice(self):
		pass

	def __removeOffered(self):
		pass


	#key handlers
	def handleKeyPress(self):
		pass

	def handleKeyRelease(self):
		pass
