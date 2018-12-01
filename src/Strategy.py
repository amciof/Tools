try:
    import Queue as Q  # ver. < 3.0
except ImportError:
    import queue as Q


class Strategy:

	def __init__(self, game):
		#do whatever initialization you need

		#self.game  = game - ref to game
		#self.moves = []   - sequence of moves
		#and other inits
		pass

	def playStrategy(self):
		#calculate the moves
		#and create self.moves list
		pass

	def getMoves(self):
		#return self.moves
		pass

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

		return cost_so_far,came_from