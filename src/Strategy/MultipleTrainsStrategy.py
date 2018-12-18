from itertools import permutations
import itertools

from Strategy.StrategyAbs import Strategy, INT_INF, TRAIN, TOWN
from Strategy.PathWalker import Path\
	, PathWalker\
	, WalkerStateType\
	, WalkingPath\
	, WalkingBack\
	, WalkingRoad\
	, Waiting\
	, Broken

from Game.GameElements import BaseType, Speed

from Networking.Networking import Action


class Resource:
	NONE    = 0
	PRODUCT = 1
	ARMOR   = 2

class UltraSoldier(PathWalker):

	def __init__(self, owner, train):
		PathWalker.__init__(self, owner, train)

		self.resource = Resource.NONE

	def getResource(self):

		return self.resource

	def setResource(self):

		return self.resource


class ItJustWorks(Strategy):
	#or not

	THRESHOLD = 0.75

	SPLIT = 0.7

	#inits
	def __init__(self, game):
		Strategy.__init__(self, game)

		self.__initUpdateSequence()

		self.__initPathWalkers()

		self.__initCaches()

		self.__initWalkCycles()

		self.__initSplitParams()
		

	def __initUpdateSequence(self):

		self.updateSequence = [TOWN, TRAIN, TOWN, TRAIN]

	def __initCaches(self):
		self.toMarkets  = {}
		self.toStorages = {}

		self.noIgnore = {}

	def __initPathWalkers(self):
		self.pathWalkers = {
			idx : UltraSoldier(self, train) for idx, train in self.game.trains.items()
		}

	def __initWalkCycles(self):
		#cache paths to markets
		self.__cachePaths(
			self.townIdx
			, self.toMarkets
			, self.marketsIdx
			, set(self.storagesIdx)
		)

		#cache paths to storages
		self.__cachePaths(
			self.townIdx
			, self.toStorages
			, self.storagesIdx
			, set(self.marketsIdx)
		)

		#cache back-paths & paths to other bases
		#markets
		self.__cacheBackPaths(self.townIdx, self.noIgnore, self.marketsIdx)
		
		#storages
		self.__cacheBackPaths(self.townIdx, self.noIgnore, self.storagesIdx)

		#init walk cycles
		#markets
		self.marketsCycle = self.__getCycle(
			self.toMarkets
			, self.noIgnore
			, self.townIdx
			, set(self.marketsIdx)
		)

		#storage
		self.storagesCycle = self.__getCycle(
			self.toStorages
			, self.noIgnore
			, self.townIdx
			, set(self.storagesIdx)
		)

		print('###Markets cycle###')
		for first, second, cache in self.marketsCycle:
			print('(%i; %i)' % (first, second))
		print()

		print('###Storages cycle###')
		for first, second, cache in self.storagesCycle:
			print('(%i; %i)' % (first, second))
		print()

	def __initSplitParams(self):
		whole = len(self.pathWalkers)

		self.product = int(whole * ItJustWorks.SPLIT)
		self.armor   = whole - self.product


	#utils
	def __cachePaths(self, start, cache, bases, ignore):
		dist, pred = self.dijkstraIgnoreVertexes(start, ignore)

		if not start in cache:
			cache[start] = {}

		for idx in bases:
			if dist[idx] != INT_INF:

				cache[start][idx] = Path(
					self.game.adjacencyRel
					, dist, pred
					, start, idx
				)

	def __cacheBackPaths(self, back, cache, bases):
		for idx in bases:
			dist, pred = self.dijkstra(idx)

			if dist[back] != INT_INF:
				if not idx in cache:
					cache[idx] = {}

				cache[idx][back] = Path(
					self.game.adjacencyRel
					, dist, pred
					, idx, back
				)

			for other in bases:
				if other != idx and dist[other] != INT_INF:
					if not idx in cache:
						cache[idx] = {}

					cache[idx][other] = Path(
						self.game.adjacencyRel
						, dist, pred
						, idx, other
					)

	def __getCycle(self, firstSearch, cachedPaths, start, bases):

		def criteriaFirst(idx):
			nonlocal self
			nonlocal firstSearch
			nonlocal start

			if start in firstSearch and idx in firstSearch[start]:
				return firstSearch[start][idx].length
			return INT_INF

		def criteria(idx):
			nonlocal self
			nonlocal cachedPaths
			nonlocal prev

			if prev in cachedPaths and idx in cachedPaths[prev]:
				return cachedPaths[prev][idx].length
			return INT_INF

		cycle = []

		next = min(bases, key = criteriaFirst)
		cycle.append((start, next, firstSearch))
		bases.remove(next)

		while len(bases) > 0:
			prev = next
			next = min(bases, key = criteria)
			cycle.append((prev, next, cachedPaths))
			bases.remove(next)
		
		cycle.append((next, start, cachedPaths))

		return cycle

	def __setOnWalkCycle(self, pathWalker, cycle):
		for first, second, cache in reversed(cycle):
			path = cache[first][second]

			pathWalker.pushState(WalkingPath, WalkingPath.Params(path))

	def __getConflictsMap(self):
		pass


	#get Actions
	def getActions(self):
		self.resetActions()

		self.__resetCrashed()
		
		self.__processIdle()

		self.__processFull()

		self.__getActions()
		
		self.__resolveConflicts()

		return self.actions


	def __resetCrashed(self):
		for idx, walker in self.pathWalkers.items():
			if walker.train.onCooldown():
				walker.flushStates()

	def __processIdle(self):
		for idx, walker in self.pathWalkers.items():
			if walker.peekState().getType() == WalkerStateType.IDLE\
				and not walker.train.onCooldown():

				wait = 0
				for idx, walker in self.pathWalkers.items():
					self.__setOnWalkCycle(walker, self.marketsCycle)
					walker.pushState(Waiting, Waiting.Params(wait))
					wait += 5

	def __processFull(self):
		for idx, walker in self.pathWalkers.items():
			if not walker.peekState().getType() == WalkerStateType.WALKING_BACK\
				\
			   and walker.train.fullThreshold(ItJustWorks.THRESHOLD):

				road = walker.train.getRoad()
				pos  = walker.train.getPosition()

				idx1, idx2 = road.getAdjacentIdx()
				if pos == 0:
					base = idx1
				elif pos == road.getLength():
					base = idx2
				else:
					base = None

				if base is None:
					print('[DEBUG] Train %i is full and not in base' % (idx))
					print()
					continue

				path = self.noIgnore[base][self.townIdx]

				walker.flushStates()
				walker.pushState(WalkingBack, WalkingBack.Params(path))

	def __tryUpgrade(self):
		pass

	def __getActions(self):
		for idx, walker in self.pathWalkers.items():
			self.actions[Action.MOVE][idx] = walker.getAction()

	def __resolveConflicts(self):
		pass

	
	#????
	def __findPath(self):
		pass

	def __findPathIgnoreVertexes(self):
		pass

	def __findPathIgnoreEdges(self):
		pass

