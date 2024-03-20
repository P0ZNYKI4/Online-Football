# cd D:\Python\Скрипты\Вольтяшка\группа_2\zan_22 & D: & python server.py

from socket import *
import urllib.request, urllib.error
from threading import Thread
import pygame; pygame.init()
import pymunk
from pymunk import pygame_util, Vec2d
from random import randint
pymunk.pygame_util.positive_y_is_up = False



class ServerGame:

	def __init__(self, ip):
		self.ip = ip
		self.addr = (self.ip, 3301)

		self.tcp_socket = socket(AF_INET, SOCK_STREAM)

		self.players = dict()

		self.status_message = "wait"
		self.meaning_message = ""

		self.message_now = ""
		self.server_online = True

		self.receiving_messages = dict()

		th = Thread(target=self.connection)
		th.daemon = True
		th.start()
		

	def connection(self):
		print("server create")
		self.tcp_socket.bind(self.addr)
		self.tcp_socket.listen(6)

		while self.server_online:
			conn, addr = self.tcp_socket.accept()
			new_player = Player([100, 100])

			messages = conn.recv(1024).decode()
			new_player.skin = messages

			self.players[conn] = new_player
			print("client accept: ", addr)

			pl = Thread(target=self.receiving_message, args=((conn, addr)))
			pl.daemon = True
			pl.start()


	def receiving_message(self, conn, addr):

		print("Ожидаю")

		connect = True

		while connect:

			try:
				messages = conn.recv(1024).decode()
			except ConnectionResetError:

				if conn in self.players:
					space.remove(self.players[conn].shape)
					self.players.pop(conn, None)

				connect = False
				messages = ""
			
			if messages == "w_d":
				self.players[conn].key_w = True
			elif messages == "a_d":
				self.players[conn].key_a = True
			elif messages == "s_d":
				self.players[conn].key_s = True
			elif messages == "d_d":
				self.players[conn].key_d = True

			elif messages == "w_u":
				self.players[conn].key_w = False
			elif messages == "a_u":
				self.players[conn].key_a = False
			elif messages == "s_u":
				self.players[conn].key_s = False
			elif messages == "d_u":
				self.players[conn].key_d = False

			#print(messages)

	def send_message(self, conn, message):
		try:
			conn.send(str.encode(message))
		except ConnectionResetError:

			if conn in self.players:
				space.remove(self.players[conn].shape)
				self.players.pop(conn, None)



class Player:
	
	def __init__(self, coord):
		self.coord = coord

		self.segment_add = False

		self.speed = 5

		self.key_w = False
		self.key_a = False
		self.key_s = False
		self.key_d = False

	def draw(self, screen):
		pygame.draw.circle(screen, (255, 255, 255), self.coord, 30)


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
		velocity = [0, 0]
		# w s
		if not (self.key_w and self.key_s):
			if self.key_w:
				velocity[1] = -190
			elif self.key_s:
				velocity[1] = 190
		# a d
		if not (self.key_a and self.key_d):
			if self.key_a:
				velocity[0] = -190
			elif self.key_d:
				velocity[0] = 190

		self.body.velocity = velocity


if __name__ == "__main__":


	game = ServerGame("192.168.1.70")

	screen = pygame.display.set_mode((900, 500))
	clock = pygame.time.Clock()

	background = pygame.image.load("background.png").convert()

	draw_options = pymunk.pygame_util.DrawOptions(screen)
	space = pymunk.Space()
	space.gravity = 0, 0

	# границы
	sides = (
		pymunk.Segment(space.static_body, (0, 0), (900, 0), 15),
		pymunk.Segment(space.static_body, (0, 498), (900, 498), 15),
		pymunk.Segment(space.static_body, (0, 0), (0, 500), 15),
		pymunk.Segment(space.static_body, (900, 0), (900, 500), 15),

		pymunk.Segment(space.static_body, (0, 171), (115, 171), 15),
		pymunk.Segment(space.static_body, (0, 336), (115, 336), 15),
		pymunk.Segment(space.static_body, (760, 171), (900, 171), 15),
		pymunk.Segment(space.static_body, (760, 336), (900, 336), 15)
	)

	for i in sides:
		i.elasticity = 0.4
		i.friction = 1.0
		space.add(i)
	
	# мяч
	mass = 1
	radius = 10
	inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
	body = pymunk.Body(mass, inertia)
	body.position = (900 / 2, 500 / 2)
	shape = pymunk.Circle(body, 10, (0, 0))
	shape.mass = 0.1
	shape.elasticity = 0.95
	shape.friction = 0.9
	space.add(body, shape)

	score = [0, 0]

	bad_internet_test = False


	loop = 1
	while loop:
		
		clock.tick(60)

		for ev in pygame.event.get():

			if ev.type == pygame.QUIT:
				loop = 0

		screen.blit(background, (0, 0))

		message = f" | (({body.position.x:.2f},{body.position.y:.2f},'m',{body.angle:.2f}),"

		for key in game.players:
			player = game.players[key]

			if not player.segment_add:
				player.segment_add = True
				player.create_ball(space)

			player.animation()

			message += f"({player.body.position.x:.2f},{player.body.position.y:.2f},'{player.skin}',{player.body.angle:.2f}),"

		message += ") l "


		if not (bad_internet_test and randint(0, 100) > 30):
			for conn in game.players:
				game.send_message(conn, message)


		score_send = False

		if body.position.x > 780 and 188 <= body.position.y <= 320:
			score[0] += 1; score_send = True
		elif body.position.x < 90 and 188 <= body.position.y <= 320:
			score[1] += 1; score_send = True

		if score_send:
			body.position = (900 / 2, 500 / 2)
			body.velocity = [0, 0]

			message = f" | ({score[0]},{score[1]}) z "

			for conn in game.players:
				game.send_message(conn, message)

		space.step(1 / 60)
		space.debug_draw(draw_options)

		pygame.display.flip()

