
from SceneElements import Speed

import random as rand
import heapq  as hq

#base class for strategies
class Strategy:

	def __init__(self, game):
		self.game  = game
		self.graph = game.adjacencyRel
		self.moves = []

	def getMoves(self):
		pass


#really primitive random choose strategy
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


#Shortest path strategy(dijkstra alg)
#TODO: rework this shit
class Path:
	#start  -> path start
	#end    -> path end
	#edgesDict -> dict of tuples(i_list, edge, speed)
	#edgesList -> list of tuples(edge, speed)
	#length -> path length

	#don't touch that
	def __init__(self, start, end):
		self.start  = start
		self.end    = end
		self.length = 0

		self.edgesDict = {}
		self.edgesList = []

class TrainState:
	#Cant't move(in fact train is stopped)
	IDLE = 0

	#On the way to resources
	COLLECTING = 1

	#Resource collected. Returning to base
	RETURNING = 2

	#Stupid fucking WG server lagged so train is off the path.
	#So we need to chose what adjacent base to return(from which path is shorter)
	CORRECTING = 3 

#TODO: rework this
class TrainManager:
	
	def __init__(self, strategy, path, train):
		#TODO - total rework
		self.train = train
		self.state = TrainState.COLLECTING
		self.path  = path
		self.curr  = 0

		currEdge, currSpeed = self.path.edgesList[self.curr]

		self.edgePos = -1 if currSpeed == Speed.FORWARD else (currEdge.getLength() + 1)


	def getMove(self):
		if self.state == TrainState.IDLE:
			return self.__caseIDLE()

		elif self.state == TrainState.COLLECTING:
			return self.__caseCOLLECTING()

		elif self.state == TrainState.RETURNING:
			return self.__caseRETURNING()

	def __caseIDLE(self):
		currEdge = self.train.getRoad()

		return (currEdge.getIdx(), Speed.STOP, self.train.getIdx())

	def __caseCOLLECTING(self):
		print('---Collecting---')

		currEdge, currSpeed = self.path.edgesList[self.curr]

		if self.train.full():
			print('--Train is full. Returning to base--')
			self.state    = TrainState.RETURNING
			self.edgePos -= currSpeed

			#move
			move = (currEdge.getIdx(), -currSpeed, self.train.getIdx())

		else:
			limit = currEdge.getLength() if currSpeed == Speed.FORWARD else 0

			if self.edgePos == limit:
				print('--End of road--')
				self.curr += 1

				if self.curr >= len(self.path.edgesList):
					print('-End of path. Returning to base-')
					self.state = TrainState.RETURNING
					self.curr  = len(self.path.edgesList) - 1

					nextEdge, nextSpeed = self.path.edgesList[self.curr]

					self.edgePos -= nextSpeed

					#move
					move = (currEdge.getIdx(), -currSpeed, self.train.getIdx())

				else:
					print('-Jumping to new road-')
					nextEdge, nextSpeed = self.path.edgesList[self.curr]

					self.edgePos = 0 if nextSpeed == Speed.FORWARD else nextEdge.getLength()

					self.edgePos += nextSpeed

					#move
					move = (nextEdge.getIdx(), nextSpeed, self.train.getIdx())

			else:
				print('--Continue moving--')
				self.edgePos += currSpeed
				#move
				move = (currEdge.getIdx(), currSpeed, self.train.getIdx())

		return move

	def __caseRETURNING(self):
		print('---Returning---')
		currEdge, currSpeed = self.path.edgesList[self.curr]
		
		limit = currEdge.getLength() if currSpeed == -Speed.FORWARD else 0

		if self.edgePos == limit:
			print('--End of road--')
			self.curr += -1

			if self.curr < 0:
				print('-Returned. Start collecting.-')
				self.state = TrainState.COLLECTING
				self.curr  = 0

				nextEdge, nextSpeed = self.path.edgesList[self.curr]

				self.edgePos -= -nextSpeed

				#move
				move = (currEdge.getIdx(), currSpeed, self.train.getIdx())

			else:
				print('-Jump to next road-')
				nextEdge, nextSpeed = self.path.edgesList[self.curr]

				self.edgePos = 0 if nextSpeed == -Speed.FORWARD else nextEdge.getLength()

				self.edgePos += -nextSpeed

				#move
				move = (nextEdge.getIdx(), -nextSpeed, self.train.getIdx())

		else:
			print('--Continue moving--')
			self.edgePos += -currSpeed
			#move
			move = (currEdge.getIdx(), -currSpeed, self.train.getIdx())

		return move


	def getState(self):

		return self.state

	def validate(self):
		road  = self.train.getRoad()
		pos   = self.train.getPosition()
		speed = self.train.getSpeed()

		currRoad, currSpeed = self.path.edgesList[self.curr]
		
		if not (currRoad.getIdx() == road.getIdx() \
			and self.edgePos == pos \
			and currSpeed == speed):
			self.state = TrainManager.INVALID

#estimates best moves
class PrimitiveStrategy(Strategy):
	
	def __init__(self, game, town, markets):
		Strategy.__init__(self, game)

		#all markets idx
		self.markets = markets

		#cache all shortest paths
		self.__cacheAllPaths()

		self.trainState = {}
		for idx, train in self.game.trains.items():
			self.trainState[idx] = TrainManager(self, self.allPath[25][33], train)

	#probably unnesessary
	def __cacheAllPaths(self):
		self.allPath = {}

		#TODO: rework
		allIdx = list(self.game.bases.keys())
		for i, start in enumerate(allIdx):
			dist, pred = self.__dijkstra(start)

			paths = self.__restorePaths(start, pred)

			self.allPath[start] = {}
			for end, path in paths.items():
				self.allPath[start][end] = path

	#probably unnesessary
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

	5
	#TODO: improve
	#multiple resources now
	#need to find shortest path ignoring bases of other resource type
	#(we don't want to obtain this resource)
	def __dijkstra(self, start):
		INT_INF = 2000000000

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


	#logic
	def getMoves(self):
		self.moves = []
		
		for idx, state in self.trainState.items():
			self.moves.append(state.getMove())

		return self.moves
