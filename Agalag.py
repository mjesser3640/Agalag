import sys, pygame, os, time, random
pygame.init()

black = 0,0,0
white = 250,250,250

size = width, height = 500, 600
screen = pygame.display.set_mode(size)
player_ship = pygame.image.load("player_ship.png")
laser = pygame.image.load("laser.png")
enemy_laser = pygame.image.load("enemy_laser.png")
enemy_ship = pygame.image.load("enemy.png")

class Player:
	def __init__(self):
		self.image = player_ship
		self.pos = self.image.get_rect()
		self.pos.midbottom = screen.get_rect().midbottom
		self.pos.bottom -= 20
		self.last_move = 0
		self.last_shot = 0
		self.projectiles = []
		self.score = 0
		self.playing = True
	def move_right(self):
		if self.pos.right < 500 and time.monotonic() - self.last_move > 0.001:
			self.pos = self.pos.move(2,0)
			self.last_move = time.monotonic()
	def move_left(self):
		if self.pos.left > 0 and time.monotonic() - self.last_move > 0.001:
			self.pos = self.pos.move(-2,0)
			self.last_move = time.monotonic()
	def shoot(self):
		if len(self.projectiles) < 2 and time.monotonic() - self.last_shot > 0.2:
			new_shot = Laser(self.pos.midtop, -1, self)
			self.projectiles.append(new_shot)
			self.last_shot = time.monotonic()
	def move_projectiles(self):
		if self.projectiles:
			for laser in self.projectiles:
				laser.move()

class Enemy:
	def __init__(self, top_left, wave):
		self.image = enemy_ship
		self.pos = self.image.get_rect()
		self.pos.topleft = top_left
		self.projectiles = []
		self.wave = wave
	def move_right(self):
		self.pos = self.pos.move(10,0)
	def move_left(self):
		self.pos = self.pos.move(-10,0)
	def move_down(self):
		self.pos = self.pos.move(0, 10)
	def die(self):
		self.wave.ships.remove(self)
		del self
	def is_touching_player(self):
		if self.pos.colliderect(player.pos):
			player.playing = not player.playing
			return True

class Wave:
	def __init__(self):
		self.ships = []
		for x in range(6):
			self.ships.append(Enemy((10 + (x * (enemy_ship.get_rect().width + 10)),2),self))
		self.direction = True
		self.last_move = 0
		self.last_shot = 0
		self.projectiles = []
	def draw(self):
		for ship in self.ships:
			screen.blit(ship.image, ship.pos)
	def check_screen_edge(self):
		return self.ships[0].pos.left < 10 or self.ships[-1].pos.right > 490
	def move(self):
		if self.direction:
			for ship in self.ships:
				ship.move_right()
				ship.is_touching_player()
		else:
			for ship in self.ships:
				ship.move_left()
				ship.is_touching_player()
		if self.check_screen_edge():
			self.direction = not self.direction
			for ship in self.ships:
				ship.move_down()
	def shoot(self):
		ship = self.ships[random.randrange(len(self.ships))]
		new_shot = Laser(ship.pos.midbottom, 1, self)
		new_shot.pos.bottom += 27
		self.projectiles.append(new_shot)
		self.last_shot = time.monotonic()
	def ready_for_next_wave(self):
		return self.ships[0].pos.top > 63
	def is_empty(self):
		return not self.ships
	def move_projectiles(self):
		if self.projectiles:
			for laser in self.projectiles:
				laser.move()

class Laser:
	def __init__(self, midbottom, direction, owner):
		self.image = enemy_laser if direction == 1 else laser
		self.pos = self.image.get_rect()
		self.pos.midbottom = midbottom
		self.direction = direction
		self.owner = owner
		self.last_move = 0
	def move(self):
		screen.blit(self.image, self.pos)
		if time.monotonic() - self.last_move > 0.01:
			self.pos = self.pos.move(0, self.direction*5)
			if not self.check_offscreen():
				self.owner.projectiles.remove(self)
				del self
			elif self.check_hit():
				self.owner.projectiles.remove(self)
				del self
			else:
				self.last_move = time.monotonic()
	def check_offscreen(self):
		return self.pos.colliderect(screen.get_rect())
	def check_hit(self):
		if self.direction == 1:
			#ADD GAMEOVER LOGIC HERE
			if self.pos.colliderect(player.pos):
				player.playing = not player.playing
				return True
		else:
			for wave in waves:
				for ship in wave.ships:
					if self.pos.colliderect(ship.pos):
						self.owner.score += 100
						ship.die()
						return 1

player = Player()
waves = [Wave()]
score_text = pygame.font.Font('freesansbold.ttf', 20)
score_surface = score_text.render("Score: " + str(player.score), True, white)
score_rect = score_surface.get_rect()
score_rect.midbottom = screen.get_rect().midbottom 

while player.playing:
	for event in pygame.event.get(): #Check for program closing
		if event.type == pygame.QUIT:
			sys.exit()

	keys = pygame.key.get_pressed() #Check player actions
	if keys[pygame.K_RIGHT]:
		player.move_right()
	if keys[pygame.K_LEFT]:
		player.move_left()
	if keys[pygame.K_SPACE]:
		player.shoot()


	screen.fill(black) #redraw screen

	player.move_projectiles()

	if waves:
		for wave in waves: #move and draw enemy waves
			if wave.is_empty():
				waves.remove(wave)
				del wave
			else:
				wave.move_projectiles()
				if time.monotonic() - wave.last_move > 0.1:
					wave.move()
					wave.last_move = time.monotonic()
				wave.draw()
	else:
		waves.append(Wave())
	if waves:
		if waves[-1].ready_for_next_wave():
			waves.append(Wave())
		if time.monotonic() - waves[0].last_shot > 1:
			waves[0].shoot()


	score_surface = score_text.render("Score: " + str(player.score), True, white)
	screen.blit(score_surface, score_rect)
	screen.blit(player.image, player.pos)
	pygame.display.flip()
time.sleep()
