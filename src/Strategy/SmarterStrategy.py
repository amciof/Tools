
import sys
sys.path.append('../')


from .StrategyAbs import Strategy
from .PathWalker  import PathWalker, Path, StateType, Idle, WalkingRoad, WalkingPath, Waiting, Broken

from Game.GameElements import Speed

import heapq  as hq


INT_INF = 2000000000


class SmarterStrategy(Strategy):
	
	def __init__(self, game, updateSequence):
		Strategy.__init__(self, game)

		self.town     = None
		self.markets  = []
		self.storages = []

		self.updateSequence = updateSequence

		self.pathWalkers = []


	def getActions(self):

		pass


	#path finding
	def __restorePaths(self, start, pred):
		paths = {}
		
		for idx in self.game.bases:
			if idx != start:
				path = Path(start, idx)
				
				curr = idx
				while pred[curr] != -1:
					next = pred[curr]

					edge = self.graph[next][curr]

					edgeId = edge.getIdx()
					length = edge.getLength()
					idx1, idx2 = edge.getAdjacentIdx()

					speed = Speed.FORWARD if next == idx1 else Speed.BACKWARD
					path.edgesList.append( (edge, speed) )
					path.length += length

					curr = next

				path.edgesList = path.edgesList[::-1]
				for i, unit in enumerate(path.edgesList):
					edge, speed = unit
					path.edgesDict[edge.getIdx()] = (i, edge, speed)

				paths[idx] = path

		return paths

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

	#TODO
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
				newDist = dist[curr] + edge.length
				if newDist < dist[to]:
					dist[to] = newDist
					pred[to] = curr
					hq.heappush(pqueue, (dist[to], to))

		return dist, pred

	#TODO
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
				newDist = dist[curr] + edge.length
				if newDist < dist[to]:
					dist[to] = newDist
					pred[to] = curr
					hq.heappush(pqueue, (dist[to], to))

		return dist, pred


	
