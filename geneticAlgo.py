from pyGemTD import A_star, cartesian_distance, Game
import math
import random
import logging
import pygame
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(funcName)s %(lineno)d %(message)s')
logger = logging.getLogger('genetic')

class Individual(object):
    # an Individual is a gridm of zero/math.inf values

    grid_size = 40
    mutation_prob = 0.1

    def __init__(self):
        self.grid = []
        self.fitness = 0
        self.is_valid = False

    def initialize(self):
        for x in range(Individual.grid_size):
            self.grid.append([0 for y in range(Individual.grid_size)])
            

    def get_neighbor(self, c):
        x,y = c
        result = [(x+1,y), (x-1,y), (x, y+1), (x, y-1)]
        result = [i for i in result if i[0] >= 0 and i[0]<len(self.grid)]
        result = [i for i in result if i[1] >= 0 and i[1]<len(self.grid)]
        result = [i for i in result if self.grid[i[0]][i[1]] == 0]
        return result

    def clone(self):
        clone = Individual()
        clone.grid = self.grid[:]
        clone.fitness = self.fitness
        clone.is_valid = self.is_valid
        return clone

    def calculate_fitness(self):
        # calculates not only the fitness but also sets the is_valid flag
        path = [(0, 5), (5, 5), (5, 19), (33, 19), (33, 5), (19, 5), (19, 33), (39, 32)]
        result = 0
        for i in range(len(path) - 1):
            search = A_star(
                    path[i],
                    path[i+1],
                    lambda w: cartesian_distance((path[i][0], path[i][1]),(w[0], w[1])),
                    lambda w1,w2: cartesian_distance((w1[0], w1[1]),(w2[0], w2[1])),
                    lambda w: self.get_neighbor(w)
                    )
            if not search:
                self.is_valid = False
                self.fitness = math.inf
                return
            else:
                result += len(search)
        self.is_valid = True
        self.fitness = result

    def get_random(self):
        r = random.random()
        if r < 0.3:
            return math.inf
        return 0
        #return random.choice([0,0,math.inf])

    def randomize(self):
        while not self.is_valid:
            i += 1
            self.grid = []
            for x in range(Individual.grid_size):
                self.grid.append([self.get_random() for y in range(Individual.grid_size)])
            self.calculate_fitness()
        logger.debug('Randomized ' + str(self) + ' after ' + str(i) + ' tries.')

    def mutate(self):
        for x,line in enumerate(self.grid):
            for y,cell in enumerate(line):
                if random.random() < Individual.mutation_prob:
                    store = cell
                    self.grid[x][y] = 0 if cell == math.inf else math.inf
                    self.calculate_fitness()
                    if not self.is_valid:
                        self.grid[x][y] = store
                        self.calculate_fitness()

    def clone(self):
        clone = Individual()
        clone.grid = self.grid[:]
        clone.calculate_fitness()
        return clone

    def crossover(self, other):
        # strategy is to use as many blocks as possible without becoming invalid
        child = Individual()
        child.initialize()
        for x, line in enumerate(self.grid):
            for y, cell in enumerate(line):
                child.grid[x][y] = math.inf if (self.grid[x][y] == math.inf or other.grid[x][y] == math.inf) else 0
                child.calculate_fitness()
                if not child.is_valid:
                    child.grid[x][y] = 0
        child.calculate_fitness()
        return child

    def __repr__(self):
        return str(id(self)) + '@' + str(self.fitness)

    def gradient_flip(self, tries=100):
        # flip a tile and keep it if the fitness increases
        # will climb the current slope, so a recipe for local optima
        f = self.fitness
        for t in range(tries):
            cf = self.fitness
            x = random.randrange(Individual.grid_size)
            y = random.randrange(Individual.grid_size)
            self.flip(x,y)
            if self.fitness <= cf:
                # it did not do anything, flip it back
                self.flip(x,y)
        logger.debug(str(self) + ' gradient flipped for ' + str(self.fitness - f))

    def mutate(self, tries = 50):
        # same as gradient_flip but without the requirement to increase 
        # the fitness
        f = self.fitness
        for t in range(tries):
            cf = self.fitness
            x = random.randrange(Individual.grid_size)
            y = random.randrange(Individual.grid_size)
            self.flip(x,y)
        logger.debug(str(self) + ' mutated for ' + str(self.fitness - f))

    def flip(self, x, y):
        old_fitness = self.fitness
        self.grid[x][y] = 0 if self.grid[x][y] > 0 else math.inf
        self.calculate_fitness()
        if not self.is_valid:
            # unlock the tile and reset the fitness
            self.grid[x][y] = 0
            self.fitness = old_fitness

    def show_window(self):
        display = pygame.display.set_mode((1000,1000))
        game = Game()
        for (x,y), tile in game.grid.items():
            if self.grid[x][y] > 0:
                tile.block()
        game.show_waypoints()
        game.make_path()
        game.show_path()
        for tile in game.grid.values():
            tile.draw(display)
        pygame.display.update()
        terminated = False
        while not terminated:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminated = True

class Population(object):

    size = 10

    def __init__(self):
        self.individuals = []
        self.generation = 1

    def initialize(self):
        logger.debug('Starting Population initialization')
        for s in range(len(self.individuals),Population.size):
            i = Individual()
            i.randomize()
            self.individuals.append(i)
        logger.debug('Finished Population initialization')
        self.individuals.sort(key=lambda i: i.fitness, reverse=True)

    def evolve(self):
        # advance to the next generation
        self.sort()
        # two times clone the leader and gradient_flip it
        winner = self.individuals[0]
        for pos in [-1,-2]:
            clone = winner.clone()
            clone.gradient_flip()
            self.individuals[pos] = clone
        # mutate a clone of the winner
        clone = winner.clone()
        clone.mutate()
        self.individuals[-3] = clone
        # gradient_flip the second
        self.individuals[1].gradient_flip()
        # mutate the third and fourth
        self.individuals[2].mutate()
        self.individuals[3].mutate()
        self.sort()
        self.generation += 1


    def sort(self):
        self.individuals.sort(key=lambda i: i.fitness, reverse=True)


    def repr_fitness(self):
        return str(self.individuals)
                

if __name__ == '__main__':
    i = Individual()
    i.grid = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, 0, math.inf, math.inf, math.inf, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, math.inf, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, math.inf, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, 0, math.inf, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, math.inf, math.inf, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, 0, 0, math.inf, 0, 0, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, math.inf, 0, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, math.inf, math.inf, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, 0, 0, math.inf, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, 0, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, math.inf, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, math.inf, 0, math.inf, 0, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, math.inf, 0, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    i.calculate_fitness()
    #i.show_window()
    p = Population()
    p.initialize()
    for g in range(5):
        p.evolve()
        winner = p.individuals[0]
        winner.show_window()
        logger.debug(winner.grid)
        logger.debug(p.repr_fitness())
