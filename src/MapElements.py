
class Base:

	TOWN    = 1
	MARKET  = 2
	STORAGE = 3

	def __init__(self, idx, pointIdx, pos, color):

		#----Base info----
		#events
		#name
		self.idx      = idx
		self.pointIdx = pointIdx

		#----Graphical info----
		self.pos   = pos
		self.color = color


class Town(Base):

	def __init__(self):

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

	pass


class Market(Base):

	def __init__(self):

		#product
		#product_capacity
		#replenishment

		pass

	pass


class Storage(Base):

	def __init__(self):

		#armor
		#armor_capacity
		#replenishment

		pass

	pass



#roads

#class RoadBase:
#	pass

#class Road(RoadBase):
class Road:

	def __init__(self, idx, length):

		self.idx    = idx
		self.length = length