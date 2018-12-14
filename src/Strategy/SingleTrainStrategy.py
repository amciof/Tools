import sys
sys.path.append('../')


from Strategy.StrategyAbs import Strategy, INT_INF, TOWN, TRAIN
from Strategy.PathWalker  import PathWalker, Path, WalkerStateType, Idle, WalkingRoad, WalkingPath, Waiting, Broken

from Game.GameElements import Speed
from Game.GameElements import BaseType

from Networking.Networking import Action


class Best:
	def __init__(self, base, obtained, toDist, toPred, backDist, backPred):
		self.base     = base
		self.obtained = obtained
		self.toDist   = toDist
		self.toPred   = toPred
		self.backDist = backDist
		self.backPred = backPred

class SingleTrainStrategy(Strategy):

	def __init__(self, game, updateSequence):
		Strategy.__init__(self, game)

		#we have only one train
		train = list(self.game.trains.values())[0]
		self.pathWalker = PathWalker(self, train)

		#self.updateSequence = updateSequence
		self.updateSequence = [TOWN, TOWN, TRAIN, TRAIN]

		#some cached paths
		self.toMarkets   = None
		self.fromMarkets = None

		self.toStorages   = None
		self.fromStorages = None


	def getActions(self):
		#in this strategy pathwalker is idle => it's in the town
		self.resetActions()
	
		print(self.pathWalker.train.level)
		print(self.town.population)
		print()

		if self.pathWalker.idle():
			self.__tryUpgrade()

			bestStorage = self.__obtainArmor(self.town.product)
			if not bestStorage is None:
				self.__walkBestPath(bestStorage, self.town, bestStorage.base)

			else:
				bestMarket = self.__obtainProduct(self.town.product)
				if not bestMarket is None:
					self.__walkBestPath(bestMarket, self.town, bestMarket.base)

		idx  = self.pathWalker.train.getIdx()
		self.actions[Action.MOVE][idx] = self.pathWalker.getAction()

		return self.actions


	def __tryUpgrade(self):
		if len(self.updateSequence) != 0:
			if self.updateSequence[-1] == TRAIN:
				idx     = self.pathWalker.train.getIdx()
				level   = self.pathWalker.train.level
				price   = self.pathWalker.train.nextPrice
				onStock = self.town.armor
				if onStock >= price:
					self.actions[Action.UPGRADE]['trains'].append(idx)
					del self.updateSequence[-1]

			elif self.updateSequence[-1] == TOWN:
				idx     = self.town.getBaseIdx()
				level   = self.town.level
				price   = self.town.nextPrice
				onStock = self.town.armor
				if onStock >= price:
					self.actions[Action.UPGRADE]['posts'].append(idx)
					del self.updateSequence[-1]

	def __obtainArmor(self, currProduct):
		bestStorage = None
		bestMarket  = None

		for storage in self.storages:
			toDist, toPred = self.dijkstraIgnoreVertexes(self.town.getBaseIdx(), self.marketsIdx)

			if toDist[storage.getBaseIdx()] != INT_INF:
				backDist, backPred = self.dijkstra(storage.getBaseIdx())

				timeTo   = toDist[storage.getBaseIdx()]
				timeBack = backDist[self.town.getBaseIdx()]

				product = currProduct - self.town.population * (timeTo + timeBack)

				obtained = storage.armor + storage.replenishment * timeTo
				obtained = min(storage.armorCapacity, obtained)
				obtained = min(self.pathWalker.train.goodsCapacity, obtained)

				bestMarket = self.__obtainProduct(product)

				if not bestMarket is None:
					newBest = Best(storage, obtained, toDist, toPred, backDist, backPred)

					if not bestStorage is None:
						if bestStorage.obtained < obtained:
							bestStorage = newBest
					else:
						bestStorage = newBest

		return bestStorage

	def __obtainProduct(self, currProduct):
		bestMarket = None

		for market in self.markets:
			toDist, toPred = self.dijkstraIgnoreVertexes(self.town.getBaseIdx(), self.storagesIdx)

			if toDist[market.getBaseIdx()] != INT_INF:
				backDist, backPred = self.dijkstra(market.getBaseIdx())

				timeTo   = toDist[market.getBaseIdx()]
				timeBack = backDist[self.town.getBaseIdx()] 

				product  = currProduct - self.town.population * (timeTo + timeBack)

				obtained = market.product + market.replenishment * timeTo
				obtained = min(market.productCapacity, obtained)
				obtained = min(self.pathWalker.train.goodsCapacity, obtained)

				if product <= 0 and abs(product) > self.town.population:
					continue
				else:
					newBest = Best(market, obtained, toDist, toPred, backDist, backPred)

					if not bestMarket is None:
						if bestMarket.obtained < obtained:
							bestMarket = newBest
					else:
						bestMarket = newBest

		return bestMarket

	def __walkBestPath(self, best, fromBase, toBase):
		to = Path(
			self.game.adjacencyRel
			, best.toDist
			, best.toPred
			, fromBase.getBaseIdx()
			,   toBase.getBaseIdx()
		)
		
		back = Path(
			self.game.adjacencyRel
			, best.backDist
			, best.backPred
			,   toBase.getBaseIdx()
			, fromBase.getBaseIdx()
		)

		self.pathWalker.pushState(
			WalkingPath
			, WalkingPath.Params(back)
		)
		self.pathWalker.pushState(
			WalkingPath
			, WalkingPath.Params(to)
		)
