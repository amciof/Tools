
from PyQt5.QtGui  import QPainter, QColor, QPen, QBrush, QPolygonF
from PyQt5.QtCore import QPointF

#Supply
class Supply:

	NO_SUPPLY = 0
	ARMOR     = 1
	PRODUCT   = 2

	def __init__(self, type, amount):
		self.type   = type
		self.amount = amount

#bases
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


	#useless get/set
	def getType(self):

		return self.baseType

	def getBaseIdx(self):

		return self.baseIdx


	#logic
	def update(self):

		pass

	def addEvent(self):

		pass

	#?????
	#def storeSupply(self):
	#	pass

	#def withdrawSupply(self):
	#	pass


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

		#self.nextPrice     = jsonTown['next_level_price'] # -
		#self.trainCooldown = jsonTown['train_cooldown']   # -
		#self.level         = jsonTown['level']            # -

		self.playerIdx = jsonTown['player_idx'] # -


	#useless get/set
	def getPlayerIdx(self):

		return self.playerIdx

	def getIdx(self):

		return self.idx

	def getArmor(self):

		return self.armor

	def getProduct(self, getProduct):

		return self.product


	#logic
	def update(self):
		#for event in self.events:
		#	event.apply()

		product = self.product - self.population
		product = 0 if product < 0 else product

		self.product = product

	def addEvent(self, event):

		pass


	def upgrade(self):

		pass

	#?????
	def storeSupply(self, amount, supplyType):
		if supplyType == Supply.ARMOR:
			available = self.armorCapacity - self.armor

			if amount <= available:
				self.armor += amount
				return True, 0
			else:
				self.armor += available
				return True, amount - available

		elif supplyType == Supply.PRODUCT:
			available = self.productCapacity - self.product

			if amount <= available:
				self.product += amount
				return True, 0
			else:
				self.product += available
				return True, amount - available

		return False, amount

	def withdrawArmor(self, amount):
		#for train upgrades
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
	def update(self):
		self.product = min(
			self.product + self.replenishment
			, self.productCapacity
		)

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



#road
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


#i like trains
class Speed:
	STOP     = 0
	FORWARD  = +1
	BACKWARD = -1

class Train:

	def __init__(self, jsonTrain, road):
		self.goodsCapacity = jsonTrain['goods_capacity'] # -
		self.goodsType     = jsonTrain['goods_type']     # -
		self.goods         = jsonTrain['goods']          # -

		#self.fuelConsumption = jsonTrain['fuel_consumption'] # -
		#self.fuelCapacity    = jsonTrain['fuel_capacity']    # -
		#self.fuel            = jsonTrain['fuel']             # -

		#self.level     = jsonTrain['level']            # -
		#self.nextPrice = jsonTrain['next_level_price'] # -

		self.playerIdx = jsonTrain['player_idx'] # +
		self.idx       = jsonTrain['idx']        # +

		#self.cooldown = jsonTrain['cooldown'] # -
		self.position = jsonTrain['position'] # +
		self.speed    = jsonTrain['speed']    # +

		self.road  = road  # +
		self.moved = False # +

	
	#useless shit
	def getPlayerIdx(self):

		return self.playerIdx


	def getIdx(self):

		return self.idx


	def setSpeed(self, speed):

		self.speed = speed

	def getSpeed(self):

		return self.speed

	
	def setRoad(self, newRoad):
		##hmmm this looks sucpicious
		old = self.road
		pos = self.position

		if pos == 0 or pos == old.getLength():
			base1, base2 = old.getAdjacent()

			curr = base1 if pos == 0 else base2

			base1, base2 = newRoad.getAdjacent()
			if curr.getBaseIdx() == base1.getBaseIdx():
			   self.position = 0
			   self.road = newRoad
			elif curr.getBaseIdx() == base2.getBaseIdx():
				self.position = newRoad.getLength()
				self.road = newRoad

			self.speed = 0

	def getRoad(self):

		return self.road


	def getPosition(self):

		return self.position


	#logic
	def move(self):
		length = self.road.length
		pos    = self.position
		speed  = self.speed
	
		newPos = pos + speed
		if newPos > length:
			self.speed    = 0
			self.position = length
		elif newPos < 0:
			self.speed    = 0
			self.position = 0
		else:
			self.position = newPos

	def setDir(self, baseIdx):
		idx1, idx2 = self.road.getAdjacentIdx()

		if baseIdx == idx1:
			self.speed = Speed.BACKWARD
		elif baseIdx == idx2:
			self.speed = Speed.FORWARD


	def upgrade(self):

		pass


	def onCooldown(self):

		return self.cooldown == 0


	def withdrawSupply(self):
		supply   = self.goods
		supType = self.goodsType
		
		self.goods     = 0
		self.goodsType = None

		return supply, supType

	def storeSupply(self, amount, supplyType):
		if self.goodsType == supplyType:
			available = self.goodsCapacity - self.goods

			if amount <= available:
				self.goods += amount
				return True, 0
			else:
				self.goods += available
				return True, amount - available

		return False, amount
