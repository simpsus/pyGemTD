import pygame
import math
import logging
pygame.init()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(funcName)s %(lineno)d %(message)s')
logger = logging.getLogger('pyGemTD')

colors = {
	'shot' : pygame.Color('#e0bd3e'),
	'creep' : pygame.Color('#d0c64b'),
	'creep_dark' : pygame.Color('#847a00'),
	'ground' : pygame.Color('#7c9c54'),
	'wall' : pygame.Color('#2f655a'),
	'tower' : pygame.Color('#1c353b'),
	'ground_path' : pygame.Color('#666666'),
	'ground_blocked' : pygame.Color('#AA6666'),
	'ground_waypoint' : pygame.Color('#FF0000'),
	'text_waypoint' : pygame.Color('#FFD300'),
	'skill_coldAuraBlast' : pygame.Color('#2DAFED'),
	'skill_arcWave' : pygame.Color('#ECA26A'),
	'ground_path' : pygame.Color('#e0bd3e'),
}
# a square screen makes for maximum maze possibilities. 1k might be too much vertically, though
width = 1000
height = 1000
tile_multiplier = 10

display = pygame.display.set_mode((width,height))
pygame.display.set_caption('pyGemTowerDefense')
clock = pygame.time.Clock()
arial_font = pygame.font.SysFont('arial',10)

# render queue for background entities
background = []
# render queue for active creeps
active_creeps = []

# grid tile types
FREE = 'F'
BLOCKED = 'B'
WAYPOINT = 'W'

def reconstruct_path(cameFrom, current):
	"""
	reverse-walks the the cameFrom dict to construct the path contained starting from current
	"""
	path = [current]
	while current in cameFrom:
		current = cameFrom[current]
		path = [current] + path
	return path

def cartesian_distance(one, other):
	"""
	geometric line distance between two points
	"""
	return math.sqrt((other[0] - one[0])**2 + (other[1] - one[1])**2)

def A_star(start, goal, h, d, ne):
	"""
	returns the shortest path from start to goal, or False if there is none
	h: a function giving the weight for any position on the grid
	d: a distance function between two positions on the grid
	ne: a function returning the neighbors of a position
	"""
	openSet = set()
	openSet.add(start)
	cameFrom = {}
	gScore = {}
	gScore[start] = 0
	fScore = {}
	fScore[start] = h(start)
	while len(openSet) > 0:
		current = None
		#print('fScore ', fScore)
		for n in openSet:
			if not current or fScore[n] < fScore[current]:
				current = n
		if current == goal:
			return reconstruct_path(cameFrom, current)
		#print(current, openSet)
		openSet.remove(current)
		for neighbor in ne(current):
			#print(neighbor)
			tentative_gScore = gScore[current] + d(current, neighbor)
			if neighbor not in gScore or tentative_gScore < gScore[neighbor]:
				cameFrom[neighbor] = current
				gScore[neighbor] = tentative_gScore
				fScore[neighbor] = gScore[neighbor] + h(neighbor)
				if neighbor not in openSet:
					openSet.add(neighbor)
	return False

class Tile(object):
	"""
	A Tile is 10 px square on the board and the smallest buildable unit
	"""

	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		background.append(self)
		self.rect = pygame.Rect(x*tile_multiplier, y*tile_multiplier, tile_multiplier, tile_multiplier)
		self.color = colors['ground']
		self.type = FREE
		self.x = x
		self.y = y
		self.text = None

	def draw(self, surface):
		pygame.draw.rect(surface, self.color, self.rect, 0)
		if self.text:
			textsurface = arial_font.render(self.text, True, colors['text_waypoint'])
			surface.blit(textsurface, self.rect.midtop)

	def clear(self):
		self.color = colors['ground']
		self.type = FREE

	def block(self):
		self.color = colors['ground_blocked']
		self.type = BLOCKED

	def waypoint(self):
		self.color = colors['ground_waypoint']
		self.type = WAYPOINT

	def path(self, color = colors['ground_path']):
		self.color = color

	def __repr__(self):
		return '('+str(self.x) + ',' + str(self.y) + ')'

class Creep(object):

	def __init__(self, hp, speed, creep_type):
		self.pos = None
		self.hp = hp
		# size is the radius of the circle that represents the creep
		#TODO change creeps to animated sprites
		self.size = 4
		self.currnet_hp = self.hp
		self.speed = speed
		self.current_speed = self.speed
		# creep types can either be things like immune/fast/boss/group
		#TODO decide how flying and potentially other types (spawn) are handled. type or sublcass
		self.type = creep_type
		self.rect = None
		#TODO stun flag/timer, slowed flag/timer/amount
		# when a creep is active it is on the map and walks
		self.active = False
		# when a creep is breached it made it to the end alive
		self.breached = False
		self.path = []
		#the point currently walking towards
		self.current_destination = None
		self.dead = False

	def activate(self):
		self.active = True
		self.pos = (round(self.path[0].x * tile_multiplier + 0.5 * tile_multiplier), \
			round(self.path[0].y * tile_multiplier + 0.5 * tile_multiplier))
		self.current_destination = (round(self.path[1].x * tile_multiplier + 0.5 * tile_multiplier), \
			round(self.path[1].y * tile_multiplier + 0.5 * tile_multiplier))
		self.path = self.path[2:]

	def die(self):
		self.active = False

	def breach(self):
		self.breached = True
		self.active = False

	def update(self):
		# update means the creep is active, so it is walking
		#TODO implement things like stunned and slowed
		#pos and current_destination are tuples, not objects
		#the coordinates of the path have to be translated to screen coordinates
		#logger.debug('Creep Position before update: ' + str(self.pos) + '. Destination ' + str(self.current_destination))
		if cartesian_distance(self.pos, self.current_destination) <= self.speed:
			if len(self.path) == 0:
				self.breach()
				return
			else:
				self.current_destination = (round(self.path[0].x * tile_multiplier + 0.5 * tile_multiplier), \
					round(self.path[0].y * tile_multiplier + 0.5 * tile_multiplier))
				self.path = [] if len(self.path) == 1 else self.path[1:]
		#now we walk. x first, then y
		if abs(self.pos[0] - self.current_destination[0]) > self.speed:
			if self.pos[0] < self.current_destination[0]:
				#we are walking right
				self.pos = (self.pos[0] + self.speed, self.pos[1])
			else:
				#we are walking left
				self.pos = (self.pos[0] - self.speed, self.pos[1])
		else:
			#as we are active so we are not breached, y it has to be
			if self.pos[1] < self.current_destination[1]:
				#we are walking down
				self.pos = (self.pos[0], self.pos[1] + self.speed)
			else:
				#we are walking up
				self.pos = (self.pos[0], self.pos[1] - self.speed)
		#logger.debug('Creep Position after update: ' + str(self.pos) + '. Destination ' + str(self.current_destination))

	def draw(self, surface):
		pygame.draw.circle(surface, colors['creep'], self.pos, self.size, 0)

	def __repr__(self):
		return 'Creep(' + str(id(self)) + ')@' + str(self.pos)

class Game(object):

	def __init__(self):
		# initialize the grid with Tiles
		self.grid = {}
		for x in range(width//tile_multiplier):
			for y in range(height//tile_multiplier):
				self.grid[(x,y)] = Tile(x,y)
		# define the waypoints
		self.start = (0,5)
		self.waypoints = [(10,5),(10,50),(90,50),(90,5),(50,5),(50,80)]
		self.end = (99,80)
		self.path = []
		# the creeps currently in the game. TODO change to (to be implemented) Wave
		self.current_creeps = []

	def show_waypoints(self):
		"""
		colors and blocks the waypoint tiles around the waypoints
		"""
		for i,point in enumerate(self.waypoints):
			for x in range(4):
				for y in range(4):
					self.grid[(point[0]-1+x,point[1]-1+y)].waypoint()
			self.grid[point].text = str(i)

	def get_neighbor(self, tile):
		# diagonal tiles are not neighbors, only above, below, right, left
		result = []
		coords = ((tile.x-1,tile.y),(tile.x+1,tile.y),(tile.x,tile.y-1),(tile.x,tile.y+1))
		for (x,y) in coords:
			if x < 0 or y < 0 or x > 99 or y > 99:
				continue
			n = self.grid[(x,y)]
			if n.type != BLOCKED:
				#print(n.type)
				result.append(n)
		return result

	def make_path(self):
		"""
		compute the total path the creeps have to go
		"""
		wp = [self.start] + self.waypoints + [self.end]
		path = []
		for i in range(len(wp) - 1):
			a = self.grid[wp[i]]
			b = self.grid[wp[i+1]]
			path.extend(
				A_star(
					a,
					b,
					lambda w: cartesian_distance((a.x, a.y),(w.x, w.y)),
					lambda w1,w2: cartesian_distance((w1.x, w1.y),(w2.x,w2.y)),
					lambda w: self.get_neighbor(w)
					)
				)
		self.path = path
		logger.debug('Calculated Path. Length: ' + str(len(self.path)))
		#print(self.path)

	def show_path(self):
		total = len(self.path)
		for i, tile in enumerate(self.path):
			c = round((i/total) * 255)
			tile.path(color=(c,c,c))

	def clear_path(self):
		# blocked tiles cannot be cleared
		for tile in self.path:
			if tile.type != BLOCKED:
				tile.clear()

	def get_tile_for_position(self, pos):
		return self.grid[(pos[0]//tile_multiplier,pos[1]//tile_multiplier)]

	def process_breach(self, creep):
		logger.debug('Creep breached: ' + str(creep))
		self.current_creeps.remove(creep)
		active_creeps.remove(c)
		logger.debug('Creep ' + str(c) + ' removed from active creeps.')


	def update(self):
		#update the list of creeps
		for c in self.current_creeps:
			c.update()
			if c.breached:
				self.process_breach(c)

game = Game()
game.make_path()
game.show_waypoints()
game.show_path()
logger.debug('Creating and activating test creep')
creep = Creep(100,2,'NORMAL')
creep.path = game.path[:]
creep.activate()
game.current_creeps.append(creep)
active_creeps.append(creep)
logger.debug('Active Creeps ' + str(active_creeps))
terminated = False
#Path updates will not affect the debug creep
while not terminated:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			terminated = True
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE:
				game.clear_path()
				game.make_path()
				game.show_waypoints()
				game.show_path()
		elif event.type == pygame.MOUSEBUTTONDOWN:
			tile = game.get_tile_for_position(pygame.mouse.get_pos())
			if tile.type == BLOCKED:
				tile.clear()
			elif tile.type != WAYPOINT:
				tile.block()
	game.update()
	for b in background:
		b.draw(display)
	for c in active_creeps:
		c.draw(display)
	pygame.display.update()
	clock.tick(60)

pygame.quit()