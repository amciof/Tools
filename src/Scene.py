
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush

from SceneElements import Base, Town, Market, Storage
from SceneElements import Road, Speed, Train

import networkx as nx
import numpy    as np

import math
import json


class RenderInfo:

	def __init__(self, color, pos):
		self.pos   = pos
		self.color = color


class Scene:

	BASES_COLORS = {
		  Base.BASE    : QColor(255, 255, 255)
		, Base.TOWN    : QColor(255, 255, 255)
		, Base.MARKET  : QColor(255, 255, 255)
		, Base.STORAGE : QColor(255, 255, 255)
	}

	TRAIN_DEFAULT  = QColor(255, 255, 255)
	TRAIN_SELECTED = QColor(255,   0,   0)

	ROAD_COLOR    = QColor(  0,   0,   0)

	COMPRESSION = 0.85

	##init
	def __init__(self, jsonLogin, jsonMap, viewport):
		#viewport reference to window

		self.__initBases(jsonMap)
		self.__initRoads(jsonMap)
		self.__initAdjacencyRel(jsonMap)

		self.__initTrains(jsonLogin)

		self.__initViewport(viewport)

		self.__initBasesInfo(jsonMap)
		self.__initRoadsVectors()
		self.__initTrainsInfo()

		self.__initBasesWorldPos()
		self.__initTrainsWorldPos()

		self.__initBasesRenderBuffer()
		self.__initTrainsRenderBuffer()


	def __initBases(self, jsonMap):#jsonLogin
		#TODO: should init towns & markets & storages first
		self.bases = {}

		for jsonPoint in jsonMap['points']:
			idx = jsonPoint['idx']

			self.bases[idx] = Base(jsonPoint, Base.BASE)

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

	def __initViewport(self, viewport):

		self.viewport = viewport


	def __initBasesInfo(self, jsonMap):
		MAGIC_CONST = 5

		graph = nx.Graph()

		for base in self.bases.values():
			graph.add_node(base.idx)

		for road in self.roads.values():
			u, v = road.getAdjacentIdx()
			graph.add_edge(u, v)

		assigned = nx.spring_layout(graph, iterations = MAGIC_CONST * len(jsonMap['points']))

		self.basesInfo = {}
		for idx, pos in assigned.items():
			base = self.bases[idx]

			self.basesInfo[idx] = RenderInfo(Scene.BASES_COLORS[base.baseType], pos)

	def __initRoadsVectors(self):
		self.roadsVecs = {}

		for idx, road in self.roads.items():
			base1, base2 = road.getAdjacentIdx()

			pos1 = self.basesInfo[base1].pos
			pos2 = self.basesInfo[base2].pos

			vec = (pos2 - pos1) / road.length

			self.roadsVecs[idx] = vec

	def __initTrainsInfo(self):
		self.trainsInfo = {}

		for idx, train in self.trains.items():
			road     = train.road

			roadIdx  = road.idx
			base1, _ = road.getAdjacentIdx()

			trainPos = train.position

			roadVec = self.roadsVecs[roadIdx]
			basePos = self.basesInfo[base1].pos

			self.trainsInfo[idx] \
				= RenderInfo(Scene.TRAIN_DEFAULT, basePos + roadVec * trainPos)
			

	def __initBasesWorldPos(self):
		self.basesWorldPos = {}

		for idx, info in self.basesInfo.items():
			worldPos = np.int32([0, 0])

			self.__toViewport(info.pos, worldPos)

			self.basesWorldPos[idx] = worldPos

	def __initTrainsWorldPos(self):
		self.trainsWorldPos = {}
		
		for idx, info in self.trainsInfo.items():
			worldPos = np.int32([0, 0])

			self.__toViewport(info.pos, worldPos)

			self.trainsWorldPos[idx] = worldPos


	def __initBasesRenderBuffer(self):
		self.basesRenderBuffer = {}

		for idx in self.bases:
			self.basesRenderBuffer[idx] = np.int32([0, 0])

	def __initTrainsRenderBuffer(self):
		self.trainsRenderBuffer = {}

		for idx in self.trains:
			self.trainsRenderBuffer[idx] = np.int32([0, 0])


	##logic(fkng clicks)
	def hitsAdjacent(self, idxBase, winCoords):
		#can be O(log(V)), but no need: this will soon shrink))
		for idx in self.adjacencyRel[idxBase]:
			if self.hitsBase(idx, winCoords):
				return idx

		return None

	def hitsBase(self, idxBase, winCoords):
		pos = self.basesWorldPos[idxBase]
		
		#adjustWinCoords() -> in future(maybe)
		return abs(winCoords[0] - pos[0]) < Base.SIZE // 2 \
			and abs(winCoords[1] - pos[1]) < Base.SIZE // 2

	def hitsTrain(self, idxTrain, winCoords):
		pos = self.trainsWorldPos[idxTrain]
		
		#adjustWinCoords() -> in future(maybe)
		return abs(winCoords[0] - pos[0]) < Train.SIZE // 2 \
			and abs(winCoords[1] - pos[1]) < Train.SIZE // 2


	def moveTrain(self, idxTrain, speed):
		train = self.trains[idxTrain]

		train.move(speed)

		#update train pos
		road     = train.road
		trainPos = train.position

		base1, _  = road.getAdjacentIdx()

		roadVec = self.roadsVecs[road.idx]
		basePos = self.basesInfo[base1].pos

		trainModel = self.trainsInfo[idxTrain].pos
		trainModel[0] = basePos[0] + roadVec[0] * trainPos
		trainModel[1] = basePos[1] + roadVec[1] * trainPos

		trainWorld = self.trainsWorldPos[idxTrain]
		self.__toViewport(trainModel, trainWorld)

	
	def getBase(self, idx):
		
		return self.bases[idx]

	def getRoad(self, idx):
		
		return self.roads[idx]

	def getTrain(self, idx):
		
		return self.trains[idx]

	def getRoadByAdjRel(self, idx1, idx2):
		
		return self.adjacencyRel[idx1][idx2]


	def setTrainColor(self, idx, color):
		info = self.trainsInfo[idx]
		info.color = color

	def setBaseColor(self, idx, color):
		info = self.basesInfo[idx]
		info.color = color

	##
	def update(self):
		#very dirty
		self.viewport.update()

	##render
	def renderScene(self):
		self.__computeBasesPos()
		self.__computeTrainsPos()

		context = self.__getContext()

		self.__drawRoads(context)
		self.__drawBases(context)
		self.__drawTrains(context)

		self.__releaseContext(context)
	

	def __getContext(self):

		return QPainter(self.viewport)

	def __releaseContext(self, context):

		context.end()


	def __computeBasesPos(self):

		self.__computePos(self.basesInfo, self.basesRenderBuffer)
	
	def __computeTrainsPos(self):
		
		self.__computePos(self.trainsInfo ,self.trainsRenderBuffer)


	def __computePos(self, renderInfo, renderBuffer):
		for idx, buffer in renderBuffer.items():
			pos = renderInfo[idx].pos

			self.__toViewport(pos, buffer)

	def __orthoTransform(self, pos):

		pass

	def __toViewport(self, model, world):
		w = self.viewport.size().width()
		h = self.viewport.size().height()

		world[0] = np.int32((Scene.COMPRESSION * model[0] + 1.0) * w / 2)
		world[1] = np.int32((Scene.COMPRESSION * model[1] + 1.0) * h / 2)
	

	def __drawBases(self, context):
		restore = context.brush()

		for idx, pos in self.basesRenderBuffer.items():
			x, y  = pos
			color = self.basesInfo[idx].color

			context.setBrush(QBrush(color))
			context.drawEllipse(
				  x - Base.SIZE // 2
				, y - Base.SIZE // 2
				, Base.SIZE
				, Base.SIZE
			)

		context.setBrush(restore)

	def __drawRoads(self, context):
		restore = context.pen()

		context.setPen(Scene.ROAD_COLOR)
		for road in self.roads.values():
			first, second = road.getAdjacentIdx()

			x1, y1 = self.basesRenderBuffer[first]
			x2, y2 = self.basesRenderBuffer[second]

			context.drawLine(x1, y1, x2, y2)

		context.setPen(restore)

	def __drawTrains(self, context):
		restore = context.brush()

		for idx, pos in self.trainsRenderBuffer.items():
			x, y  = pos
			color = self.trainsInfo[idx].color

			context.setBrush(QBrush(color))
			context.drawRect(
				  x - Train.SIZE // 2
				, y - Train.SIZE // 2
				, Train.SIZE
				, Train.SIZE
			)

		context.setBrush(restore)