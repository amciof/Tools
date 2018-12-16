from Strategy.StrategyAbs import Strategy
from Strategy.PathWalker import Path\
	, PathWalker\
	, WalkingPath\
	, WalkingRoad\
	, Waiting\
	, Broken

from Game.GameElements import BaseType, Speed

from Networking.Networking import Action



class BaseLayout:
	pass

class RoadLayout:
	pass

class Walker(PathWalker):
	pass



class ItJustWorks(Strategy):

	def __init__(self, game, updateSequence):
		Strategy.__init__(self, game)

		#self.updateSequence = updateSequence
		self.updateSequence = [TOWN, TRAIN, TOWN, TRAIN]

		#some cached paths
		self.toMarkets   = None
		self.fromMarkets = None

		self.toStorages   = None
		self.fromStorages = None


	def __initPathWalkers(self):

		pass

	def __initGameLayout(self):
		self.basesLayoutBefore = None
		self.roadsLayoutBefore = None

		self.basesLayoutAfter = None
		self.roadsLayoutAfter = None

	def __initWalkCycles(self):

		pass


	def getActions(self):
		pass


	def __tryUpgrade(self):
		pass

	def __setOnWalkCycle(self):
		pass

	def __clearLayout(self):
		pass

	def __resolveConflicts(self):
		pass