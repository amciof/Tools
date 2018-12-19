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


class Token:
	NONE    = 0
	PRODUCT = 1
	ARMOR   = 2

class UltraSoldier(PathWalker):

	def __init__(self, owner, train):
		PathWalker.__init__(self, owner, train)

		self.token = Token.NONE

	def getToken(self):

		return self.token

	def setToken(self, token):

		self.token = token

	def withdrawToken(self):
		token = self.token
		self.token = Token.NONE
		return token


class ItJustWorks(Strategy):
	#or not

	THRESHOLD = 0.75

	SPLIT = 0.8

	#inits
	def __init__(self, game):
		Strategy.__init__(self, game)

		self.__initUpdateSequence()

		self.__initPathWalkers()

		self.__initCaches()

		self.__initWalkCycles()

		self.__initSplitParams()
		

	def __initUpdateSequence(self):

		self.updateSequence = [(TOWN, 3), (TRAIN, 3), (TOWN, 2), (TRAIN, 2)]

	def __initCaches(self):
		self.toMarkets  = {}
		self.toStorages = {}

		self.noIgnore = {}

	def __initPathWalkers(self):
		self.pathWalkers = {
			idx : UltraSoldier(self, train)
				for idx, train in self.game.trains.items()
					if train.playerIdx == self.game.player.idx
		}
		print("[INFO] Manages: ", len(self.pathWalkers))

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

		self.productTokens = int(whole * ItJustWorks.SPLIT)
		self.armorTokens   = whole - self.productTokens

		print('###Tokens###')
		print('Armor  : ', self.armorTokens)
		print('Product: ', self.productTokens)
		print()


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


	#get Actions
	def getActions(self):
		print('Entering getActions')

		self.resetActions()

		self.__tryUpgrade()

		self.__resetCrashed()
		
		self.__processIdle()

		self.__processFull()

		self.__getActions()
		
		return self.actions


	def __resetCrashed(self):
		for idx, walker in self.pathWalkers.items():
			if walker.train.onCooldown():
				walker.flushStates()

				#return token
				print('###Train crashed###')
				print('##getting back its token')

				token = walker.withdrawToken()

				print('#token : ', token)
				print()

				if token == Token.ARMOR:
					self.armorTokens += 1
				elif token == Token.PRODUCT:
					self.productTokens += 1

	def __processIdle(self):
		wait = 0
		for idx, walker in self.pathWalkers.items():
			if walker.idle()\
				and not walker.train.onCooldown():
					#return token
					print('###Train idle###')
					print('##getting back its token')

					token = walker.withdrawToken()

					print('#token : ', token)
					print()

					if token == Token.ARMOR:
						self.armorTokens += 1
					elif token == Token.PRODUCT:
						self.productTokens += 1

					#obtain 
					print('###Tokens available###')
					print('##Armor  : ', self.armorTokens)
					print('##Product: ', self.productTokens)
					if self.armorTokens >= self.productTokens:
						print('#Armor chosen')
						walkCycle = self.storagesCycle
						token     = Token.ARMOR

						self.armorTokens -= 1
					else:
						print('#Product chosen')
						walkCycle = self.marketsCycle
						token     = Token.PRODUCT

						self.productTokens -= 1
					print()

					#prepare for walking
					self.__setOnWalkCycle(walker, walkCycle)
					walker.setToken(token)
					walker.pushState(Waiting, Waiting.Params(wait))

					wait += 5

	def __processFull(self):
		for idx, walker in self.pathWalkers.items():
			if not walker.back()\
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
		if len(self.updateSequence) != 0:
			if self.updateSequence[-1] == TRAIN:
				allUpgraded = True
				for idx, walker in self.pathWalkers.items():
					if walker.idle():
						idx     = self.pathWalker.train.getIdx()
						level   = self.pathWalker.train.level
						price   = self.pathWalker.train.nextPrice

						if level >= self.updateSequence[-1][1]:
							continue

						onStock = self.town.armor
						if onStock >= price:
							self.actions[Action.UPGRADE]['trains'].append(idx)
							self.town.armor -= price
						else:
							allUpgraded = False

				if allUpgraded:
					del self.updateSequence[-1]

			elif self.updateSequence[-1] == TOWN:
				idx     = self.town.getBaseIdx()
				level   = self.town.level
				price   = self.town.nextPrice
				onStock = self.town.armor
				if onStock >= price:
					self.actions[Action.UPGRADE]['posts'].append(idx)
					del self.updateSequence[-1]

	def __getActions(self):
		for idx, walker in self.pathWalkers.items():
			self.actions[Action.MOVE][idx] = walker.getAction()

