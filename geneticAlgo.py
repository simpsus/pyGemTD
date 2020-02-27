from pyGemTD import A_star, cartesian_distance
import math
import random
import logging
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(funcName)s %(lineno)d %(message)s')
logger = logging.getLogger('genetic')

class Individual(object):
    # an Individual is a gridm of zero/math.inf values

    grid_size = 40

    def __init__(self):
        self.grid = []
        self.fitness = 0
        self.is_valid = False

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
            print(str(i))
            i += 1
            self.grid = []
            for x in range(Individual.grid_size):
                self.grid.append([random.choice([0,0,math.inf]) for y in range(Individual.grid_size)])
            self.calculate_fitness()

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
            logger.debug('Individual #' + str(s))

    def repr_fitness(self):
        return str(self.individuals)
                

if __name__ == '__main__':
    i = Individual()
    i.grid = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, 0, math.inf, math.inf, math.inf, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, math.inf, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, math.inf, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, 0, math.inf, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, math.inf, math.inf, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, 0, 0, math.inf, 0, 0, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, math.inf, 0, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, math.inf, math.inf, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, 0, 0, math.inf, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, math.inf, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, 0, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, math.inf, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, math.inf, 0, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, math.inf, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, math.inf, 0, 0, math.inf, 0, 0, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, math.inf, 0, math.inf, 0, math.inf, math.inf, math.inf, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, math.inf, 0, math.inf, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, math.inf, 0, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    i.calculate_fitness()
    
    p = Population()
    p.initialize()
    print(p.repr_fitness())
