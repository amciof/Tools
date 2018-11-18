
class Train:

	def __init__(self, jsonTrain):
		self.goods         = jsonTrain['goods']
		self.goodsCapacity = jsonTrain['goods_capacity']
		self.goodsType     = jsonTrain['goods_type']
		self.idx           = jsonTrain['idx']
		self.lineIdx       = jsonTrain['line_idx']
		self.playerIdx     = jsonTrain['player_idx']
		self.position      = jsonTrain['position']
		self.speed         = jsonTrain['speed']

class Player:

	def __init__(self, jsonLogin):
		self.home    = jsonLogin['home']['post_idx']
		self.idx     = jsonLogin['idx']
		self.inGame  = jsonLogin['in_game']
		self.name    = jsonLogin['name']
		self.rating  = jsonLogin['rating']
		#self.town
		self.trains  = [Train(obj) for obj in jsonLogin['trains']]