from PyQt5.QtGui  import QPainter, QColor, QPen, QBrush, QPolygonF
from PyQt5.QtCore import QPointF


class Base:

	BASE    = 0
	TOWN    = 1
	MARKET  = 2
	STORAGE = 3

	def __init__(self, name, idx, baseType):
		self.events = []

		self.baseType = baseType
		self.baseIdx  = idx
		self.name     = name

	def getType(self):

		return self.baseType

	def getBaseIdx(self):

		return self.baseIdx


	#logic
	def update(self):

		pass

	def addEvent(self):

		pass


class Town(Base):

	def __init__(self, jsonTown):
		Base.__init__(self, jsonTown['name'], jsonTown['point_idx'], Base.TOWN)

		self.idx = jsonTown['idx'] # +

		self.armorCapacity = jsonTown['armor_capacity'] # -
		self.armor         = jsonTown['armor']          # -

		self.productCapacity = jsonTown['product_capacity'] # +
		self.product         = jsonTown['product']          # +

		self.populationCapacity = jsonTown['population_capacity'] # +
		self.population         = jsonTown['population']          # +

		# self.nextPrice     = jsonTown['next_level_price'] # -
		# self.trainCooldown = jsonTown['train_cooldown']   # -
		# self.level         = jsonTown['level']            # -

		self.playerIdx = jsonTown['player_idx'] # -


	# useless get/set
	def getPlayerIdx(self):

		return self.playerIdx

	def getIdx(self):

		return self.idx

	def getArmor(self):

		return self.armor

	def getProduct(self, getProduct):

		return self.product


	# logic
	def update(self, jsonUpdate):

		self.product            = jsonUpdate['product']
		self.productCapacity    =  jsonUpdate['product_capacity']
		self.population         = jsonUpdate['population']
		self.populationCapacity = jsonUpdate['population_capacity']

	def addEvent(self, event):

		pass

	def upgrade(self):

		pass

	def withdrawArmor(self, amount):
		# for train upgrades
		if self.armor >= amount:
			self.armor -= amount
			return True

		return False


class Market(Base):

	def __init__(self, jsonMarket):
		Base.__init__(
			self
			, jsonMarket['name']
			, jsonMarket['point_idx']
			, Base.MARKET
		)

		self.product         = jsonMarket['product']          # +
		self.productCapacity = jsonMarket['product_capacity'] # +
		self.replenishment   = jsonMarket['replenishment']    # +

	
	#logic

	def update(self, jsonUpdate):
		self.product         = jsonUpdate['product']
		self.productCapacity = jsonUpdate['product_capacity']

	#????
	def withdrawProduct(self, amount):
		if self.product >= amount:
			self.product -= amount
			return True

		return False


class Storage(Base):

	def __init__(self, jsonStorage):
		Base.__init__(
			self
			, jsonStorage['name']
			, jsonStorage['point_idx']
			, Base.STORAGE
		)

		self.armor         = jsonStorage['armor']          # +
		self.armorCapacity = jsonStorage['armor_capacity'] # +
		self.replenishment = jsonStorage['replenishment']  # +


	#logic
	def update(self):
		self.armor = min(
			self.armor + self.replenishment
			, self.armorCapacity
		)

	#????
	def withdrawArmor(self, amount):
		if self.armor >= amount:
			self.armor -= amount
			return True

		return False


class Road:

	def __init__(self, jsonLine, base1, base2):
		self.idx    = jsonLine['idx']
		self.length = jsonLine['length']
		self.base1  = base1
		self.base2  = base2

	def getAdjacent(self):
		return self.base1, self.base2

	def getAdjacentIdx(self):
		return self.base1.getBaseIdx(), self.base2.getBaseIdx()

	def getLength(self):
		return self.length

	def getIdx(self):
		return self.idx


class Speed:
	STOP     = +0
	FORWARD  = +1
	BACKWARD = -1


class Train:

	def __init__(self, jsonTrain, road):
		self.goodsCapacity = jsonTrain['goods_capacity'] # -
		self.goodsType     = jsonTrain['goods_type']     # -
		self.goods         = jsonTrain['goods']          # -

		# self.fuelConsumption = jsonTrain['fuel_consumption'] # -
		# self.fuelCapacity    = jsonTrain['fuel_capacity']    # -
		# self.fuel            = jsonTrain['fuel']             # -

		# self.level     = jsonTrain['level']            # -
		# self.nextPrice = jsonTrain['next_level_price'] # -

		self.playerIdx = jsonTrain['player_idx'] # +
		self.idx       = jsonTrain['idx']        # +

		# self.cooldown = jsonTrain['cooldown'] # -
		self.position = jsonTrain['position'] # +
		self.speed    = jsonTrain['speed']    # +

		self.road  = road  # +
		self.moved = False # +

	def getPlayerIdx(self):
		return self.playerIdx

	def getIdx(self):
		return self.idx

	def setSpeed(self, speed):
		self.speed = speed

	def getSpeed(self):
		return self.speed

	def setRoad(self, newRoad):
		old = self.road
		pos = self.position

		if pos == 0 or pos == old.getLength():
			idx1, idx2 = old.getAdjacentIdx()

			curr = idx1 if pos == 0 else idx2

			idx1, idx2 = newRoad.getAdjacentIdx()
			if curr == idx1:
				self.position = 0
				self.road     = newRoad
			elif curr == idx2:
				self.position = newRoad.getLength()
				self.road     = newRoad

			self.speed = 0

	def getRoad(self):
		return self.road

	def getPosition(self):
		return self.position

	def isMoved(self):
		return self.moved

	def reset(self):
		self.moved = False

	def move(self):
		if self.moved:
			return

		length = self.road.length
		pos    = self.position
		speed  = self.speed
	
		newPos = pos + speed
		if newPos > length:
			self.position = length
		elif newPos < 0:
			self.position = 0
		else:
			self.position = newPos
			self.moved    = True

	def upgrade(self):
		pass

	def onCooldown(self):
		return self.cooldown == 0

	def update(self, jsonUpdate, additional):
		self.goods         = jsonUpdate['goods']
		self.goodsCapacity = jsonUpdate['goods_capacity']
		self.goodsType     = jsonUpdate['goods_type']
		self.position      = jsonUpdate['position']
		self.speed         = jsonUpdate['speed']

		self.road  = additional['road']
		self.moved = False

	def printStats(self):
		print('Goods   : ', self.goods)
		print('Position: ', self.position)
		print('Speed   : ', self.speed)
		print('Moved   : ', self.moved)
		print('Road    : ', self.road.getIdx())
		print('Length  : ', self.road.getLength())
		print('UV      : ', self.road.getAdjacentIdx())
