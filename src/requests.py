import socket
import json
from enum import Enum

class Action(Enum):
    LOGIN = 1,
    LOGOUT = 2,
    MOVE = 3,
    UPGRADE = 4,
    TURN = 5,
    PLAYER = 6,
    MAP = 10



def mapRequest(sock):
    myDict = {"layer": 0};
    myDict["layer"] = int(input());
    request = b'\x02\x00\x00\x00\x0b\x00\x00\x00' + bytes(json.dumps(myDict, separators=(',', ':')), encoding='ascii')
    sock.send(request)
    data = sock.recv(1024)
    print(data)  # .decode('utf-8'))

def playerRequest(sock):
    sock.send(b'\x06\x00\x00\x00\x00\x00\x00\x00')
    data = sock.recv(1024)
    print(data.decode('utf-8'))

def loginRequest(sock):
    myDict = {"name":""};
    myDict["name"] = input();
    request=b'\x01\x00\x00\x00\x10\x00\x00\x00'+bytes(json.dumps(myDict, separators=(',', ':')), encoding='ascii')
    sock.send(request)
    data = sock.recv(1024)

   # import io
   # data  = io.BytesIO()
    #chunk = sock.recv(1024)

    #data.seek(0)
    #res, length =
    #data.write(chunk)

    #chunk = sock.recv(1024)
    print(data)#.decode('utf-8'))

def main():
    SERVER_ADDR = 'wgforge-srv.wargaming.net'
    SERVER_PORT = 443
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect((SERVER_ADDR, SERVER_PORT))
  #  sock.setblocking(0)
    loginRequest(sock)
    mapRequest(sock)
    sock.close()

if __name__ == '__main__':
    main()