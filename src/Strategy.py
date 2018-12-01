try:
	import Queue as Q  # ver. < 3.0
except ImportError:
	import queue as Q


class Strategy:

	def __init__(self, game):
		self.game = game
		self.graph = game.adjacencyRel
		self.moves = []

	def getMoves(self):
		self.moves.clear()
		for idx, train in self.game.trains.items():
			position = train.getPosition()
			road = train.getRoad()
			if position == road.length:
				import random as rand
				start = road.base2.getBaseIdx()
				keys = list(self.graph.get(start).keys())
				end = rand.choice(keys)
				line_idx = self.graph.get(start).get(end).idx
			else:
				line_idx = road.idx
			self.moves.append((line_idx, 1, idx))
		return self.moves

	def Dijkstra(S, adjacencyLists):
		priority_queue = Q.PriorityQueue()
		priority_queue.put(S, 0)

		came_from = {}
		cost_so_far = {}
		came_from[S] = S
		cost_so_far[S] = 0

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
