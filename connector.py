import socket
import struct

# Based on Valve Developer Community WIKI: https://developer.valvesoftware.com/wiki/Server_queries

class Querier:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        
    def connect(self):
        self.connector = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.connector.connect((self.ip, self.port))
    
    def receive(self, Request):
        received = self.connector.recv(65536)
        result, data = struct.unpack('l', received[:4])[0], received[4:] 
        print("Result", result)

        if (result == -1):
            result, data = struct.unpack('c', data[:1])[0], data[1:]
            print(result)
            if (result == b"A"):
                print("challenge")
                print(data)
                return self.challenge(data, Request)
                
            if (result == b"I"):
                print("No Challenge")
                print(data)
                return data
            
            if (result == b"D"):
                print("infoplayer")
                print(data)
                return data
    
    def challenge(self, data, Request):
        if (Request == "info"):
            self.connector.send(struct.pack('l', -1) + b"T" + b"Source Engine Query" + b'\x00' + data)
            print("info")
            return self.receive("info")
        elif (Request == "players"):
            self.connector.send(struct.pack('l', -1) + b"U" + data)
            print("players", data)
            return self.receive("players")
        elif (Request == "convars"):
            self.connector.send(struct.pack('l', -1) + b"V" + data)
            print("convars", data)
            return self.receive("convars")
        
    def convars(self):
        pass
        # furtehr to be established, convars are multi-packeted
#         self.connect()
#         self.connector.send(struct.pack('l', -1) + b"V" + struct.pack('l', -1))
#         data = self.receive("convars")
        
#         print(data)
        
        
    def players(self):
        self.connect()
        self.connector.send(struct.pack('l', -1) + b"U" + struct.pack('l', -1))
        data = self.receive("players")
        
        maxplayers, rest = struct.unpack('b', data[:1])[0], data[1:]
        
        players = []
        
        print(maxplayers)
        
        for i in range(0, maxplayers):
            player = dict()
            player['idx'], rest = struct.unpack('b', rest[:1])[0], rest[1:]
            player['name'], rest = rest.split(b'\x00', 1)
            player['name'] = player['name'].decode()
            player['score'], rest = struct.unpack('l', rest[:4])[0], rest[4:]
            player['duration'], rest = struct.unpack('f', rest[:4])[0], rest[4:] 
            players.append(player)
        
        print(players)
        return players
            
        
    def info(self):
        self.connect()
        self.connector.send(struct.pack('l', -1) + b"T" + b"Source Engine Query" + b'\x00')
        data = self.receive("info")
        
        info = dict()
        
        info['protocol'], rest = struct.unpack('b', data[:1])[0], data[1:]
        info['hostname'], rest = rest.split(b'\x00', 1)
        info['matching'], rest = rest.split(b'\x00', 1)
        info['gamefolder'], rest = rest.split(b'\x00', 1)
        info['gamename'], rest = rest.split(b'\x00', 1)
        info['idgame'], rest = struct.unpack('h', rest[:2]), rest[2:]
        info['players'], rest = struct.unpack('b', rest[:1]), rest[1:]
        info['maxplayers'], rest = struct.unpack('b', rest[:1]), rest[1:]
        info['bots'], rest = struct.unpack('b', rest[:1]), rest[1:]
        info['servertype'], rest = struct.unpack('b', rest[:1]), rest[1:]
        info['os'], rest = struct.unpack('b', rest[:1]), rest[1:]
        info['visibility'], rest = struct.unpack('b', rest[:1]), rest[1:]
        info['vac'], rest = struct.unpack('b', rest[:1]), rest[1:]
        info['version'], rest = rest.split(b'\x00', 1)
        info['edf'], rest = struct.unpack('b', rest[:1]), rest[1:]
        
        if info['edf'][0] & 0x80:
            #short, gameport
            info['gameport'], rest = struct.unpack('h', rest[:2]), rest[2:]
        if info['edf'][0] & 0x10:
            #long long steamid
            info['gameport'], rest = struct.unpack('q', rest[:8]), rest[8:]
        if info['edf'][0] & 0x40:
            #sourcetv port:
            info['stv'], rest = struct.unpack('h', rest[:2]), rest[2:]
            info['stvname'], rest = rest.split(b'\x00', 1)
        if info['edf'][0] & 0x20:
            info['svtags'], rest = rest.split(b'\x00', 1)
        if info['edf'][0] & 0x01:
            info['gameid'], rest = struct.unpack('q', rest[:8]), rest[8:]
        
        return info


        
