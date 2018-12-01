try:
	import Queue as Q  # ver. < 3.0
except ImportError:
	import queue as Q

from SceneElements import Speed

import random as rand
import heapq  

class Strategy:

	def __init__(self, game):
		self.game = game
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


class PrimitiveStrategy(Strategy):

	def __init__(self, game):
		Strategy.__init__(self, game)

	def getMoves(self):
		pass

	def dijkstra(self, adjacencyLists):
		priority_queue = Q.PriorityQueue()
		priority_queue.put(self, 0)

		came_from   = {}
		cost_so_far = {}
		came_from[self]   = self
		cost_so_far[self] = 0

		while not priority_queue.empty():
			current = priority_queue.get()

			for next in range(len(adjacencyLists[current])):
				new_cost = cost_so_far[current] + adjacencyLists[current][next]
				if next not in cost_so_far or new_cost < cost_so_far[next]:
					cost_so_far[next] = new_cost
					priority = new_cost
					priority_queue.put(next, priority)
					came_from[next] = current

		return cost_so_far, came_from