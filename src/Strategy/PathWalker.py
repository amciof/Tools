
import sys
sys.path.append('../')


from Game.GameElements import Speed


#path struct
class Path:

	D_INDEX = 0 #path.roadsDict[roadIdx][0] -> path.roadsDict[roadIdx][Path.D_INDEX]
	D_SPEED = 1 #path.roadsDict[roadIdx][1] -> path.roadsDict[roadIdx][Path.D_SPEED]

	L_ROAD  = 0 #path.roadsList[index][0] -> path.roadsDict[index][Path.L_ROAD]
	L_SPEED = 1 #path.roadsList[index][0] -> path.roadsDict[index][Path.L_SPEED]

	#start  -> path start
	#end    -> path end
	#roadsDict -> dict of (key: roadIdx, value: tuple(i_list, speed))
	#roadsList -> list of tuples(roadIdx, speed)
	#length -> path length

	def __init__(self, start, end, length, roadsList, roadsDict):
		self.start  = start
		self.end    = end

		self.length = length

		self.roadsDict = roadsDict
		self.roadsList = roadsList


	def getReversed(self):
		roadsList = [
			(road, -speed) for road, speed in reversed(self.roadsList)
		]
		roadsDict = {
			elem[Path.L_ROAD] : (i, -elem[Path.SPEED]) for i, elem in enumerate(roadsList)
		}
		
		return Path(self.end, self.start, self.length, roadsList, roadsDict)


#states
class StateType:
	IDLE = 0

	WALKING_PATH = 1
	WALKING_ROAD = 2

	WAITING = 3

	BROKEN  = -1

class State:

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


class Idle(State):

	def __init__(self, owner, train):

		State.__init__(self, StateType.IDLE, owner, train)	


	def getAction(self):
		
		return (self.train.getRoad().getIdx(), Speed.STOP, self.train.getIdx())


class WalkingPath(State):

	def __init__(self, owner, train, path):
		State.__init__(self, StateType.WALKING_PATH, owner, train)
		
		self.path  = path

	
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
			self.owner.pushState(Broken(self.owner, self.train))

			action = self.owner.getAction()

		return action


class WalkingRoad(State):

	def __init__(self, owner, train, speed):
		State.__init__(self, StateType.WALKING_ROAD, owner, train)

		self.speed   = speed
		self.roadIdx = train.getRoad().getIdx()


	def getAction(self):
		if train.getRoad().getIdx() != self.roadIdx:
			self.owner.pushState(Broken(self.owner, self.train))
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


class Waiting(State):

	def __init__(self, owner, train, wait):
		State.__init__(self, StateType.WAITING, owner)

		self.train = train
		self.wait  = wait


	def getAction(self):
		if wait > 0:
			wait  -= 1
			action = (self.train.getRoad().getIdx(), Speed.STOP, self.train.getIdx())

		else:
			self.owner.popState()
			action = self.owner.getAction()

		return action


class Broken(State):

	def __init__(self, owner, train):
		State.__init__(self, StateType.BROKEN, owner)

		self.train = train


	def getAction(self):
		
		return (self.train.getRoad().getIdx(), Speed.STOP, self.train.getIdx())


#pathwalker
class PathWalker:
	
	def __init__(self, owner, train):
		self.owner = owner

		self.stateStack = [Idle(self, train)]


	def getAction(self):
		
		return self.stateStack[-1].getAction()


	def pushState(self, state):
		
		self.stateStack.append(state)

	def popState(self):
		if self.stateStack[-1].getType() != StateType.IDLE:
			del self.stateStack[-1]

	def peekState(self):
		
		return self.stateStack[-1]


	def flushStates(self):
		
		del self.stateStack[1 : ]
	