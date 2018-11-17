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

    action=b'\n\x00\x00\x00';
    msg =bytes(json.dumps(myDict, separators=(',', ':')), encoding='ascii')
    msg_length =len(json.dumps(myDict, separators=(',', ':'))).to_bytes(4, byteorder='little', signed=True)
    request = action + msg_length+ msg

    print(int.from_bytes(b'\n\x00\x00\x00', byteorder='little'))
    print(request)
    sock.send(request)

    action_request = sock.recv(4)
    print(action_request)
    length_message_bytes = sock.recv(4)
    print(length_message_bytes)
    length_message_int = int.from_bytes(length_message_bytes, byteorder='little')
    print(length_message_int)
    data = b''
    while length_message_int > len(data):
        packet = sock.recv(length_message_int - len(data));
        if not packet:
            break;
        data += packet
    print(data)

def playerRequest(sock):
    sock.send(b'\x06\x00\x00\x00\x00\x00\x00\x00')

    action_request = sock.recv(4)
    length_message_bytes = sock.recv(4)
    length_message_int = int.from_bytes(length_message_bytes, byteorder='little')
    data = b''

    while length_message_int > len(data):
        packet = sock.recv(length_message_int - len(data));
        if not packet:
            break;
        data += packet
    print(data)

def logoutRequest(sock):
    action = b'\x02\x00\x00\x00\x00\x00\x00\x00';
    sock.send(action)

    action_request = sock.recv(4)
    print(action_request)


def loginRequest(sock):
    myDict = {"name":""};
    myDict["name"] = input();

    action = b'\x01\x00\x00\x00'
    msg = bytes(json.dumps(myDict, separators=(',', ':')), encoding='ascii')
    msg_length= len(json.dumps(myDict, separators=(',', ':'))).to_bytes(4, byteorder='little', signed=True)

    request=action+msg_length+msg

    sock.send(request)

    action_request =sock.recv(4)
    length_message_bytes =sock.recv(4)
    length_message_int =int.from_bytes(length_message_bytes, byteorder='little')
    data = b''

    while length_message_int > len(data):
        packet = sock.recv(length_message_int-len(data));
        if not packet:
            break;
        data += packet
    print(data)

def main():
    SERVER_ADDR = 'wgforge-srv.wargaming.net'
    SERVER_PORT = 443

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((SERVER_ADDR, SERVER_PORT))
    except (sock.error, msg):
        print("Couldnt connect with the socket-server: %s\n terminating program" % msg)
        sys.exit(1)



    loginRequest(sock)
    playerRequest(sock)
    mapRequest(sock)
    logoutRequest(sock)
    sock.close()

if __name__ == '__main__':
    main()