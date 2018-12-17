import sys
sys.path.append('../')

import heapq  as hq

from Game.GameElements import BaseType
from Networking.Networking import Action

INT_INF = 2000000000

TRAIN = 0
TOWN  = 1

#base class for strategies
class Strategy:

	def __init__(self, game):
		self.game  = game
		self.actions = {}

		self.town    = self.game.bases[self.game.player.home]
		self.townIdx = self.town.getBaseIdx()

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


	def getActions(self):
		pass


	def resetActions(self):
		self.actions = {
			  Action.UPGRADE : {'posts' : [], 'trains' : []}
			, Action.MOVE    : {} #key: trainIdx value: move params
		}


	#path finding
	#returns dist, pred
	def dijkstra(self, start):
		pqueue = []
		dist = {}
		pred = {}
		for idx in self.game.adjacencyRel:
			dist[idx] = INT_INF
			pred[idx] = -1

		dist[start] = 0
		pred[start] = -1
		hq.heappush(pqueue, (0, start))

		while len(pqueue) != 0:
			d, curr = hq.heappop(pqueue)

			if dist[curr] < d:
				continue

			for to, edge in self.game.adjacencyRel[curr].items():
				newDist = dist[curr] + edge.length
				if newDist < dist[to]:
					dist[to] = newDist
					pred[to] = curr

					hq.heappush(pqueue, (dist[to], to))

		return dist, pred

	def dijkstraIgnoreVertexes(self, start, ignoreVertexes):
		pqueue = []
		dist = {}
		pred = {}
		for idx in self.game.adjacencyRel:
			dist[idx] = INT_INF
			pred[idx] = -1

		dist[start] = 0
		pred[start] = -1
		hq.heappush(pqueue, (0, start))

		while len(pqueue) != 0:
			d, curr = hq.heappop(pqueue)

			if dist[curr] < d:
				continue

			for to, edge in self.game.adjacencyRel[curr].items():

				if to in ignoreVertexes:
					continue

				newDist = dist[curr] + edge.length
				if newDist < dist[to]:
					dist[to] = newDist
					pred[to] = curr
					hq.heappush(pqueue, (dist[to], to))

		return dist, pred

	def dijkstraIgnoreEdges(self, start, ignoreEdges):
		pqueue = []
		dist = {}
		pred = {}
		for idx in self.game.adjacencyRel:
			dist[idx] = INT_INF
			pred[idx] = -1

		dist[start] = 0
		pred[start] = -1
		hq.heappush(pqueue, (0, start))

		while len(pqueue) != 0:
			d, curr = hq.heappop(pqueue)

			if dist[curr] < d:
				continue

			for to, edge in self.game.adjacencyRel[curr].items():

				if edge.getIdx() in ignoreEdges:
					continue

				newDist = dist[curr] + edge.length
				if newDist < dist[to]:
					dist[to] = newDist
					pred[to] = curr
					hq.heappush(pqueue, (dist[to], to))

		return dist, pred
