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

		self.udp_socket = socket(AF_INET, SOCK_DGRAM)

		self.players = dict()

		self.status_message = "wait"
		self.meaning_message = ""

		self.message_now = ""
		self.server_online = True

		self.receiving_messages = dict()

		self.remove_players = []
		self.add_players = []

		th = Thread(target=self.receiving_message)
		th.daemon = True
		th.start()
		

	def connection(self):
		print("server create")
		#self.tcp_socket.bind(self.addr)
		#self.tcp_socket.listen(6)
		self.udp_socket.bind(self.addr)

		while self.server_online:
			#conn, addr = self.tcp_socket.accept()

			messages, addr = self.udp_socket.recvfrom(1024)#.decode()

			messages = messages.decode()

			new_player = Player([100, 100])

			#messages = list(conn.recv(1024).decode())
			new_player.skin = messages[0]

			new_player.create_ball(space)

			#self.players[conn] = new_player
			self.players[addr] = new_player

			print("client accept: ", addr)

			#pl = Thread(target=self.receiving_message, args=((conn, addr)))
			#pl.daemon = True
			#pl.start()
			pl = Thread(target=self.receiving_message)
			pl.daemon = True
			pl.start()

	def receiving_message(self):

		print("Приём сообщений")

		self.udp_socket.bind(self.addr)

		while True:

			addr = ""

			messages, addr = self.udp_socket.recvfrom(1024)
			
			messages = messages.decode()

			if not addr in self.players:

				skin = messages

				new_player = Player([720, 250] if skin in right_command else [140, 250])
				new_player.skin = messages

				if not (new_player, addr) in self.add_players:
					self.add_players.append((new_player, addr))

				print("client accept: ", addr)

				continue

			
			messages = messages.split()


			edit = False
			for i in messages:

				if i == "w_d":
					self.players[addr].key_w = True; edit = True
				elif i == "a_d":
					self.players[addr].key_a = True; edit = True
				elif i == "s_d":
					self.players[addr].key_s = True; edit = True
				elif i == "d_d":
					self.players[addr].key_d = True; edit = True

				elif i == "w_u":
					self.players[addr].key_w = False; edit = True
				elif i == "a_u":
					self.players[addr].key_a = False; edit = True
				elif i == "s_u":
					self.players[addr].key_s = False; edit = True
				elif i == "d_u":
					self.players[addr].key_d = False; edit = True

				elif i == "q":
					print("Пользователь отключился, удаляю его с поля")

					self.remove_players.append(addr)

					while len(self.remove_players) != 0:
						...

					message = f" | ({addr[1]}) q "
					print("Сообщение для удаления:", message)
					for addr in self.players:
						self.send_message(addr, message)

			# send all
			if edit:
				pl = self.players[addr]

				pl.animation()

				message = f" | ({addr[1]},{self.get_obj_data(pl.body)},'{pl.skin}') l "

				for addr in self.players:
					self.send_message(addr, message)

	def get_obj_data(self, body):
		txt = ""
		txt += f"{body.position.x:.2f},{body.position.y:.2f},"
		txt += f"{body.velocity.x:.2f},{body.velocity.y:.2f},"
		txt += f"{body.angle:.2f},"
		txt += f"{body.rotation_vector.x:.2f},{body.rotation_vector.y:.2f}"
		return txt

	def send_message(self, addr, message):
		self.udp_socket.sendto(message.encode(), addr)



class Player:
	
	def __init__(self, coord):
		self.coord = coord

		#self.segment_add = False

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


	game = ServerGame("192.168.1.69")

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

	old_velocity_ball = (body.velocity.x, body.velocity.y)

	score = [0, 0]

	bad_internet_test = False
	
	'''
	"d" Даня
	"p" Паша
	"t" Тимофей
	"k" Катя
	"a" Таня
	"i" Дима
	'''

	right_command = ["i", "d"]

	loop = 1
	while loop:
		
		clock.tick(60)

		for ev in pygame.event.get():

			if ev.type == pygame.QUIT:
				loop = 0

		screen.blit(background, (0, 0))

		

		for data in game.add_players:
			new_player, addr = data
			new_player.create_ball(space)
			game.players[addr] = new_player
			message = f"{addr[1]}"
			game.send_message(addr, message)

			print("client add: ", addr)

			game.add_players.remove(data)

		for addr in game.remove_players:
			space.remove(game.players[addr].shape)
			game.players.pop(addr, None)
			game.remove_players.remove(addr)

		#if len(game.players) != 0:
		#	print(game.players)

		for key in game.players:
			player = game.players[key]

			player.animation()

		old_velocity_ball = (body.velocity.x, body.velocity.y)
		message = f" | (-100,{game.get_obj_data(body)},'m') l "

		for conn in game.players:
			game.send_message(conn, message)

		score_send = False

		if body.position.x > 759 and 188 <= body.position.y <= 320:
			score[0] += 1; score_send = True
		elif body.position.x < 119 and 188 <= body.position.y <= 320:
			score[1] += 1; score_send = True

		#print(pygame.mouse.get_pos())

		if score_send:
			body.position = (900 / 2, 500 / 2)
			body.velocity = [0, 0]

			message = f" | ({score[0]},{score[1]}) z "

			for conn in game.players:
				game.send_message(conn, message)

			for addr in game.players:
				pl = game.players[addr]

				pl.body.position = [720, 250] if pl.skin in right_command else [140, 250]

				message = f" | ({addr[1]},{game.get_obj_data(pl.body)},'{pl.skin}') l "

				for addr in game.players:
					game.send_message(addr, message)


		



		space.step(1 / 60)
		space.debug_draw(draw_options)

		pygame.display.flip()
