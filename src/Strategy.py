
from SceneElements import Speed

import random as rand
import heapq  as hq


class Strategy:

	def __init__(self, game):
		self.game  = game
		self.graph = game.adjacencyRel
		self.moves = []

	def getMoves(self):
		pass


class RandomStrategy(Strategy):

	def __init__(self, game):
		Strategy.__init__(self, game)

	def getMoves(self):
		self.moves.clear()
		for idx, train in self.game.trains.items():
			position = train.getPosition()
			road     = train.getRoad()

			if position == 0 or position == road.getLength():
				idx1, idx2 = road.getAdjacentIdx()

				start    = idx1 if position == 0 else idx2
				adjacent = list(self.graph[start].keys())
				end      = rand.choice(adjacent)
				new_road = self.graph[start][end]

				idx1, idx2 = new_road.getAdjacentIdx()

				line_idx = new_road.getIdx()
				speed    = Speed.FORWARD if start == idx1 else Speed.BACKWARD

				self.moves.append((line_idx, speed, idx))

			elif train.speed == 0:
				speed = rand.choice([Speed.FORWARD, Speed.BACKWARD])
				self.moves.append((train.getRoad().getIdx(), speed, idx))

		return self.moves

INT_INF = 2000000000

class PrimitiveStrategy(Strategy):
	
	def __init__(self, game):
		Strategy.__init__(self, game)

	def getMoves(self):
		pass

	def _dijkstra(self, start):
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

