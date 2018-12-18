
import io
import socket
import json

from threading import Thread
from queue     import Queue


class Action:
	LOGIN   = 1
	LOGOUT  = 2
	MOVE    = 3
	UPGRADE = 4
	TURN    = 5
	PLAYER  = 6
	GAMES   = 7
	MAP     = 10

class Result:
	OKEY                  = 0
	BAD_COMMAND           = 1
	RESOURCE_NOT_FOUND    = 2
	ACCESS_DENIED         = 3
	NOT_READY             = 4
	TIMEOUT               = 5
	INTERNAL_SERVER_ERROR = 500

class Options:
	LAYER_0 = 0
	LAYER_1 = 1

class GameState:
	INIT     = 1
	RUN      = 2
	FINISHED = 3


class Response:

	def __init__(self, action, msgDict):
		self.action = action
		self.result = msgDict['result']
		self.length = msgDict['length']
		self.msg    = msgDict['msg']

class Request:

	def __init__(self, token, action, data):
		self.token  = token
		self.action = action
		self.data   = data


#TODO
#all requests return token
#accepts outQueue
#puts to the outQueue tuple(token, response)

class Network(Thread):

	CHUNK_SIZE  = 4096

	RESULT_SIZE = 4
	LENGTH_SIZE = 4
	ACTION_SIZE = 4

	#for queue
	REQUEST   = 0
	TERMINATE = 1


	def __init__(self, address, port):
		Thread.__init__(self)

		self.token  = 0
		self.sock   = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.buffer = io.BytesIO()
		self.taskQueue = Queue()

		try:
			self.sock.connect((address, port))
		except RuntimeError as re:
			print(re.msg)

		self.log = open('log.txt', 'w')
	
	def __del__(self):
		self.log.close()
		self.sock.close()


	#thread method
	def run(self):
		while True:
			type, outQueue, request = self.taskQueue.get(True)

			if type == Network.REQUEST:
				self.log.write('%i request polled\n' % (request.token))
				response = self.__request(request.action, request.data)

				self.log.write('%i response got\n' % (request.token))
				outQueue.put((request.token, response))

			elif type == Network.TERMINATE:
				self.log.write('Terminating network\n')
				break

		self.__del__()

	def terminate(self):

		self.taskQueue.put((Network.TERMINATE, None, None))


	#requests
	def requestLogin(
		self
		, outQueue
		, name
		, password
		, game       = None
		, numTurns   = None
		, numPlayers = None
	):
		data   = {}

		data['name'] = name
		if not numPlayers is None:
			data['num_players'] = numPlayers
		if not game is None:
			data['game'] = game
		if not numTurns is None:
			data['num_turns']   = numTurns

		token = self.__getToken()
		request = Request(token, Action.LOGIN, data)
		self.taskQueue.put((Network.REQUEST, outQueue, request))

		return token

	def requestLogout(self, outQueue):
		token = self.__getToken()
		request = Request(token, Action.LOGOUT, None)
		self.taskQueue.put((Network.REQUEST, outQueue, request))

		return token

	def requestMove(self, outQueue, line_idx, speed, train_idx):
		data   = {
			  'line_idx'  : line_idx
			, 'speed'     : speed
			, 'train_idx' : train_idx
		}

		token   = self.__getToken()
		request = Request(token, Action.MOVE, data)
		self.taskQueue.put((Network.REQUEST, outQueue, request))

		return token

	def requestUpgrade(self, outQueue, posts, trains):
		data   = {
			  'posts'  : posts
			, 'trains' : trains
		}

		token   = self.__getToken()
		request = Request(token, Action.UPGRADE, data)
		self.taskQueue.put((Network.REQUEST, outQueue, request))

		return token

	def requestTurn(self, outQueue):
		token   = self.__getToken()
		request = Request(token, Action.TURN, None)
		self.taskQueue.put((Network.REQUEST, outQueue, request))

		return token

	def requestPlayer(self, outQueue):
		token   = self.__getToken()
		request = Request(token, Action.PLAYER, None)
		self.taskQueue.put((Network.REQUEST, outQueue, request))

		return token

	def requestMap(self, outQueue, layer):
		data   = {'layer' : layer}

		token   = self.__getToken()
		request = Request(token, Action.MAP, data)
		self.taskQueue.put((Network.REQUEST, outQueue, request))

		return token

	def requestGames(self, outQueue):
		token   = self.__getToken()
		request = Request(token, Action.GAMES, None)
		self.taskQueue.put((Network.REQUEST, outQueue, request))

		return token


	#private
	def __getToken(self):
		token = self.token
		self.token += 1

		return token


	#generalised request
	def __request(self, action, data):
		temp = action

		action = action.to_bytes(Network.ACTION_SIZE, 'little')

		if data is None:
			data = b''
		else:
			data = json.dumps(data, separators=(',', ':')).encode('ascii')

		length = len(data).to_bytes(Network.LENGTH_SIZE, 'little')

		self.__sendRequest(action + length + data)

		return self.__getResponse(temp)
	
	#send whole msg(can be socket.sendall() instead)
	def __sendRequest(self, msg):
		totalsent = 0
		while totalsent < len(msg):
			sent = self.sock.send(msg[totalsent:])
			if sent == 0:
				raise RuntimeError("socket connection broken")
			totalsent += sent


	#get whole response(haven't found socket.recvall() yet)
	def __getResponse(self, action):

		respond = {}

		result = self.__getWholeMsg(Network.RESULT_SIZE)
		result = int.from_bytes(result, 'little')

		respond['result'] = result

		length = self.__getWholeMsg(Network.LENGTH_SIZE)
		length = int.from_bytes(length, 'little')

		respond['length'] = length

		msg = self.__getWholeMsg(length)

		if msg != b'':
			msg = json.loads(msg.decode('ascii'))
		
		respond['msg'] = msg

		return Response(action, respond)

	def __getWholeMsg(self, msgLen):

		bytes_got = 0
		while bytes_got < msgLen:

			chunk = self.sock.recv(min(msgLen - bytes_got, Network.CHUNK_SIZE))
			if chunk == b'':
				raise RuntimeError("socket connection broken")

			self.buffer.write(chunk)
			bytes_got += len(chunk)

		self.buffer.seek(0, io.SEEK_SET)
		msg = self.buffer.read(msgLen)
		self.buffer.seek(0, io.SEEK_SET)

		return msg



if __name__ == '__main__':
	net = Network('wgforge-srv.wargaming.net', 443)

	login  = net.requestLogin('Pingas')
	map0   = net.requestMap(Options.LAYER_0)
	map1   = net.requestMap(Options.LAYER_1)
	player = net.requestPlayer()

	with open('../Watch/Login.txt', 'w') as login_info:
		json.dump(login.msg, login_info, indent='    ')

	with open('../Watch/Map0.txt', 'w') as map0_info:
		json.dump(map0.msg, map0_info, indent='    ')

	with open('../Watch/Map1.txt', 'w') as map1_info:
		json.dump(map1.msg, map1_info, indent='    ')

	with open('../Watch/Player.txt', 'w') as player_info:
		json.dump(player.msg, player_info, indent='    ')
