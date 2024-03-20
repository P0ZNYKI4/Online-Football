from socket import *
import urllib.request, urllib.error
from threading import Thread
import pygame; pygame.init()

class Online:

	def __init__(self, ip):
		self.ip = ip
		self.addr = self.addr = (self.ip, 3301)
		self.decoder = DecodingMessage()

	def connection(self, name):
		self.tcp_socket = socket(AF_INET, SOCK_STREAM)
		self.tcp_socket.connect(self.addr)
		print("accept: ", self.addr)

		self.send(name)



	def send(self, message):
		message = str.encode(message)
		self.tcp_socket.send(message)

	def receiving_message(self):
		return self.decoder.get(self.tcp_socket.recv(1024).decode())
			
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

				msg = ("l", eval(self.long_txt))
				message.append(msg)

				self.long_txt = ""
				
			elif txt == "z":
				self.join_status = False

				msg = ["score", eval(self.long_txt)]
				msg[1] = f"{msg[1][0]}       {msg[1][1]}"
				message.append(msg)

				self.long_txt = ""
				
			elif txt == "|":
				self.join_status = True

			else:
				self.long_txt += txt

		return message


#class 


