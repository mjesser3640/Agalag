import sys, pygame, os, time
pygame.init()

black = 0,0,0

size = width, height = 500, 900
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
		self.last_move = 0
		self.last_shot = 0
		self.projectiles = []
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
	def die(self):
		self.wave.ships.remove(self)
		del self

class Wave:
	def __init__(self):
		self.ships = []
		for x in range(6):
			self.ships.append(Enemy((10 + (x * (enemy_ship.get_rect().width + 10)),2),self))
	def draw(self):
		for ship in self.ships:
			screen.blit(ship.image, ship.pos)

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
			return self.pos.colliderect(player)
		else:
			for wave in waves:
				for ship in wave.ships:
					if self.pos.colliderect(ship.pos):
						ship.die()
						return 1

player = Player()
waves = [Wave()]

while 1:
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
	for wave in waves:
		wave.draw()
	screen.blit(player.image, player.pos)
	pygame.display.flip()
