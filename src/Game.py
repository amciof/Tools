
from Networking import Network, Action, Options
from Scene      import Scene
from Player     import Player

from PyQt5.QtGui  import QPainter


class Game:
	
	EVENT_MOUSE_PRESS = 2
	EVENT_PAINT       = 12

	##init section
	def __init__(self, serverAddr, portNum, playerName, viewport):
		##network init
		self.net = Network(serverAddr, portNum)

		##basic requests
		playerResp = self.net.requestLogin(playerName)
		mapResp    = self.net.requestMap(Options.LAYER_0)

		##map
		self.scene = Scene(playerResp.msg, mapResp.msg, viewport)
		
		##player
		self.player = Player(playerResp.msg)

		##state params
		self.selectedTrain = None


	##events
	#update logic(main method)
	def update(self, event, dt):
		if event.type() == Game.EVENT_MOUSE_PRESS:
			self.handleMousePress(event)
		elif event.type() == Game.EVENT_PAINT:
			self.render()


	#render
	def render(self):
		self.scene.renderScene()


	#mouse handlers
	def handleMouseMove(self):
		pass

	def handleMouseRelease(self):
		pass

	def handleMousePress(self, event):
		pass

	#key handlers
	def handleKeyPress(self):
		pass

	def handleKeyRelease(self):
		pass
