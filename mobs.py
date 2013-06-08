import time, random, threading, math

import globals


idcharacters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def generate_id():
	global idcharacters
	
	id = ""
	
	for i in range(10):
		id += random.choice( idcharacters )
		
	return id
	
troutpopulation = 0
	
class Spawner( threading.Thread ):
	def run ( self ):
		time.sleep(2)
		
		dt = 5
		while True:
		
			if troutpopulation < len( globals.clients.values() )*5:
				Trout().start()
				
			time.sleep(dt)
			
class Trout( threading.Thread ):
	def run ( self ):
		global troutpopulation
		
		troutpopulation += 1
		
		self.id = generate_id()
		
		print "Spawned Trout " + self.id
		
		self.person = random.choice( globals.clients.values() )
		
		angle = random.uniform(0.0, 6.28)
		radius = 100
		
		self.pos = [float(self.person.pos[0]) + radius*math.sin(angle), random.uniform(0.0, -80), float(self.person.pos[2]) + radius*math.cos(angle)]
		self.vel = [0, 0, 0]
		self.acc = [0, 0, 0]
		
		self.yaw = 0
		
		self.state = "idle"
		
		
		dt = 0.25
		
		while True:
		
			canlive = False
			
			#if you are within the radius of at least somebody, then you can live
			for dest in globals.clients.values():
				dist = math.sqrt( math.pow(self.pos[0] - float(dest.pos[0]), 2 ) + 
					#math.pow(self.pos[2] - float(dest.pos[2]), 2 ) +
					math.pow(self.pos[2] - float(dest.pos[2]), 2 ) )
					
				if  dist < 400:
					canlive = True
			
			
			if canlive == False:
				print "Despawning Trout " + self.id
				break
				
			mindist = None
			
			for dest in globals.clients.values():
				dist = math.sqrt( math.pow(self.pos[0] - float(dest.pos[0]), 2 ) + 
					math.pow(self.pos[2] - float(dest.pos[2]), 2 ) +
					math.pow(self.pos[2] - float(dest.pos[2]), 2 ) )
					
				if mindist == None or mindist > dist:
					mindist = dist
					
			self.vel[0] += self.acc[0]*dt
			self.vel[1] += self.acc[1]*dt
			self.vel[2] += self.acc[2]*dt
			
			self.pos[0] += self.vel[0]*dt
			self.pos[1] += self.vel[1]*dt
			self.pos[2] += self.vel[2]*dt
			
			#Behavior
			if self.state == "idle":
				self.vel[0] = 20*math.sin(self.yaw)
				self.vel[2] = 20*math.cos(self.yaw)
				
				self.yaw += dt*0.3
				
				if mindist < 50:
					self.state = "scared"
			if self.state == "scared":
				self.vel[0] = 60*math.sin(self.yaw)
				self.vel[2] = 60*math.cos(self.yaw)
				
				if mindist > 100:
					self.state = "idle"
			
			relay = "mob " + self.id
			relay += " " + str(self.pos[0]) + " " + str(self.pos[1]) + " " + str(self.pos[2])
			relay += " " + str(self.vel[0]) + " " + str(self.vel[1]) + " " + str(self.vel[2])
			relay += " " + str(self.acc[0]) + " " + str(self.acc[1]) + " " + str(self.acc[2])
			
			relay += " " + str(self.yaw)
			
			for dest in globals.clients.values():
				if dest.udphost != None and dest.udpport != None:
					globals.gameudp.transport.write(relay, (dest.udphost, dest.udpport))
					
			time.sleep(dt)
			
		troutpopulation -= 1