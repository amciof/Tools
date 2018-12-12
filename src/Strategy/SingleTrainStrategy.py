import sys
sys.path.append('../')

import heapq  as hq


from Strategy.StrategyAbs import Strategy
from Strategy.PathWalker  import PathWalker, Path, WalkerStateType, Idle, WalkingRoad, WalkingPath, Waiting, Broken

from Game.GameElements import Speed
from Game.GameElements import BaseType

from Networking.Networking import Action


INT_INF = 2000000000

UPGRADES_TOWN = {
	 1 : 100
	, 2 : 200
}

UPGRADES_TRAIN = {
	1 : 40
	, 2 : 80
}

TRAIN = 0
TOWN  = 1


class Best:
	def __init__(self, base, obtained, toDist, toPred, backDist, backPred):
		self.base     = base
		self.obtained = obtained
		self.toDist   = toDist
		self.toPred   = toPred
		self.backDist = backDist
		self.backPred = backPred

class SingleTrainStrategy(Strategy):
	#UPGRADE action
	#This action upgrades trains and posts to the next level.

	#The server expects to receive following required values:

	#posts - list with indexes of posts to upgrade
	#trains - list with indexes of trains to upgrade
	#Example: UPGRADE request
	#b'\x04\x00\x00\x00\x19\x00\x00\x00{"posts":[],"trains":[1]}'

	#|action|msg length|msg                      |
	#|------|----------|-------------------------|
	#|4     |25        |{"posts":[],"trains":[1]}|

	#Теперь возможны прибытия беженцев (от 1 до 2) с вероятностью 50% 
	#и периодом появления [10 ходов * кол-во беженцев]


	def __init__(self, game, updateSequence):
		Strategy.__init__(self, game)

		self.town = self.game.bases[self.game.player.home]

		self.markets = [
			base
				for idx, base in self.game.bases.items() 
					if base.getType() == BaseType.MARKET
		]
		self.markets.sort(key=lambda market: -market.replenishment)
		self.marketsIdx = {market.getBaseIdx() for market in self.markets}

		self.storages = [
			base
				for idx, base in self.game.bases.items() 
					if base.getType() == BaseType.STORAGE
		]
		self.storages.sort(key=lambda storage: -storage.replenishment)
		self.storagesIdx = {storage.getBaseIdx() for storage in self.storages}
		

		#self.pathWalkers = [
		#	PathWalker(self, train) 
		#		for idx, train in self.game.trains.items()
		#]

		#we have only one train
		train = list(self.game.trains.values())[0]
		self.pathWalker = PathWalker(self, train)

		#self.updateSequence = updateSequence
		self.updateSequence = [TOWN, TOWN, TRAIN, TRAIN]

		#actions to return
		self.actions = {}

		#some cached paths
		self.toMarkets   = None
		self.fromMarkets = None

		self.toStorages   = None
		self.fromStorages = None


	def getActions(self):
		#in this strategy pathwalker is idle => it's in the town
		self.actions = {
			  Action.UPGRADE : []
			, Action.MOVE    : []
		}

		if self.pathWalker.idle():
			self.__tryUpgrade()

			bestStorage, bestMarket = self.__obtainArmor(self.town.product)
			if not bestStorage is None:
				self.__walkBestPath(bestStorage, self.town, bestStorage.base)
				self.__walkBestPath(bestMarket , self.town,  bestMarket.base)

			else:
				bestMarket = self.__obtainProduct()
				if not bestMarket is None:
					self.__walkBestPath(bestMarket, self.town, bestMarket.base)

		self.actions[Action.MOVE].append(self.pathWalker.getAction())

		return self.actions


	def __tryUpgrade(self):
		if len(self.updateSequence) != 0:
			if self.updateSequence[-1] == TRAIN:
				level   = self.pathWalker.train.level
				price   = self.pathWalker.train.nextPrice
				onStock = self.town.armor
				
			elif self.updateSequence[-1] == TOWN:
				pass

	def __obtainArmor(self, currProduct):
		bestStorage = None
		bestMarket  = None

		for storage in self.storages:
			toDist, toPred = self.__dijkstraIgnoreVertexes(self.town.getBaseIdx(), self.marketsIdx)

			if toDist[storage.getBaseIdx()] != INT_INF:
				backDist, backPred = self.__dijkstra(storage.getBaseIdx())

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

		return bestStorage, bestMarket

	def __obtainProduct(self, currProduct):
		bestMarket = None

		for market in self.markets:
			toDist, toPred = self.__dijkstraIgnoreVertexes(self.town.getBaseIdx(), self.storagesIdx)

			if toDist[market.getBaseIdx()] != INT_INF:
				backDist, backPred = self.__dijkstra(market.getBaseIdx())

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


	#path finding
	#returns dist, pred
	def __dijkstra(self, start):
		pqueue = []
		dist = {}
		pred = {}
		for idx in self.graph:
			dist[idx] = INT_INF
			pred[idx] = -1

		dist[start] = 0
		pred[start] = -1
		hq.heappush(pqueue, (0, start))

		while len(pqueue) != 0:
			d, curr = hq.heappop(pqueue)

			if dist[curr] < d:
				continue

			for to, edge in self.graph[curr].items():
				newDist = dist[curr] + edge.length
				if newDist < dist[to]:
					dist[to] = newDist
					pred[to] = curr
					hq.heappush(pqueue, (dist[to], to))

		return dist, pred

	def __dijkstraIgnoreVertexes(self, start, ignoreVertexes):
		pqueue = []
		dist = {}
		pred = {}
		for idx in self.graph:
			dist[idx] = INT_INF
			pred[idx] = -1

		dist[start] = 0
		pred[start] = -1
		hq.heappush(pqueue, (0, start))

		while len(pqueue) != 0:
			d, curr = hq.heappop(pqueue)

			if dist[curr] < d:
				continue

			for to, edge in self.graph[curr].items():

				if to in ignoreVertexes:
					continue

				newDist = dist[curr] + edge.length
				if newDist < dist[to]:
					dist[to] = newDist
					pred[to] = curr
					hq.heappush(pqueue, (dist[to], to))

		return dist, pred

	def __dijkstraIgnoreEdges(self, start, ignoreEdges):
		pqueue = []
		dist = {}
		pred = {}
		for idx in self.graph:
			dist[idx] = INT_INF
			pred[idx] = -1

		dist[start] = 0
		pred[start] = -1
		hq.heappush(pqueue, (0, start))

		while len(pqueue) != 0:
			d, curr = hq.heappop(pqueue)

			if dist[curr] < d:
				continue

			for to, edge in self.graph[curr].items():

				if edge.getIdx() in ignoreEdges:
					continue

				newDist = dist[curr] + edge.length
				if newDist < dist[to]:
					dist[to] = newDist
					pred[to] = curr
					hq.heappush(pqueue, (dist[to], to))

		return dist, pred
