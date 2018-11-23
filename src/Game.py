
from Networking import Network, Action, Options
from Scene         import Scene
from SceneElements import Speed
from Player     import Player

from PyQt5.QtGui  import QPainter

import numpy as np

class Game:
	
	EVENT_MOUSE_PRESS = 2
	EVENT_PAINT       = 12

	##init section
	def __init__(self, serverAddr, portNum, playerName, viewport):
		##network init
		self.net = Network(serverAddr, portNum)

		##basic requests
		playerResp = self.net.requestLogin(playerName)
		mapResp    = self.net.requestMap(Options.LAYER_0)

		##map
		self.scene = Scene(playerResp.msg, mapResp.msg, viewport)
		
		##player
		self.player = Player(playerResp.msg)

		##state params
		self.selectedTrain = None


	##events
	#update logic(main method)
	def update(self, event):
		if event.type() == Game.EVENT_MOUSE_PRESS:
			self.handleMousePress(event)

		elif event.type() == Game.EVENT_PAINT:
			self.render()


	#render
	def render(self):

		self.scene.renderScene()


	#mouse handlers
	def handleMouseMove(self):
		pass

	def handleMouseRelease(self):
		pass

	def handleMousePress(self, event):
		#should be reworked
		train = self.selectedTrain
		winCoords = np.int32([event.x(), event.y()])

		if not train is None:
			if train.position == 0 or train.position == train.road.length:
				#get road bases
				base1, base2 = train.road.getAdjacent()
				speed = Speed.FORWARD

				if train.position == train.road.length:
					#swap bases
					base2, base1 = base1, base2
					speed = Speed.BACKWARD
				
				base = self.scene.hitsAdjacent(base1.idx, winCoords)
				if not base is None:
					if base != base2.idx:
						#hits base on the other road
						newRoad = self.scene.getRoadByAdjRel(base1.idx, base)
						train.jumpToRoad(newRoad)

						base1, base2 = newRoad.getAdjacent()

						speed = Speed.FORWARD if base == base2.idx else Speed.BACKWARD

					self.scene.moveTrain(train.idx, speed)
			else:
				base1, base2 = train.road.getAdjacentIdx()

				if self.scene.hitsBase(base1, winCoords):
					self.scene.moveTrain(train.idx, Speed.BACKWARD)
				if self.scene.hitsBase(base2, winCoords):
					self.scene.moveTrain(train.idx, Speed.FORWARD)

			self.__resetTrain()

		else:
			for trainIdx in self.player.trains:
				if self.scene.hitsTrain(trainIdx, winCoords):
					self.__selectTrain(trainIdx)
					break

		self.scene.update()

	def __resetTrain(self):
		self.scene.setTrainColor(self.selectedTrain.idx, Scene.TRAIN_DEFAULT)
		self.selectedTrain = None

	def __selectTrain(self, idx):
		self.selectedTrain = self.scene.getTrain(idx)
		self.scene.setTrainColor(idx, Scene.TRAIN_SELECTED)


	#key handlers
	def handleKeyPress(self):
		pass

	def handleKeyRelease(self):
		pass
