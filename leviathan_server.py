from twisted.internet import reactor, protocol
from twisted.protocols import basic

from twisted.internet.protocol import DatagramProtocol

import mobs

import globals

import os

SERVER_PORT_TCP = 1025
SERVER_PORT_UDP = 1026

CLIENT_PORT_UDP = 54000

class Client:
	def __init__(self, tcpprotocol):
		self.tcpprotocol = tcpprotocol
		
		self.udphost = None
		self.udpport = None
		
		self.id = None
		
		self.pos = [0,0,0]
		self.vel = [0,0,0]
		self.acc = [0,0,0]
		
		self.yaw = 0
		


class GameProtocol(basic.LineReceiver):
	def __init__(self, factory):
		self.factory = factory
		self.client = None
		
	def connectionMade(self):
		self.client = Client(self)
		self.client.tcp = self.transport.getPeer()
		
		print "Added client " + self.client.tcp.host + ":" + str(self.client.tcp.port)
		#self.sendLine( self.transport.getHost() )
		

	def connectionLost(self, reason):
		if self.client != None and self.client.id != None:
			del globals.clients[self.client.id]
		print "Lost a connection " + self.client.tcp.host + ":" + str(self.client.tcp.port)

	def lineReceived(self, line):
		print line
		
		words = line.split()
		
		if len(words) > 0:
			if len(words) > 1:
				pass
			else:
				self.client.id = words[0]
				globals.clients[ self.client.id ] = self.client
				print "Set ID of a client to " + self.client.id
			
		#for c in self.factory.clients:
		#	c.sendLine("<{}> {}".format(self.transport.getHost(), line))

class GameFactory(protocol.Factory):
	def __init__(self):
		pass

	def buildProtocol(self, addr):
		return GameProtocol(self)
		
def getClient(host, port):
	for client in globals.clients.values():
		if client.udphost != None and client.udpport != None:
			if client.udphost == host and client.udpport == port:
				return client
	return None
		
class GameUDP(DatagramProtocol):
    def datagramReceived(self, data, (host, port)):
		words = data.split()
		if len(words) > 0:
			if len(words) > 1:
				if words[0] == "motion":
					client = getClient(host, port)
					if client != None:
						client.pos[0] = words[1]
						client.pos[1] = words[2]
						client.pos[2] = words[3]
						
						client.vel[0] = words[4]
						client.vel[1] = words[5]
						client.vel[2] = words[6]
						
						client.acc[0] = words[7]
						client.acc[1] = words[8]
						client.acc[2] = words[9]
						
						client.yaw = words[10]
						
						relay = "divermotion " + client.id
						relay += " " + client.pos[0] + " " + client.pos[1] + " " + client.pos[2]
						relay += " " + client.vel[0] + " " + client.vel[1] + " " + client.vel[2]
						relay += " " + client.acc[0] + " " + client.acc[1] + " " + client.acc[2]
						
						relay += " " + client.yaw
						
						for dest in globals.clients.values():
							if dest.udphost != None and dest.udpport != None:
								self.transport.write(relay, (dest.udphost, dest.udpport))
				if words[0] == "arrow":
					for dest in globals.clients.values():
							if dest.udphost != None and dest.udpport != None:
								self.transport.write(data, (dest.udphost, dest.udpport))
			else:
				id = words[0]
				
				if id in globals.clients.keys():
					globals.clients[id].udphost = host
					globals.clients[id].udpport = port
					print "Associated a UDP location with a client " + id
				
		#print "received %r from %s:%d" % (data, host, port)

gamefactory = GameFactory()

globals.gameudp = GameUDP()

reactor.listenTCP(1025, gamefactory)
reactor.listenUDP(1026, globals.gameudp)

mobs.Spawner().start()

reactor.run()

os._exit(0)