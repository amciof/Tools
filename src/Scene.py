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

#my little glm lib
def modelMat(size, pos):
	model = np.zeros((3, 3), np.float32)

	model[0][0] = size / 2.0
	model[1][1] = size / 2.0
	model[2][2] = 1.0
	model[0][2] = pos[0]
	model[1][2] = pos[1]

	return model

def orthoMat(w, h):
	ortho = np.zeros((3, 3), np.float32)

	ortho[0][0] = 2 / w
	ortho[1][1] = 2 / h
	ortho[2][2] = 1.0

	return ortho

def cameraMat(x, y):
	camera = np.zeros((3, 3), np.float32)

	camera[0][0] = 1.0
	camera[1][1] = 1.0
	camera[2][2] = 1.0

	camera[0][2] = -x
	camera[1][2] = -y

	return camera


class RenderInfo:

	def __init__(self, data, model, color):
		self.data  = data
		self.model = model
		self.color = color


class Scene:
	#Resources
	RESOURCES = {
		Base.BASE      : initPolygon(6)
		, Base.TOWN    : initPolygon(4)
		, Base.MARKET  : initPolygon(3)
		, Base.STORAGE : initPolygon(5)
	}
	ZERO_POINT = np.float32([0.0, 0.0, 1.0])

	#sizes
	BASE_SIZES = {
		  Base.BASE    : 40
		, Base.TOWN    : 80
		, Base.MARKET  : 60
		, Base.STORAGE : 60
	}
	TRAIN_SIZE = 25

	#colors
	BASE_COLORS = {
		  Base.BASE    : QColor(200, 255, 200)
		, Base.TOWN    : QColor(255,   0,   0)
		, Base.MARKET  : QColor(  0, 255,   0)
		, Base.STORAGE : QColor(  0,   0, 255)
	}
	ROAD_COLOR  = QColor(  0,   0,   0)
	TRAIN_COLOR = QColor(255,   0, 255)

	#special coefs
	DEFAULT_ZOOM = 0.9

	MAX_ZOOM = 8.0
	MIN_ZOOM = 0.5

	CAMERA_LIM_COEF = 0.1


	##init
	def __init__(self, bases, roads, trains, window):

		self.__initViewport(window)
		self.__initCameraComp()

		self.__initBasesInfo(bases, roads)

		self.__initRoadsInfo(roads)
		self.__initRoadsVectors(roads)

		self.__initTrainsInfo(trains)

	def __initViewport(self, window):
		self.w = window.size().width()
		self.h = window.size().height()

	def __initCameraComp(self):
		self.zoom = Scene.DEFAULT_ZOOM
		self.proj = orthoMat(self.w / self.zoom, self.h / self.zoom)

		self.cam  = cameraMat(self.w / 2, self.h / 2)
		self.left  = -self.w * (Scene.CAMERA_LIM_COEF)
		self.right =  self.w * (Scene.CAMERA_LIM_COEF + 1.0)
		self.down  = -self.h * (Scene.CAMERA_LIM_COEF)
		self.up    =  self.h * (Scene.CAMERA_LIM_COEF + 1.0)

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
			size     = Scene.BASE_SIZES[baseType]

			data  = Scene.RESOURCES[baseType]

			pos = self.__toViewport(pos)

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
			model = modelMat(Scene.TRAIN_SIZE, Scene.ZERO_POINT)
			color = Scene.TRAIN_COLOR

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
	def moveCam(self, dx, dy):
		x = -self.cam[0][2]
		y = -self.cam[1][2]

		x += dx
		y += dy
		x = min(max(self.left, x), self.right)
		y = min(max(self.down, y), self.up   )

		self.cam[0][2] = -x
		self.cam[1][2] = -y

	def zoomCam(self, delta):
		self.zoom = min(max(self.zoom + delta, Scene.MIN_ZOOM), Scene.MAX_ZOOM)

		self.proj[0][0] = 2 * self.zoom / self.w
		self.proj[1][1] = 2 * self.zoom / self.h

		
	def updateTrain(self, train):
		road = train.getRoad()
		coef = train.getPosition()

		idx1, idx2 = road.getAdjacentIdx()

		roadVec = self.roadsVecs[road.getIdx()]
		baseMod = self.basesInfo[idx1].model

		trainMod = self.trainsInfo[train.getIdx()].model

		trainMod[0][2] = baseMod[0][2] + coef * roadVec[0]
		trainMod[1][2] = baseMod[1][2] + coef * roadVec[1]


	##render
	def renderScene(self, context):
		self.__drawRoads(context)
		self.__drawBases(context)
		self.__drawTrains(context)
	
	#my little openGL
	def __transform(self, model, point):
		point = np.matmul(model    , point)
		point = np.matmul(self.cam , point)
		point = np.matmul(self.proj, point)

		point /= point[2]

		point = self.__toViewport(point)

		return point

	def __toViewport(self, point):
		temp = np.empty((3,), np.float32)
		temp[0] = (point[0] + 1.0) * self.w / 2
		temp[1] = (point[1] + 1.0) * self.h / 2

		return temp

	#draw logic
	def __drawBases(self, context):
		restore = context.brush()

		for idx, info in self.basesInfo.items():
			context.setBrush(QBrush(info.color))

			self.__drawPolygon(context, info.data, info.model)

			#context.drawText(info.model[0][2] - 8, info.model[1][2] - 15, str(idx))

		context.setBrush(restore)

	def __drawRoads(self, context):
		restore = context.pen()

		context.setPen(Scene.ROAD_COLOR)

		for idx, info in self.roadsInfo.items():
			self.__drawLine(context, info)

		context.setPen(restore)
	
	def __drawTrains(self, context):
		restore = context.brush()

		for idx, info in self.trainsInfo.items():
			context.setBrush(QBrush(info.color))

			self.__drawPolygon(context, info.data, info.model)

		context.setBrush(restore)

	def __drawLabels(self, context):

		pass

	#primitives draw
	def __drawPolygon(self, context, data, model):
		buffer = QPolygonF()

		for point in data:
			point = self.__transform(model, point)

			buffer.append(QPointF(point[0], point[1]))
			
		context.drawPolygon(buffer)

	def __drawLine(self, context, info):
		idx1, idx2 = info.data

		model1 = self.basesInfo[idx1].model
		model2 = self.basesInfo[idx2].model

		point1 = self.__transform(model1, Scene.ZERO_POINT)
		point2 = self.__transform(model2, Scene.ZERO_POINT)

		context.drawLine(
			 int(point1[0]), int(point1[1])
			,int(point2[0]), int(point2[1])
		)