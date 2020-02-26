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
tile_multiplier = 25



# render queue for background entities
background = []

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

class BlinkingTileAnimation(object):

	def __init__(self, tile):
		self.tile = tile
		background.append(self)
		self.timer = 0
		self.colors = (colors['ground'], pygame.Color('#000000'))
		self.flick = 0

	def draw(self, surface):
		self.timer += 1
		if self.timer == 60:
			tile.color = colors['ground']
			background.remove(self)
		elif self.timer % 10 == 0:
			self.flick = 0 if self.flick == 1 else 1
			tile.color = self.colors[self.flick]


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

	def reset(self):
		# does not change the type, resets the color to remove a path
		if self.type == FREE:
			self.color = colors['ground']
		elif self.type == WAYPOINT:
			self.color = colors['ground_waypoint']
		elif self.type == BLOCKED:
			self.color = colors['ground_blocked']	

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

class Wave(object):
	"""
	A wave is a group of creeps.
	A wave is started by the game
	Assumption: As there is no building/removing of blocks during a wave, the path of all creeps in one
	wave is the same. 
	"""

	def __init__(self, size, creep_generator, gap):
		#the size is the number of creeps in this wave
		self.size = size
		#the creep generator is a function without argument that will create creeps for this wave
		self.creep_generator = creep_generator
		#the gap is the number of ticks that passes between creeps starting
		self.gap = gap
		#the gap_ticker is the counter looping the gap
		self.gap_ticker = 0
		#the creeps in ths wave
		self.creeps = []
		#a flag indicating if this wave is active, a wave is active when there are still creeps active
		self.active = False
		#a flag indicating if this wave is released, a wave is released when all the creeps are on their way
		self.released = False
		# the path is not required at creation time (may change since then) but has to be set before creeps
		# can be sent. Is the same for all creeps in the wave
		self.path = []
		logger.debug('Created Wave ' + str(id(self)) + ' with ' + str(self.size) + ' creeps and ' + str(self.gap) + ' ticks gap.')

	def update(self):
		#Assumption: update is only called when the wave is active and has the task to
		# create creeps until all are there
		# manage the lifecycle of the creeps
		# keep the wave flags active/released correct
		if not self.released:
			if self.gap_ticker == self.gap:
				creep = self.creep_generator()
				creep.path = self.path[:]
				creep.activate()
				self.creeps.append(creep)
				self.gap_ticker = 0
				logger.debug('Wave ' + str(id(self)) + ' releases creep ' + str(creep))
				if len(self.creeps) == self.size:
					logger.debug('Wave ' + str(id(self)) + ' has released all of its creeps.')
					self.released = True
			else:
				self.gap_ticker += 1
		# assumption: creeps keep their flags (active, dead, breached) updates themselves
		for c in [c for c in self.creeps if c.active]:
			c.update()
		# recalculate if a creep is now inactive (optimization potential ...)
		if self.released and len([c for c in self.creeps if c.active]) == 0:
			#logger.debug('Wave ' + str(id(self)) + ' has no more active creeps.')
			self.active = False

	def draw(self, surface):
		for c in [c for c in self.creeps if c.active]:
			c.draw(surface)




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
		#activating sets the position to the first item in the path, the destination to the second
		#and updates the path to the remainder
		self.active = True
		self.pos = (round(self.path[0].x * tile_multiplier + 0.5 * tile_multiplier), \
			round(self.path[0].y * tile_multiplier + 0.5 * tile_multiplier))
		self.current_destination = (round(self.path[1].x * tile_multiplier + 0.5 * tile_multiplier), \
			round(self.path[1].y * tile_multiplier + 0.5 * tile_multiplier))
		self.path = self.path[2:]
		logger.debug('Creep ' + str(self) + ' is now active.')

	def die(self):
		self.active = False

	def breach(self):
		logger.debug('Creep ' + str(self) + ' has breached.')
		self.breached = True
		self.active = False

	def update(self):
		# update means the creep is active, so it is walking
		#TODO implement things like stunned and slowed
		#pos and current_destination are tuples, not objects
		#the coordinates of the path have to be translated to screen coordinates
		#logger.debug('Creep Position before update: ' + str(self.pos) + '. Destination ' + str(self.current_destination))
		#check if we are done with the path, if so, breach
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
		# define the waypoints, in relation to the tile_multiplier
		self.start = (0,125//tile_multiplier)
		self.waypoints = [(125//tile_multiplier,125//tile_multiplier),(125//tile_multiplier,475//tile_multiplier),\
		(825//tile_multiplier,475//tile_multiplier),(825//tile_multiplier,125//tile_multiplier),\
		(475//tile_multiplier,125//tile_multiplier),(475//tile_multiplier,825//tile_multiplier)]
		self.end = (990//tile_multiplier,800//tile_multiplier)
		self.path = []
		# the waves currently active
		self.current_waves = []

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
			if x < 0 or y < 0 or x > (990//tile_multiplier) or y > (990//tile_multiplier):
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
		logger.debug('Showing Path Visualization.')
		total = len(self.path)
		for i, tile in enumerate(self.path):
			c = round((i/total) * 255)
			tile.path(color=(c,c,c))

	def hide_path(self):
		logger.debug('Hiding Path Visualization.')
		for tile in self.path:
			tile.reset()

	def clear_path(self):
		# blocked tiles cannot be cleared
		logger.debug('Removing blocks from path tiles.')
		for tile in self.path:
			if tile.type != BLOCKED:
				tile.clear()

	def dump_path(self):
		size = width // tile_multiplier
		result = []
		for j in range(size):
			t = [None for i in range(size)]
			result.append(t)
		for (x,y), tile in self.grid.items():
			result[x][y] = math.inf if tile.type == BLOCKED else 0
		return result

	def get_tile_for_position(self, pos):
		return self.grid[(pos[0]//tile_multiplier,pos[1]//tile_multiplier)]

	def update(self):
		#update the current waves
		for wave in self.current_waves:
			wave.update()
			if not wave.active:
				logger.debug(str(wave) + ' is no longer active')
		self.current_waves = [w for w in self.current_waves if w.active]

	def is_valid_grid(self):
		# returns a tuple with a boolean. If the boolean is false, the 
		# second item is the tile that is not reachable
		wp = [self.start] + self.waypoints + [self.end]
		path = []
		for i in range(len(wp) - 1):
			a = self.grid[wp[i]]
			b = self.grid[wp[i+1]]
			search = A_star(
				a,
				b,
				lambda w: cartesian_distance((a.x, a.y),(w.x, w.y)),
				lambda w1,w2: cartesian_distance((w1.x, w1.y),(w2.x,w2.y)),
				lambda w: self.get_neighbor(w)
				)
			if search == False:
				return (False, self.grid[wp[i+1]])
		return (True, None)
		


if __name__ == '__main__':

	display = pygame.display.set_mode((width,height))
	pygame.display.set_caption('pyGemTowerDefense')
	clock = pygame.time.Clock()
	arial_font = pygame.font.SysFont('arial',10)

	game = Game()
	game.make_path()
	game.show_waypoints()
	game.show_path()

	print (game.start, game.waypoints, game.end)
	logger.debug('SPACE calculates path and displays it.')
	logger.debug('w creates a wave and sends them along the current path.')
	logger.debug('h hides the current path (still there, just invisible).')
	logger.debug('c resets all blocked tiles and puts path to vanilla.')
	logger.debug('d dumps a representation of the current grid in console.')
	logger.debug('Creating and activating test wave')
	c_gen = lambda : Creep(100,2,'NORMAL')
	wave = Wave(10, c_gen, 60)
	wave.path = game.path
	wave.active = True
	game.current_waves.append(wave)

	terminated = False
	dragging = False
	while not terminated:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				terminated = True
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					# the path was updated in the gui, make it known
					game.clear_path()
					game.make_path()
					game.show_waypoints()
					game.show_path()
				elif event.key == pygame.K_w:
					# starts a new wave with the current path
					w = Wave(10, c_gen, 60)
					w.path = game.path
					w.active = True
					game.current_waves.append(w)
				elif event.key == pygame.K_h:
					# hides the current path
					game.hide_path()
				elif event.key == pygame.K_c:
					# clear the grid in the sense that it is reset to vanilla
					for tile in game.grid.values():
						if tile.type == BLOCKED:
							tile.clear()
					game.clear_path()
					game.make_path()
					game.show_waypoints()
					game.show_path()
				elif event.key == pygame.K_d:
					# dump the current path to a format that is reusable
					grid = game.dump_path()
					logger.debug('START Dumping Grid')
					logger.debug(grid)
					logger.debug('END Dumping')
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					dragging = True
				elif event.button == 3:
					tile = game.get_tile_for_position(pygame.mouse.get_pos())
					if tile.type == BLOCKED and tile.type != WAYPOINT:
						tile.clear()
			elif event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1:
					dragging = False
		if dragging:
			tile = game.get_tile_for_position(pygame.mouse.get_pos())
			if tile.type != BLOCKED and tile.type != WAYPOINT:
				tile.block()
				# after blocking it, check if it is still a valid grid
				valid = game.is_valid_grid()
				if not valid[0]:
					#clear the tile and display an animation as feedback
					tile.clear()
					logger.debug('Blocking tile ' + str(tile) + \
						' would block access to ' + str(valid[1]))
					BlinkingTileAnimation(tile)
		game.update()
		for b in background:
			b.draw(display)
		# this is temporary for testing purpose
		for w in game.current_waves:
			w.draw(display)
		pygame.display.update()
		clock.tick(60)

	pygame.quit()