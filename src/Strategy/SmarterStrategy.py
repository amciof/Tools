
import sys
sys.path.append('../')


from Strategy.StrategyAbs import Strategy
from Strategy.PathWalker  import PathWalker, Path, WalkerStateType, Idle, WalkingRoad, WalkingPath, Waiting, Broken

from Game.GameElements import Speed
from Game.GameElements import BaseType


import heapq  as hq


class StrategyStateType:
	pass

class StrategyState:
	pass



INT_INF = 2000000000

class SmarterStrategy(Strategy):
	
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

		self.town = self.game.player.home;

		self.markets    = [
			base.getBaseIdx() 
				for idx, base in self.game.bases.items() 
					if base.getType() == BaseType.MARKET
		]

		self.storages   = [
			base.getBaseIdx() 
				for idx, base in self.game.bases.items() 
					if base.getType() == BaseType.STORAGE
		]

		self.pathWalkers = [
			PathWalker(self, train) 
				for idx, train in self.game.trains.items()
		]

		#self.updateSequence = updateSequence
		self.updateSequence = [TOWN, TOWN, TRAIN, TRAIN]


	def getActions(self):

		idle = [
			walker
			for walker in self.pathWalkers 
				if walker.peekState().getType() == WalkerStateType.IDLE
		]

		for walker in idle:
			pass
		
	#path finding
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

