from math import sin, tau
from socket import *
import urllib.request, urllib.error
from threading import Thread
import pygame; pygame.init()
import pymunk
from pymunk import pygame_util, Vec2d
pymunk.pygame_util.positive_y_is_up = False

class Online:

	def __init__(self, ip):
		self.ip = ip
		self.addr = self.addr = (self.ip, 3301)
		self.decoder = DecodingMessage()
		self.ID = 0

	def connection(self, name):
		self.udp_socket = socket(AF_INET, SOCK_DGRAM)
		print("Accept to Server: ", self.addr)

		self.send(name)

		# Get ID
		message = self.udp_socket.recv(1024).decode()
		self.ID = int(message)
		print(f"Мой уникальный Id: {self.ID}")

	def send(self, message):
		self.udp_socket.sendto(message.encode(), self.addr)

	def receiving_message(self):
		return self.decoder.get(self.udp_socket.recv(1024).decode())
			
class DecodingMessage:

	def __init__(self):
		self.status = "wait"
		self.long_txt = ""

		self.join_status = False

		self.message = []

	def get(self, message_txt):

		message_list = message_txt.split()

		message = []

		for txt in message_list:

			if txt == "l":
				self.join_status = False

				if self.long_txt[0] != "(":
					self.long_txt = self.long_txt[5:]

				msg = ("l", eval(self.long_txt))
				message.append(msg)
			
				self.long_txt = ""
				
			elif txt == "z":
				self.join_status = False

				msg = ["score", eval(self.long_txt)]
				msg[1] = f"{msg[1][0]}       {msg[1][1]}"
				message.append(msg)

				self.long_txt = ""
			
			elif txt == "q":
				self.join_status = False

				

				msg = ["quit", eval(self.long_txt)]
				message.append(msg)

				print("Удалил", self.long_txt)

				self.long_txt = ""

			elif txt == "|":
				self.join_status = True

			else:
				self.long_txt += txt

		return message

class Player:
	
	def __init__(self, coord):
		self.coord = coord

		self.speed = 5

		self.skin = "a"

		self.old_velocity = [0, 0]

		self.key_w = False
		self.key_a = False
		self.key_s = False
		self.key_d = False

	def draw(self, screen):
		pygame.draw.circle(screen, (255, 255, 255), self.coord, 30)

	def edit_velocity(self, x, y):
		self.old_velocity = [x, y]
		self.body.velocity = [x, y]
		

	def create_ball(self, space):
		mass = 100
		radius = 20
		inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))

		self.body = pymunk.Body(mass, inertia)
		self.body.position = self.coord
		self.shape = pymunk.Circle(self.body, radius) 
		self.shape.mass = 100
		self.shape.friction = 2
		self.shape.elasticity = 0.95
		self.shape.friction = 0.9
		self.shape.collision_type = 1

		space.add(self.body, self.shape)
	
	def animation(self):
		pass
		

class Objects:


	def __init__(self, images, online, font):
		self.images = images
		self.online = online
		self.font = font
		self.objects = {}


		self.space = pymunk.Space()
		self.space.gravity = 0, 0

		sides = (
			pymunk.Segment(self.space.static_body, (0, 0), (900, 0), 15),
			pymunk.Segment(self.space.static_body, (0, 498), (900, 498), 15),
			pymunk.Segment(self.space.static_body, (0, 0), (0, 500), 15),
			pymunk.Segment(self.space.static_body, (900, 0), (900, 500), 15),

			pymunk.Segment(self.space.static_body, (0, 171), (115, 171), 15),
			pymunk.Segment(self.space.static_body, (0, 336), (115, 336), 15),
			pymunk.Segment(self.space.static_body, (760, 171), (900, 171), 15),
			pymunk.Segment(self.space.static_body, (760, 336), (900, 336), 15)
		)

		for i in sides:
			i.elasticity = 0.4
			i.friction = 1.0
			self.space.add(i)

		# мячик
		mass = 1
		radius = 10
		inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
		self.body = pymunk.Body(mass, inertia)
		self.body.position = (900 / 2, 500 / 2)
		self.shape = pymunk.Circle(self.body, 10, (0, 0))
		self.shape.mass = 0.1
		self.shape.elasticity = 0.95
		self.shape.friction = 0.9
		self.space.add(self.body, self.shape)

		self.space_add_player = []
		self.space_remove_player = []
		self.score = pygame.Surface((0, 0))
		self.score_tick = .0

		self.sound_ball = pygame.mixer.Sound("ball.mp3")
		self.sound_ball.set_volume(0.2)

		self.connect = True

		self.old_velocity_ball = (self.body.velocity.x, self.body.velocity.y)

		th = Thread(target=self.update)
		th.daemon = True
		th.start()

	def add_player(self, x, y, skin):
		mass = 100
		radius = 20
		inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))

		body = pymunk.Body(mass, inertia)
		body.position = x, y
		shape = pymunk.Circle(self.body, radius) 
		shape.mass = 100
		shape.friction = 2
		shape.elasticity = 0.95
		shape.friction = 0.9
		shape.collision_type = 1
		self.space.add(self.body, self.shape)

	def add_ball(self, x, y):
		mass = 1
		radius = 10
		inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
		body = pymunk.Body(mass, inertia)
		body.position = x, y
		shape = pymunk.Circle(body, 10, (0, 0))
		shape.mass = 0.1
		shape.elasticity = 0.95
		shape.friction = 0.9
		self.space.add(body, shape)

	def draw(self, screen):

		# счет
		screen.blit(self.score, self.score.get_rect(center=(450, 55 + sin(self.score_tick) * 5)))
		self.score_tick = (self.score_tick + 0.05) % tau

		# мяч
		img = pygame.transform.rotate(self.images["m"], -self.body.angle * 20)
		screen.blit(img, img.get_rect(center=(self.body.position)))

		for conn in self.objects:
			pl = self.objects[conn]
			
			x, y = pl.body.position
			skin = pl.skin
			angle = pl.body.angle

			img = pygame.transform.rotate(self.images[skin], -angle * 40)
			screen.blit(img, img.get_rect(center=(x, y)))
		
	def animation(self):


		for data in self.space_add_player:
			pl, speed_x, speed_y, angle, conn = data
			pl.create_ball(self.space)
			pl.edit_velocity(speed_x, speed_y)
			pl.body.angle = angle
			self.objects[conn] = pl

			self.space_add_player.remove(data)

		for addr in self.space_remove_player:
			self.objects.pop(addr)
			self.space_remove_player.remove(addr)

		for key in self.objects:
			obj = self.objects[key]
			obj.edit_velocity(obj.old_velocity[0], obj.old_velocity[1])

		if self.old_velocity_ball != (self.body.velocity.x, self.body.velocity.y):
			self.old_velocity_ball = (self.body.velocity.x, self.body.velocity.y)
			self.sound_ball.play()

		self.space.step(1 / 60)

	def update(self):

		while self.connect:
			
			messages = self.online.receiving_message()

			for i in messages:

				if i[0] == "l":

					conn, x, y, speed_x, speed_y, angle, angle_rot_x, angle_rot_y, skin = i[1]

					if conn in self.objects:
						pl = self.objects[conn]
						pl.body.position = x, y
						pl.edit_velocity(speed_x, speed_y)
						pl.body.angle = angle
						pl.skin = skin

					else:

						if skin == "m":
							self.body.position = x, y
							self.body.velocity = [speed_x, speed_y]
							self.body.angle = angle
							
						else:

							self.space_add_player.append((Player((x, y)), speed_x, speed_y, angle, conn))


				elif i[0] == "score":
					self.score = self.font.render(i[1], False, (0, 0, 0))

				elif i[0] == "quit":
					if i[1] in self.objects:
						self.space_remove_player.append(i[1])

	def event(self, ev):

		for key in self.objects:
			if key == self.online.ID:
				obj = self.objects[key]
				velocity = obj.body.velocity
				x, y = velocity
				break
		else:
			return

		
		if ev.type == pygame.KEYDOWN:

			if ev.key == pygame.K_w:
				y = -190
			elif ev.key == pygame.K_a:
				x = -190
			elif ev.key == pygame.K_s:
				y = 190
			elif ev.key == pygame.K_d:
				x = 190

		if ev.type == pygame.KEYUP:

			if ev.key == pygame.K_w:
				y = 0
			elif ev.key == pygame.K_a:
				x = 0
			elif ev.key == pygame.K_s:
				y = 0
			elif ev.key == pygame.K_d:
				x = 0
		
		obj.body.velocity = x, y

