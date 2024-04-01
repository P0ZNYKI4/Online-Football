# cd D:\Python\Скрипты\Вольтяшка\группа_2\zan_22 & D: & python main.py
import pygame
pygame.init()

from fun import *

screen = pygame.display.set_mode((900, 500))
clock = pygame.time.Clock()

background = pygame.image.load("background.png").convert()
font = pygame.font.Font("5.ttf", 100)

score = font.render("", False, (0, 0, 0))

images = {
	"a": pygame.image.load("a.png").convert_alpha(),
	"d": pygame.image.load("d.png").convert_alpha(),
	"e": pygame.image.load("e.png").convert_alpha(),
	"i": pygame.image.load("i.png").convert_alpha(),
	"k": pygame.image.load("k.png").convert_alpha(),
	"m": pygame.image.load("m.png").convert_alpha(), # Не использовать как скин
	"n": pygame.image.load("n.png").convert_alpha(),
	"p": pygame.image.load("p.png").convert_alpha(),
	"r": pygame.image.load("r.png").convert_alpha(),
	"s": pygame.image.load("s.png").convert_alpha(),
	"t": pygame.image.load("t.png").convert_alpha(),	
}

my_name = "n"

online = Online("192.168.1.69")
online.connection(my_name)

obj = Objects(images, online, font)

loop = 1

while loop:

	clock.tick(60)

	for ev in pygame.event.get():

		obj.event(ev)

		if ev.type == pygame.KEYDOWN:

			if ev.key == pygame.K_w:
				online.send(" w_d ")
			elif ev.key == pygame.K_a:
				online.send(" a_d ")
			elif ev.key == pygame.K_s:
				online.send(" s_d ")
			elif ev.key == pygame.K_d:
				online.send(" d_d ")

		if ev.type == pygame.KEYUP:

			if ev.key == pygame.K_w:
				online.send(" w_u ")
			elif ev.key == pygame.K_a:
				online.send(" a_u ")
			elif ev.key == pygame.K_s:
				online.send(" s_u ")
			elif ev.key == pygame.K_d:
				online.send(" d_u ")

		if ev.type == pygame.QUIT:
			online.send(" q ")
			loop = 0

	screen.blit(background, (0, 0))

	obj.animation()
	obj.draw(screen)

	pygame.display.flip()

