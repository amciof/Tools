
class Base:

	BASE    = 0
	TOWN    = 1
	MARKET  = 2
	STORAGE = 3

	SIZE = 40

	def __init__(self, jsonPoint, baseType):

		#----Base info----
		#events
		#name
		self.idx     = jsonPoint['idx']
		self.postIdx = jsonPoint['post_idx']
		self.name    = None

		self.baseType = baseType

class Town(Base):

	def __init__(self, jsonTown, jsonPoint):

		#armor
		#armor_capacity
		#level
		#next_level_price
		#player_idx          ???
		#population
		#population_capacity
		#product
		#product_capacity
		#train_cooldown      ???

		pass

class Market(Base):

	def __init__(self, jsonMarket, jsonPoint):

		#product
		#product_capacity
		#replenishment

		pass

class Storage(Base):

	def __init__(self):

		#armor
		#armor_capacity
		#replenishment

		pass



#roads
class Road:

	def __init__(self, jsonLine, base1, base2):
		self.idx    = jsonLine['idx']
		self.length = jsonLine['length']
		self.base1  = base1
		self.base2  = base2

	def getAdjacent(self):
		return self.base1, self.base2

	def getAdjacentIdx(self):
		return self.base1.idx, self.base2.idx


#CJ JUST FOLLOW DAT DAMN TRAIN
class Speed:

	STOP     = 0
	FORWARD  = +1
	BACKWARD = -1

class Train:
	
	SIZE = 20

	def __init__(self, jsonTrain, road):
		self.goods         = jsonTrain['goods']
		self.goodsCapacity = jsonTrain['goods_capacity']
		self.goodsType     = jsonTrain['goods_type']
		self.idx           = jsonTrain['idx']
		self.playerIdx     = jsonTrain['player_idx']
		self.position      = jsonTrain['position']
		self.speed         = jsonTrain['speed']

		self.road  = road

	def move(self, speed):
		#hmmm this looks sucpicious
		length = self.road.length
		pos    = self.position

		self.position = max(min(pos + speed, length), 0)

	def jumpToRoad(self, newRoad):
		#hmmm this looks sucpicious
		oldRoad = self.road
		pos     = self.position
		
		base1, base2 = oldRoad.getAdjacent()

		if pos == 0 or pos == oldRoad.length:
			currBase = base1 if pos == 0 else base2

			base1, base2 = newRoad.getAdjacent()

			pos = 0 if currBase.idx == base1.idx else newRoad.length

			self.road = newRoad