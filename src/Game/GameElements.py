
#bases
class BaseType:
	BASE    = 0
	TOWN    = 1
	MARKET  = 2
	STORAGE = 3

#base Base class
class Base:

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

#Base subclasses
class Town(Base):

	def __init__(self, jsonTown):
		Base.__init__(self, jsonTown['name'], jsonTown['point_idx'], BaseType.TOWN)

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

	#logic
	def update(self, jsonUpdate):
		self.armor         = jsonUpdate['armor']
		self.armorCapacity = jsonUpdate['armor_capacity']

		self.product         = jsonUpdate['product']
		self.productCapacity = jsonUpdate['product_capacity']

		self.population         = jsonUpdate['population']
		self.populationCapacity = jsonUpdate['population_capacity']

		for event in jsonUpdate['events']:
			self.addEvent(event)


	def addEvent(self, event):

		pass

	def upgrade(self):

		pass

class Market(Base):

	def __init__(self, jsonMarket):
		Base.__init__(
			self
			, jsonMarket['name']
			, jsonMarket['point_idx']
			, BaseType.MARKET
		)

		self.product         = jsonMarket['product']          # +
		self.productCapacity = jsonMarket['product_capacity'] # +
		self.replenishment   = jsonMarket['replenishment']    # +


	def update(self, jsonUpdate):
		self.product         = jsonUpdate['product']
		self.productCapacity = jsonUpdate['product_capacity']

		for event in jsonUpdate['events']:
			self.addEvent(event)

	def addEvent(self, event):
		pass

class Storage(Base):

	def __init__(self, jsonStorage):
		Base.__init__(
			self
			, jsonStorage['name']
			, jsonStorage['point_idx']
			, BaseType.STORAGE
		)

		self.armor         = jsonStorage['armor']          # +
		self.armorCapacity = jsonStorage['armor_capacity'] # +
		self.replenishment = jsonStorage['replenishment']  # +


	def update(self, jsonUpdate):
		self.armor         = jsonUpdate['armor']          # +
		self.armorCapacity = jsonUpdate['armor_capacity'] # +

		for event in jsonUpdate['events']:
			self.addEvent(event)

	def addEvent(self, event):
		pass


#rock 'n' roll
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

		#self.fuelConsumption = jsonTrain['fuel_consumption'] # -
		#self.fuelCapacity    = jsonTrain['fuel_capacity']    # -
		#self.fuel            = jsonTrain['fuel']             # -

		self.level     = jsonTrain['level']            # +
		self.nextPrice = jsonTrain['next_level_price'] # +

		self.playerIdx = jsonTrain['player_idx'] # +
		self.idx       = jsonTrain['idx']        # +

		self.cooldown = jsonTrain['cooldown'] # -
		self.position = jsonTrain['position'] # +
		self.speed    = jsonTrain['speed']    # +

		self.road  = road  # +

	def getPlayerIdx(self):
		return self.playerIdx

	def getIdx(self):
		return self.idx

	def getSpeed(self):
		return self.speed

	def getRoad(self):
		return self.road

	def getPosition(self):
		return self.position

	def upgrade(self):
		pass

	def onCooldown(self):
		return self.cooldown == 0

	def full(self):
		return self.goods == self.goodsCapacity


	def update(self, jsonUpdate, additional):
		self.goods         = jsonUpdate['goods']
		self.goodsCapacity = jsonUpdate['goods_capacity']
		self.goodsType     = jsonUpdate['goods_type']
		self.position      = jsonUpdate['position']
		self.speed         = jsonUpdate['speed']

		self.level     = jsonUpdate['level']            # -
		self.nextPrice = jsonUpdate['next_level_price'] # -

		self.playerIdx = jsonUpdate['player_idx'] # +
		self.idx       = jsonUpdate['idx']        # +

		self.road  = additional['road']

	def printStats(self):
		print('Goods   : ', self.goods)
		print('Position: ', self.position)
		print('Speed   : ', self.speed)
		print('Road    : ', self.road.getIdx())
		print('Length  : ', self.road.getLength())
		print('UV      : ', self.road.getAdjacentIdx())
