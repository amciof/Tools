
from PyQt5.QtGui  import QPainter, QColor, QPen, QBrush, QPolygonF
from PyQt5.QtCore import QPointF

from SceneElements import Base, Town, Market, Storage
from SceneElements import Road, Speed, Train

import networkx as nx
import numpy    as np

import math
import json


#I dont know where to put this
def initPolygon(sides):
	if sides < 3:
		return None

	delta = 2 * math.pi / sides
	phase = (math.pi - delta) / 2
	res   = np.zeros((sides, 3), np.float32)
	for i in range(sides):
		res[i][0] = math.cos(delta * i + phase)
		res[i][1] = math.sin(delta * i + phase)
		res[i][2] = 1.0

	return res

#and this
def modelMat(size, pos):
	model = np.zeros((3, 3), np.float32)

	model[0][0] = size / 2.0
	model[1][1] = size / 2.0
	model[2][2] = 1.0
	model[0][2] = pos[0]
	model[1][2] = pos[1]

	return model

def orthoMat():

	pass

def cameraMat():

	pass


class RenderInfo:

	def __init__(self, data, model, color):
		self.data  = data
		self.model = model
		self.color = color


class Scene:

	RESOURCES = {
		Base.BASE      : initPolygon(6)
		, Base.TOWN    : initPolygon(4)
		, Base.MARKET  : initPolygon(3)
		, Base.STORAGE : initPolygon(5)
	}

	#BASE_SIZES = {
	#	  Base.BASE    : 40
	#	, Base.TOWN    : 80
	#	, Base.MARKET  : 60
	#	, Base.STORAGE : 60
	#}

	BASE_SIZE = 60

	BASE_COLORS = {
		  Base.BASE    : QColor(200, 255, 200)
		, Base.TOWN    : QColor(255,   0,   0)
		, Base.MARKET  : QColor(  0, 255,   0)
		, Base.STORAGE : QColor(  0,   0, 255)
	}

	ROAD_COLOR = QColor(  0,   0,   0)

	TRAIN_SIZE = 25

	TRAIN_DEFAULT  = QColor(255, 255, 255)
	TRAIN_SELECTED = QColor(250, 125, 250)

	MARGIN = 0.05


	##init
	def __init__(self, bases, roads, trains, window):

		self.__initViewport(window)

		self.__initBasesInfo(bases, roads)

		self.__initRoadsInfo(roads)
		self.__initRoadsVectors(roads)

		self.__initTrainsInfo(trains)

	#can be public
	def __initViewport(self, window):

		self.w = window.size().width()
		self.h = window.size().height()


	def __initBasesInfo(self, bases, roads):
		MAGIC_CONST = 3

		graph = nx.Graph()

		for idx in bases:
			graph.add_node(idx)

		for road in roads.values():
			u, v = road.getAdjacentIdx()
			graph.add_edge(u, v)

		assigned = nx.spring_layout(graph, iterations = MAGIC_CONST * len(bases))

		self.basesInfo = {}
		for idx, pos in assigned.items():
			base     = bases[idx]
			baseType = base.getType()
			size     = Scene.BASE_SIZE#Scene.BASE_SIZES[baseType]

			data  = Scene.RESOURCES[baseType]

			pos[0] = (pos[0] + 1.0) * ((1 - 2 * Scene.MARGIN) * self.w / 2) + self.w * Scene.MARGIN
			pos[1] = (pos[1] + 1.0) * ((1 - 2 * Scene.MARGIN) * self.h / 2) + self.h * Scene.MARGIN

			model = modelMat(size, pos)
			color = Scene.BASE_COLORS[baseType]
			
			self.basesInfo[idx] = RenderInfo(data, model, color)

	def __initRoadsInfo(self, roads):
		self.roadsInfo = {}

		for idx, road in roads.items():

			idx1, idx2 = road.getAdjacentIdx()

			data  = np.int32([idx1, idx2])
			model = None
			color = Scene.ROAD_COLOR

			self.roadsInfo[idx] = RenderInfo(data, model, color)

	def __initTrainsInfo(self, trains):
		self.trainsInfo = {}

		for idx, train in trains.items():
			data  = Scene.RESOURCES[Base.TOWN]
			model = modelMat(Scene.TRAIN_SIZE, np.float32([0, 0]))
			color = Scene.TRAIN_DEFAULT

			self.trainsInfo[idx] = RenderInfo(data, model, color)

			self.updateTrain(train)
	
	def __initLabelsInfo(self):

		pass

			
	def __initRoadsVectors(self, roads):
		self.roadsVecs = {}

		for idx, road in roads.items():
			base1, base2 = road.getAdjacentIdx()

			mod1 = self.basesInfo[base1].model
			mod2 = self.basesInfo[base2].model

			vec = np.float32([mod2[0][2] - mod1[0][2], mod2[1][2] - mod1[1][2]])
			vec /= road.length

			self.roadsVecs[idx] = vec


	##logic
	def hitsBase(self, idxBase, winCoords):
		model = self.basesInfo[idxBase].model
		
		#adjustWinCoords() -> in future(maybe)
		return abs(winCoords[0] - model[0][2]) < Scene.BASE_SIZE // 2 \
			and abs(winCoords[1] - model[1][2]) < Scene.BASE_SIZE // 2
	
	def hitsTrain(self, idxTrain, winCoords):
		model = self.trainsInfo[idxTrain].model
		
		#adjustWinCoords() -> in future(maybe)
		return abs(winCoords[0] - model[0][2]) < Scene.TRAIN_SIZE // 2 \
			and abs(winCoords[1] - model[1][2]) < Scene.TRAIN_SIZE // 2

	
	def updateTrain(self, train):
		road = train.getRoad()
		coef = train.getPosition()

		idx1, idx2 = road.getAdjacentIdx()

		roadVec = self.roadsVecs[road.getIdx()]
		baseMod = self.basesInfo[idx1].model

		trainMod = self.trainsInfo[train.getIdx()].model

		trainMod[0][2] = baseMod[0][2] + coef * roadVec[0]
		trainMod[1][2] = baseMod[1][2] + coef * roadVec[1]


	def setTrainColor(self, idx, color):
		info = self.trainsInfo[idx]
		info.color = color

	def setBaseColor(self, idx, color):
		info = self.basesInfo[idx]
		info.color = color


	##render
	def renderScene(self, context):
		self.__drawRoads(context)
		self.__drawBases(context)
		self.__drawTrains(context)
	
	def __drawBases(self, context):
		restore = context.brush()

		for idx, info in self.basesInfo.items():
			context.setBrush(QBrush(info.color))

			self.__drawPolygon(context, info.data, info.model)

		context.setBrush(restore)

	def __drawRoads(self, context):
		restore = context.pen()

		context.setPen(Scene.ROAD_COLOR)

		for idx, info in self.roadsInfo.items():
			idx1, idx2 = info.data

			mod1 = self.basesInfo[idx1].model
			mod2 = self.basesInfo[idx2].model

			context.drawLine(
				mod1[0][2], mod1[1][2]
				, mod2[0][2], mod2[1][2]
			)

		context.setPen(restore)
	
	def __drawTrains(self, context):
		restore = context.brush()

		for idx, info in self.trainsInfo.items():
			context.setBrush(QBrush(info.color))

			self.__drawPolygon(context, info.data, info.model)

		context.setBrush(restore)

	def __drawLabels(self, context):

		pass


	def __drawPolygon(self, context, data, model):
		buffer = QPolygonF()

		for point in data:
			point = np.matmul(model, point)

			buffer.append(QPointF(point[0], point[1]))
			
		context.drawPolygon(buffer)