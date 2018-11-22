
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
