
import io
import socket
import json


class Action:
	LOGIN   = 1
	LOGOUT  = 2
	MOVE    = 3
	UPGRADE = 4
	TURN    = 5
	PLAYER  = 6
	MAP     = 10

class Result:
	OKEY                  = 0
	BAD_COMMAND           = 1
	RESOURCE_NOT_FOUND    = 2
	ACCESS_DENIED         = 3
	NOT_READY             = 4
	TIMEOUT               = 5
	INTERNAL_SERVER_ERROR = 500

class Network:

	CHUNK_SIZE  = 4096
	RESULT_SIZE = 4
	LENGTH_SIZE = 4

	def __init__(self, address, port):

		self.sock   = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.buffer = io.BytesIO()

		try:
			self.sock.connect((address, port))
		except RuntimeError as re:
			print(re.msg)
	
	def __del__(self):

		self.sock.close()


	#Requests
	def requestLogin(self, name):
		action = b'\x01\x00\x00\x00'
		data   = {'name' : name}
		data   = json.dumps(data, separators=(',', ':')).encode('ascii')
		length = len(data).to_bytes(Network.LENGTH_SIZE, 'little')

		self.sendRequest(action + length + data)

		return self.getResponse()

	def requestLogout(self):
		action = b'\x02\x00\x00\x00'
		data   = b''
		length = b'\x00\x00\x00\x00'

		self.sendRequest(action + length + data)
		
		return self.getResponse()

	def requestMove(self, line_idx, speed, train_idx):
		action = b'\x03\x00\x00\x00'
		data   = {
			'line_idx'  : line_idx
			, 'speed'     : speed
			, 'train_idx' : train_idx
		}
		data   = json.dumps(data, separators=(',', ':')).encode('ascii')
		length = len(data).to_bytes(Network.LENGTH_SIZE, 'little')

		self.sendRequest(action + length + data)

		return self.getResponse()

	def requestUpgrade(self):

		pass

	def requestTurn(self):
		action = b'\x05\x00\x00\x00'
		data   = b''
		length = b'\x00\x00\x00\x00'

		self.sendRequest(action + length + data)

		return self.getResponse()

	def requestPlayer(self):
		action = b'\x06\x00\x00\x00'
		data   = b''
		length = b'\x00\x00\x00\x00'

		self.sendRequest(action + length + data)

		return self.getResponse()

	def requestMap(self, layer):
		action = b'\n\x00\x00\x00'
		data   = json.dumps({'layer' : layer}, separators=(',', ':')).encode('ascii')
		length = len(data).to_bytes(Network.LENGTH_SIZE, 'little')

		self.sendRequest(action + length + data)

		return self.getResponse()


	#send request
	def sendRequest(self, msg):
		totalsent = 0
		while totalsent < len(msg):
			sent = self.sock.send(msg[totalsent:])
			if sent == 0:
				raise RuntimeError("socket connection broken")
			totalsent += sent

	#get response
	def getResponse(self):

		respond = {}

		result = self.getWholeMsg(Network.RESULT_SIZE)
		result = int.from_bytes(result, 'little')

		respond['result'] = result

		length = self.getWholeMsg(Network.LENGTH_SIZE)
		length = int.from_bytes(length, 'little')

		respond['length'] = length

		msg = self.getWholeMsg(length)
		msg = json.loads(msg.decode('ascii'))
		
		respond['msg'] = msg

		return respond

	def getWholeMsg(self, msgLen):

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
	login = net.requestLogin('Pingas')
	map0   = net.requestMap(0)
	map1   = net.requestMap(1)

	print(login)
	print()
	print(map0)
	print()
	print(map1)
	print()
