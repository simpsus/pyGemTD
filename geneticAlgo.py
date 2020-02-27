from pyGemTD import A_star, cartesian_distance
import math
import random
import logging
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

    def randomize(self):
        i = 0
        while not self.is_valid:
            i += 1
            self.grid = []
            for x in range(Individual.grid_size):
                self.grid.append([random.choice([0,0,math.inf]) for y in range(Individual.grid_size)])
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

class Population(object):

    size = 20

    def __init__(self):
        self.individuals = []

    def initialize(self):
        logger.debug('Starting Population initialization')
        for s in range(len(self.individuals),Population.size):
            i = Individual()
            i.randomize()
            self.individuals.append(i)
        logger.debug('Finished Population initialization')
        self.individuals.sort(key=lambda i: i.fitness, reverse=True)

    def repr_fitness(self):
        return str(self.individuals)
                

if __name__ == '__main__':
    i = Individual()
    i.grid = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, 0, math.inf, math.inf, math.inf, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, math.inf, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, math.inf, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, 0, math.inf, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, math.inf, math.inf, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, 0, 0, math.inf, 0, 0, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, math.inf, 0, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, math.inf, math.inf, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, 0, 0, math.inf, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, 0, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, math.inf, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, math.inf, 0, math.inf, 0, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, math.inf, 0, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    i.calculate_fitness()
    print('Clone')
    c = i.clone()
    print('Mutate')
    i.mutate()
    print('Crossover')
    c2 = i.crossover(c)
    print(c,i,c2)
    #p = Population()
    #p.initialize()
    #print(p.repr_fitness())