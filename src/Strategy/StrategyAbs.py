
#base class for strategies
class Strategy:

	def __init__(self, game):
		self.game  = game
		self.graph = game.adjacencyRel


	def getActions(self):
		pass
