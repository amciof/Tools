
from .Networking import Network, Action, Options
from .Map        import Map
from .Player     import Player, Train


class Game:
	
	##init section
	def __init__(self, serverAddr, portNum, playerName):
		##network init
		self.net = Network(serverAddr, portNum)

		##map init
		self.map = None #Map(jsonLogin, jsonMap) 

		##player init
		self.player = None #Player(jsonLogin)


	##controller interface
	#mouse
	def handleMouseMove(self):
		pass

	def handleMouseRelease(self):
		pass

	def handleMousePress(self):
		pass
	
	#key
	def handleKeyPress(self):
		pass

	def handleKeyRelease(self):
		pass