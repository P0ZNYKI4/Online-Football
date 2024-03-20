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
	"m": pygame.image.load("m.png").convert_alpha(),
	"d": pygame.image.load("d.png").convert_alpha(),
	"p": pygame.image.load("p.png").convert_alpha(),
	"t": pygame.image.load("t.png").convert_alpha(),
	"k": pygame.image.load("k.png").convert_alpha(),
	"a": pygame.image.load("a.png").convert_alpha(),	
}

my_name = "a"

online = Online("192.168.1.70")
online.connection(my_name)

obj = tuple()

loop = 1

while loop:

	clock.tick(60)

	for ev in pygame.event.get():

		if ev.type == pygame.KEYDOWN:

			if ev.key == pygame.K_w:
				online.send("w_d")
			elif ev.key == pygame.K_a:
				online.send("a_d")
			elif ev.key == pygame.K_s:
				online.send("s_d")
			elif ev.key == pygame.K_d:
				online.send("d_d")

		if ev.type == pygame.KEYUP:

			if ev.key == pygame.K_w:
				online.send("w_u")
			elif ev.key == pygame.K_a:
				online.send("a_u")
			elif ev.key == pygame.K_s:
				online.send("s_u")
			elif ev.key == pygame.K_d:
				online.send("d_u")

		if ev.type == pygame.QUIT:
			loop = 0

	screen.blit(background, (0, 0))

	messages = online.receiving_message()

	for i in messages:

		if i[0] == "l":
			obj = i[1]
		elif i[0] == "score":
			score = font.render(i[1], False, (0, 0, 0))
	
	screen.blit(score, score.get_rect(center=(450, 50)))

	for x, y, skin, angle in obj:
		img = pygame.transform.rotate(images[skin], -angle * 20)
		screen.blit(img, img.get_rect(center=(x, y)))



	pygame.display.flip()

