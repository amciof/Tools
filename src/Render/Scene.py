import sys
sys.path.append('../')

from PyQt5.QtGui  import QPainter, QColor, QPen, QFont, QBrush, QPolygonF, QTextOption
from PyQt5.QtCore import QPointF, QRectF, Qt

from Game.GameElements import BaseType, Base, Town, Market, Storage
from Game.GameElements import Road, Speed, Train

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

def initTextOption():
	option = QTextOption()
	option.setAlignment(Qt.AlignCenter)

	return option

def initTextFont():
	font = QFont('Helvetica')
	
	return font


#my little glm lib
def modelMat(xSize, ySize, pos):
	model = np.zeros((3, 3), np.float32)

	model[0][0] = xSize / 2.0
	model[1][1] = ySize / 2.0
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
		self.data   = data
		self.model  = model
		self.color  = color
		self.buffer = None


class Scene:
	#Resources
	RESOURCES = {
		BaseType.BASE      : initPolygon(6)
		, BaseType.TOWN    : initPolygon(4)
		, BaseType.MARKET  : initPolygon(3)
		, BaseType.STORAGE : initPolygon(5)
	}
	ZERO_POINT = np.float32([+0.0, +0.0, +1.0])

	#sizes
	BASE_SIZES = {
		  BaseType.BASE    : 30
		, BaseType.TOWN    : 50
		, BaseType.MARKET  : 30
		, BaseType.STORAGE : 30
	}
	TRAIN_SIZE = 13

	#colors
	BASE_COLORS = {
		  BaseType.BASE    : QColor(200, 255, 200)
		, BaseType.TOWN    : QColor(255,   0,   0)
		, BaseType.MARKET  : QColor(  0, 255,   0)
		, BaseType.STORAGE : QColor(  0,   0, 255)
	}
	ROAD_COLOR  = QColor(  0,   0,   0)
	TRAIN_COLOR = QColor(255,   0, 255)
	LABEL_COLOR = QColor(255, 255, 255)

	#special coefs
	DEFAULT_ZOOM = 0.9

	MAX_ZOOM = 8.0
	MIN_ZOOM = 0.5

	CAMERA_LIM_COEF = 0.1


	BASE_LABEL_SIZE = 40
	ROAD_LABEL_SIZE = 20

	TEXT_X_SCALE = 1.00
	TEXT_Y_SCALE = 0.40

	TEXT_REL = 0.70

	TEXT_OPTION = initTextOption()
	TEXT_FONT   = initTextFont()


	##init
	def __init__(self, bases, roads, trains, viewport):
		self.__initViewport(viewport)
		self.__initCameraComp()

		self.__initBasesInfo(bases, roads)

		self.__initRoadsInfo(roads)
		self.__initRoadsVectors(roads)

		self.__initTrainsInfo(trains)

		self.__initBasesLabelsInfo(bases)
		self.__initRoadsLabelsInfo(roads)


	def __initViewport(self, viewport):
		self.w = viewport[0]
		self.h = viewport[1]

	def __initCameraComp(self):
		self.zoom = Scene.DEFAULT_ZOOM
		self.proj = orthoMat(self.w / self.zoom, self.h / self.zoom)

		self.cam  = cameraMat(self.w / 2, self.h / 2)
		self.left  = -self.w * (Scene.CAMERA_LIM_COEF)
		self.right =  self.w * (Scene.CAMERA_LIM_COEF + 1.0)
		self.down  = -self.h * (Scene.CAMERA_LIM_COEF)
		self.up    =  self.h * (Scene.CAMERA_LIM_COEF + 1.0)


	def __initBasesInfo(self, bases, roads):
		MAGIC_CONST = 10

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

			model = modelMat(size, size, pos)
			color = Scene.BASE_COLORS[baseType]
			
			self.basesInfo[idx] = RenderInfo(data, model, color)

	def __initRoadsInfo(self, roads):
		self.roadsInfo = {}

		for idx, road in roads.items():

			idx1, idx2 = road.getAdjacentIdx()

			data  = np.int32([idx1, idx2, road.getLength()])
			model = None
			color = Scene.ROAD_COLOR

			self.roadsInfo[idx] = RenderInfo(data, model, color)

	def __initTrainsInfo(self, trains):
		self.trainsInfo = {}

		for idx, train in trains.items():
			data  = Scene.RESOURCES[BaseType.TOWN]
			model = modelMat(Scene.TRAIN_SIZE, Scene.TRAIN_SIZE, Scene.ZERO_POINT)
			color = Scene.TRAIN_COLOR

			self.trainsInfo[idx] = RenderInfo(data, model, color)

			self.updateTrain(train)


	def __initRoadsVectors(self, roads):
		self.roadsVecs = {}

		for idx, road in roads.items():
			base1, base2 = road.getAdjacentIdx()

			mod1 = self.basesInfo[base1].model
			mod2 = self.basesInfo[base2].model

			vec = np.float32([mod2[0][2] - mod1[0][2], mod2[1][2] - mod1[1][2], 0.0])
			vec /= road.length

			self.roadsVecs[idx] = vec


	def __initBasesLabelsInfo(self, bases):
		self.basesLabelsInfo = {}

		for idx, info in self.basesInfo.items():
			baseType = bases[idx].getType()

			size    = Scene.BASE_LABEL_SIZE
			pos     = np.array(info.model[:, 2])
			pos[1] -= size / 2

			data  = Scene.RESOURCES[BaseType.TOWN]
			model = modelMat(size * Scene.TEXT_X_SCALE, size * Scene.TEXT_Y_SCALE, pos)
			color = Scene.LABEL_COLOR

			self.basesLabelsInfo[idx] = RenderInfo(data, model, color)

	def __initRoadsLabelsInfo(self, roads):
		self.roadsLabelsInfo = {}

		for idx, vec in self.roadsVecs.items():
			length  = roads[idx].getLength()
			base, _ = roads[idx].getAdjacentIdx()

			if length % 2 == 0:
				coef = length / 2 - 0.25
			else:
				coef = length / 2

			pos  = np.array(self.basesInfo[base].model[:, 2])
			pos += coef * vec

			size  = Scene.ROAD_LABEL_SIZE
			data  = Scene.RESOURCES[BaseType.TOWN]
			model = modelMat(size, size, pos)
			color = Scene.LABEL_COLOR

			self.roadsLabelsInfo[idx] = RenderInfo(data, model, color)


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
	#TODO: much optimizations & rework here possible
	def renderScene(self, context):
		self.__drawRoads(context)
		self.__drawBases(context)
		
		self.__drawBaseLabels(context)
		self.__drawRoadLabels(context)

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

			buffered = self.__bufferPolygon(context, info.data, info.model)

			context.drawPolygon(buffered)

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

			buffered = self.__bufferPolygon(context, info.data, info.model)

			context.drawPolygon(buffered)

		context.setBrush(restore)

	def __drawBaseLabels(self, context):
		restore = context.brush()

		for idx, info in self.basesLabelsInfo.items():
			context.setBrush(QBrush(info.color))

			buffered = self.__bufferPolygon(context, info.data, info.model)
			context.drawPolygon(buffered)

			Scene.TEXT_FONT.setPointSize(
				int(Scene.TEXT_REL * (buffered[0].y() - buffered[2].y()))
			)

			context.setFont(Scene.TEXT_FONT)
			context.drawText(QRectF(buffered[2], buffered[0]), str(idx), Scene.TEXT_OPTION)

		context.setBrush(restore)

	def __drawRoadLabels(self, context):
		restore = context.brush()

		for idx, info in self.roadsLabelsInfo.items():
			context.setBrush(QBrush(info.color))

			buffered = self.__bufferPolygon(context, info.data, info.model)
			context.drawPolygon(buffered)

			Scene.TEXT_FONT.setPointSize(
				int(Scene.TEXT_REL * (buffered[0].y() - buffered[2].y()))
			)

			length = self.roadsInfo[idx].data[2]
			context.setFont(Scene.TEXT_FONT)
			context.drawText(QRectF(buffered[2], buffered[0]), str(length), Scene.TEXT_OPTION)

		context.setBrush(restore)

	#primitives draw
	def __bufferPolygon(self, context, data, model):
		buffer = QPolygonF()

		for point in data:
			point = self.__transform(model, point)
			buffer.append(QPointF(point[0], point[1]))

		return buffer

	def __drawLine(self, context, info):
		idx1, idx2, _ = info.data

		model1 = self.basesInfo[idx1].model
		model2 = self.basesInfo[idx2].model

		point1 = self.__transform(model1, Scene.ZERO_POINT)
		point2 = self.__transform(model2, Scene.ZERO_POINT)

		context.drawLine(
			 int(point1[0]), int(point1[1])
			,int(point2[0]), int(point2[1])
		)