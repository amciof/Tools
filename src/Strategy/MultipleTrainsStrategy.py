from Strategy.StrategyAbs import Strategy, INT_INF, TRAIN, TOWN
from Strategy.PathWalker import Path\
	, PathWalker\
	, WalkingPath\
	, WalkingRoad\
	, Waiting\
	, Broken

from Game.GameElements import BaseType, Speed

from Networking.Networking import Action


class ItJustWorks(Strategy):

	def __init__(self, game, updateSequence):
		Strategy.__init__(self, game)

		self.__initUpdateSequence()

		self.__initPathWalkers()

		self.__initCaches()

		self.__initWalkCycles()


	def __initUpdateSequence():

		self.updateSequence = [TOWN, TRAIN, TOWN, TRAIN]

	def __initCaches(self):
		self.toMarkets  = {}
		self.toStorages = {}

		self.noIgnore = {}

	def __initPathWalkers(self):
		self.pathWalkers = {
			idx : PathWalker(self, train) for idx, train in self.game.trains.items()
		}

	def __initWalkCycles(self):
		
		#cache paths to markets
		dist, pred = self.dijkstraIgnoreVertexes(
				self.townIdx
				, set(self.storagesIdx)
		)
		for idx in self.marketsIdx:
			if dist[idx] != INT_INF:
				self.toMarkets[self.townIdx][idx] = Path(
					self.game.adjacencyRel
					, dist
					, pred
					, self.townIdx
					, idx
				)

		#cache paths to storages
		dist, pred = self.dijkstraIgnoreVertexes(
			self.townIdx
			, set(self.marketsIdx)
		)
		for idx in self.storagesIdx:
			if dist[idx] != INT_INF:
				self.toStorages[self.townIdx][idx] = Path(
					self.game.adjacencyRel
					, dist
					, pred
					, self.townIdx
					, idx
				)

		#cache back-paths
		for idx in self.marketsIdx:
			dist, pred = self.dijkstra(idx)
			if dist[self.townIdx] != INT_INF:
				self.noIgnore[idx][self.townIdx] = Path(
					self.game.adjacencyRel
					, dist
					, pred
					, idx
					, self.townIdx
			)

		for idx in self.storagesIdx:
			dist, pred = self.dijkstra(idx)
			if dist[self.townIdx] != INT_INF:
				self.noIgnore[idx][self.townIdx] = Path(
					self.game.adjacencyRel
					, dist
					, pred
					, idx
					, self.townIdx
			)

		#init walk cycles


	def getActions(self):
		pass


	def __findPath(self):
		pass

	def __findPathIgnoreVertexes(self):
		pass

	def __findPathIgnoreEdges(self):
		pass


	def __tryUpgrade(self):
		pass


	def __setOnWalkCycle(self):
		pass

	def __resolveConflicts(self):
		pass