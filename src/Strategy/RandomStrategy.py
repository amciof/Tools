from .StrategyAbs import Strategy

import random as rand

#really primitive random choose strategy
class RandomStrategy(Strategy):

	def __init__(self, game):
		Strategy.__init__(self, game)

	def getActions(self):
		moves = []
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

				moves.append((line_idx, speed, idx))

			elif train.speed == 0:
				speed = rand.choice([Speed.FORWARD, Speed.BACKWARD])
				moves.append((train.getRoad().getIdx(), speed, idx))

		return moves