import socket
import struct

# Implementation Based on Valve Developer Community WIKI: https://developer.valvesoftware.com/wiki/Server_queries
# Catches the requests from Source Servers

# Debug prints:
DEBUG = 1

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
        self.dmsg("Return: ", result)

        if result == -1:
            result, data = struct.unpack('c', data[:1])[0], data[1:]
            print(result)
            if result == b"A":
                self.dmsg("challenge")
                self.dmsg(data)
                return self.challenge(data, Request)
                
            if result == b"I":
                self.dmsg("No Challenge")
                self.dmsg(data)
                return data
            
            if result == b"D":
                self.dmsg("infoplayer")
                self.dmsg(data)
                return data
            
            if result == b"E":
                self.dmsg("convars")
                self.dmsg(data)
                return data

        elif result == -2:
            self.dmsg("split response")

            response, rest = struct.unpack('l', data[:4])[0], data[4:]
            totalresponses, rest = struct.unpack('b', rest[:1])[0], rest[1:]
            currentresponse, rest = struct.unpack('b', rest[:1])[0], rest[1:] 
            responsesize, rest = struct.unpack('h', rest[:2])[0], rest[2:]

            print(response, totalresponses, currentresponse, responsesize)

            fullresponse = []
            fullresponse.append(rest)

            while totalresponses - currentresponse != 1:
                respBuf = self.connector.recv(65536) #self.receive("convars")
                result, data = struct.unpack('l', respBuf[:4])[0], respBuf[4:] 
                responseBuf, rest = struct.unpack('l', data[:4])[0], data[4:]
                if (result == -2) and (response == responseBuf):
                    totalresponses1, rest = struct.unpack('b', rest[:1])[0], rest[1:]
                    currentresponse, rest = struct.unpack('b', rest[:1])[0], rest[1:] 
                    responsesize, rest = struct.unpack('h', rest[:2])[0], rest[2:]

                    self.dmsg("RESPOND", result)
                    print(response, totalresponses1, totalresponses, currentresponse, responsesize)
                    fullresponse.append(rest)
                
            result = b''.join(fullresponse)
            self.dmsg(result)
            self.dmsg(result.split(b'\x00'))

            return fullresponse
    
    def challenge(self, data, Request):
        if Request == "info":
            self.connector.send(struct.pack('l', -1) + b"T" + b"Source Engine Query" + b'\x00' + data)
            self.dmsg("info")
            return self.receive("info")
        elif Request == "players":
            self.connector.send(struct.pack('l', -1) + b"U" + data)
            self.dmsg("players", data)
            return self.receive("players")
        elif Request == "convars":
            self.connector.send(struct.pack('l', -1) + b"V" + data)
            self.dmsg("convars", data)
            return self.receive("convars")
        
    def convars(self):
        self.connect()
        self.connector.send(struct.pack('l', -1) + b"V" + struct.pack('l', -1))
        return self.receive("convars")
        
        
    def players(self):
        self.connect()
        self.connector.send(struct.pack('l', -1) + b"U" + struct.pack('l', -1))
        data = self.receive("players")
        
        maxplayers, rest = struct.unpack('b', data[:1])[0], data[1:]
        
        players = []
        
        self.dmsg(maxplayers)
        
        for i in range(0, maxplayers):
            player = dict()
            player['idx'], rest = struct.unpack('b', rest[:1])[0], rest[1:]
            player['name'], rest = rest.split(b'\x00', 1)
            player['name'] = player['name'].decode()
            player['score'], rest = struct.unpack('i', rest[:4])[0], rest[4:]
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
        info['match'], rest = rest.split(b'\x00', 1)
        info['gamefolder'], rest = rest.split(b'\x00', 1)
        info['gamename'], rest = rest.split(b'\x00', 1)
        info['idgame'], rest = struct.unpack('h', rest[:2])[0], rest[2:]
        info['players'], rest = struct.unpack('b', rest[:1])[0], rest[1:]
        info['maxplayers'], rest = struct.unpack('b', rest[:1])[0], rest[1:]
        info['bots'], rest = struct.unpack('b', rest[:1])[0], rest[1:]
        info['servertype'], rest = struct.unpack('b', rest[:1])[0], rest[1:]
        info['os'], rest = struct.unpack('b', rest[:1])[0], rest[1:]
        info['visibility'], rest = struct.unpack('b', rest[:1])[0], rest[1:]
        info['vac'], rest = struct.unpack('b', rest[:1])[0], rest[1:]
        info['version'], rest = rest.split(b'\x00', 1)
        info['edf'], rest = struct.unpack('b', rest[:1])[0], rest[1:]
        
        if info['edf'] & 0x80:
            #short, gameport
            info['gameport'], rest = struct.unpack('h', rest[:2])[0], rest[2:]
        if info['edf'] & 0x10:
            #long long steamid
            info['steamid'], rest = struct.unpack('q', rest[:8])[0], rest[8:]
        if info['edf'] & 0x40:
            #sourcetv port:
            info['stv'], rest = struct.unpack('h', rest[:2]), rest[2:]
            info['stvname'], rest = rest.split(b'\x00', 1)
        if info['edf'] & 0x20:
            info['svtags'], rest = rest.split(b'\x00', 1)
        if info['edf'] & 0x01:
            info['gameid'], rest = struct.unpack('q', rest[:8])[0], rest[8:]


        for key, value in info.items():
            if isinstance(value, bytes):
                info[key] = value.decode()
            else:
                info[key] = value

        return info

    def dmsg(self, *args):
        # debug msgs:
        if DEBUG:
            print(*args)
