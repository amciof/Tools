
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

	def __init__(self, msgDict):
		self.result = msgDict['result']
		self.length = msgDict['length']
		self.msg    = msgDict['msg']

#TODO
#all requests return token
#accepts outQueue
#puts to the outQueue tuple(token, response)

class Network:

	CHUNK_SIZE  = 4096

	RESULT_SIZE = 4
	LENGTH_SIZE = 4
	ACTION_SIZE = 4

	#for queue
	RESPONSE  = 0
	TERMINATE = 1


	def __init__(self, address, port):
		self.token  = 0
		self.sock   = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.buffer = io.BytesIO()

		try:
			self.sock.connect((address, port))
		except RuntimeError as re:
			print(re.msg)
	
	def __del__(self):

		self.sock.close()


	#requests
	def requestLogin(
		self
		, name
		, password
		, game       = None
		, numTurns   = None
		, numPlayers = None
	):
		action = b'\x01\x00\x00\x00'

		data   = {}

		data['name'] = name
		if not numPlayers is None:
			data['num_players'] = numPlayers
		if not game is None:
			data['game'] = game
		if not numTurns is None:
			data['num_turns']   = numTurns

		data   = json.dumps(data, separators=(',', ':')).encode('ascii')
		length = len(data).to_bytes(Network.LENGTH_SIZE, 'little')

		self.__sendRequest(action + length + data)

		return self.__getResponse()

	def requestLogout(self):
		action = b'\x02\x00\x00\x00'
		data   = b''
		length = b'\x00\x00\x00\x00'

		self.__sendRequest(action + length + data)
		
		return self.__getResponse()

	def requestMove(self, line_idx, speed, train_idx):
		action = b'\x03\x00\x00\x00'
		data   = {
			  'line_idx'  : line_idx
			, 'speed'     : speed
			, 'train_idx' : train_idx
		}
		data   = json.dumps(data, separators=(',', ':')).encode('ascii')
		length = len(data).to_bytes(Network.LENGTH_SIZE, 'little')

		self.__sendRequest(action + length + data)

		return self.__getResponse()

	def requestUpgrade(self, posts, trains):
		action = b'\x04\x00\x00\x00'
		data   = {
			  'posts'  : posts
			, 'trains' : trains
		}
		data   = json.dumps(data, separators=(',', ':')).encode('ascii')
		length = len(data).to_bytes(Network.LENGTH_SIZE, 'little')

		self.__sendRequest(action + length + data)

		return self.__getResponse()

	def requestTurn(self):
		action = b'\x05\x00\x00\x00'
		data   = b''
		length = b'\x00\x00\x00\x00'

		self.__sendRequest(action + length + data)

		return self.__getResponse()

	def requestPlayer(self):
		action = b'\x06\x00\x00\x00'
		data   = b''
		length = b'\x00\x00\x00\x00'

		self.__sendRequest(action + length + data)

		return self.__getResponse()

	def requestMap(self, layer):
		action = b'\n\x00\x00\x00'
		data   = json.dumps({'layer' : layer}, separators=(',', ':')).encode('ascii')
		length = len(data).to_bytes(Network.LENGTH_SIZE, 'little')

		self.__sendRequest(action + length + data)

		return self.__getResponse()

	def requestGames(self):
		action = b'\x07\x00\x00\x00'
		data   = b''
		length = b'\x00\x00\x00\x00'

		self.__sendRequest(action + length + data)

		return self.__getResponse()


	#generalised request
	def request(self, action, data):
		action = action.to_bytes(Network.ACTION_SIZE, 'little')

		if data is None:
			data = b''
		else:
			data = json.dumps(data, separators=(',', ':')).encode('ascii')

		length = len(data).to_bytes(Network.LENGTH_SIZE, 'little')

		self.__sendRequest(action + length + data)

		return self.__getResponse()

	
	#send whole msg(can be socket.sendall() instead)
	def __sendRequest(self, msg):
		totalsent = 0
		while totalsent < len(msg):
			sent = self.sock.send(msg[totalsent:])
			if sent == 0:
				raise RuntimeError("socket connection broken")
			totalsent += sent


	#get whole response(haven't found socket.recvall() yet)
	def __getResponse(self):

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

		return Response(respond)

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
