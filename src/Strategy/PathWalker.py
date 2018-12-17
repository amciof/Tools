
import sys
sys.path.append('../')


from Game.GameElements import Speed


#path struct
class Path:

	D_INDEX = 0 #path.roadsDict[roadIdx][0] -> path.roadsDict[roadIdx][Path.D_INDEX]
	D_SPEED = 1 #path.roadsDict[roadIdx][1] -> path.roadsDict[roadIdx][Path.D_SPEED]

	L_ROAD  = 0 #path.roadsList[index][0] -> path.roadsList[index][Path.L_ROAD]
	L_SPEED = 1 #path.roadsList[index][0] -> path.roadsList[index][Path.L_SPEED]

	#start  -> path start
	#end    -> path end
	#roadsDict -> dict of (key: roadIdx, value: tuple(i_list, speed))
	#roadsList -> list of tuples(roadIdx, speed)
	#basesSequence -> dict of (key : baseId, value : tuple(roadIdx, speed))
	#length -> path length

	def __init__(self, adjacencyRel, dist, pred, start, end):
		self.start = start
		self.end   = end

		self.length = dist[end]

		self.roadsDict, self.roadsList, self.basesSequence = self.__restorePath(adjacencyRel, end, pred)

	def __restorePath(self, adjacencyRel, end, pred):
		roadsDict = {}
		roadsList = []
		basesSequence = {}

		basesSequence[end] = -1
		curr = end
		while pred[curr] != -1:
			next = pred[curr]

			road = adjacencyRel[next][curr]

			roadId = road.getIdx()
			length = road.getLength()

			idx1, idx2 = road.getAdjacentIdx()
			if next == idx1:
				speed = Speed.FORWARD
			else:
				speed = Speed.BACKWARD

			elem = (roadId, speed)
			roadsList.append(elem)
			basesSequence[next] = elem

			curr = next	

		roadsList = roadsList[::-1]
		for i, unit in enumerate(roadsList):
			roadId, speed = unit
			roadsDict[roadId] = (i, speed)

		return roadsDict, roadsList, basesSequence


#states
class WalkerStateType:
	IDLE = 0

	WALKING_PATH = 1
	WALKING_ROAD = 2
	WALKING_BACK = 3

	WAITING = 4

	BROKEN  = -1

class WalkerState:

	class Params:
		pass

	def __init__(self, stateType, owner, train):
		self.stateType = stateType
		self.owner     = owner
		self.train     = train


	def getAction(self):
		pass


	def getType(self):

		return self.stateType

	def getOwner(self):

		return self.owner


class Idle(WalkerState):

	class Params(WalkerState.Params):
		
		def __init__(self, owner, train):
			pass


	def __init__(self, owner, train, params):

		WalkerState.__init__(self, WalkerStateType.IDLE, owner, train)	


	def getAction(self):
		
		return (self.train.getRoad().getIdx(), Speed.STOP, self.train.getIdx())


class WalkingPath(WalkerState):

	class Params(WalkerState.Params):
		
		def __init__(self, path):
			self.path = path


	def __init__(self, owner, train, params):
		WalkerState.__init__(self, WalkerStateType.WALKING_PATH, owner, train)
		
		self.path = params.path

	
	def getAction(self):
		road = self.train.getRoad()

		if road.getIdx() in self.path.roadsDict:
			currElem  = self.path.roadsDict[road.getIdx()]
			currSpeed = currElem[Path.D_SPEED]

			limit = road.getLength() if currSpeed == Speed.FORWARD else 0

			if self.train.getPosition() == limit:
				currIndex = currElem[Path.D_INDEX]

				if currIndex == (len(self.path.roadsList) - 1):
					self.owner.popState()

					action = self.owner.getAction()

				else:
					currIndex += 1

					currElem   = self.path.roadsList[currIndex]
					currSpeed  = currElem[Path.L_SPEED]
					currRoad   = currElem[Path.L_ROAD]

					action = (currRoad, currSpeed, self.train.getIdx())

			else:
				action = (road.getIdx(), currSpeed, self.train.getIdx())

		else:
			base = self.__onPath()
			if base != -1:
				currElem  = self.path.basesSequence[base]
				currSpeed = currElem[Path.L_SPEED]
				currRoad  = currElem[Path.L_ROAD]

				action = (currRoad, currSpeed, self.train.getIdx())

			else:
				self.owner.pushState(Broken, None)

				action = self.owner.getAction()

		return action

	def __onPath(self):
		road = self.train.getRoad()
		pos  = self.train.getPosition()

		idx1, idx2 = road.getAdjacentIdx()
		length     = road.getLength()
		
		if pos == 0 or pos == length:
			curr = idx1 if pos == 0 else idx2

			if curr in self.path.basesSequence:
				return curr

		return -1

class WalkingBack(WalkingPath):
	class Params(WalkingPath.Params):
		
		def __init__(self, path):
			self.path = path

	def __init__(self, params):
		WalkingPath.__init__(self, params)

		self.stateType = WalkerStateType.WALKING_BACK

class WalkingRoad(WalkerState):

	class Params(WalkerState.Params):
		
		def __init__(self, speed):
			self.speed = speed


	def __init__(self, owner, train, params):
		WalkerState.__init__(self, WalkerStateType.WALKING_ROAD, owner, train)

		self.speed   = params.speed
		self.roadIdx = train.getRoad().getIdx()


	def getAction(self):
		if train.getRoad().getIdx() != self.roadIdx:
			self.owner.pushState(Broken, None)
			action = self.owner.getAction()

		else:
			length = self.train.getRoad().getLength()
			limit  = length if self.speed == Speed.FORWARD else 0

			if self.train.getPosition() == limit:
				self.owner.popState()
				action = self.owner.getAction()

			else:
				action = (self.train.getRoad().getIdx(), self.speed, self.train.getIdx())

		return action


class Waiting(WalkerState):

	class Params(WalkerState.Params):
		
		def __init__(self, wait):
			self.wait  = wait


	def __init__(self, owner, train, params):
		WalkerState.__init__(self, WalkerStateType.WAITING, owner, train)

		self.wait  = params.wait


	def getAction(self):
		if self.wait > 0:
			self.wait  -= 1
			action = (self.train.getRoad().getIdx(), Speed.STOP, self.train.getIdx())

		else:
			self.owner.popState()
			action = self.owner.getAction()

		return action


class Broken(WalkerState):
	#Server lagged(or we are fucking stupid) so train is off the path
	#pathWalkers owner should fix this

	class Params(WalkerState.Params):
		pass

	def __init__(self, owner, train, params):

		WalkerState.__init__(self, WalkerStateType.BROKEN, owner, train)


	def getAction(self):
		
		return (self.train.getRoad().getIdx(), Speed.STOP, self.train.getIdx())


#pathwalker
class PathWalker:
	
	def __init__(self, owner, train):
		self.owner = owner
		self.train = train

		self.stateStack = [Idle(self, train, None)]


	def getAction(self):
		
		return self.stateStack[-1].getAction()


	def pushState(self, stateFactory, params):
		
		self.stateStack.append(stateFactory(self, self.train, params))

	def popState(self):
		if self.stateStack[-1].getType() != WalkerStateType.IDLE:
			del self.stateStack[-1]

	def peekState(self):
		
		return self.stateStack[-1]


	def flushStates(self):
		
		del self.stateStack[1 : ]


	def idle(self):

		return self.stateStack[-1].getType() == WalkerStateType.IDLE
	