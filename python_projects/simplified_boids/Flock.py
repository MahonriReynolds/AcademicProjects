
import numpy as np
from random import uniform
from Boid import Boid


class Flock():
    def __init__(self, boid_count, boid_style) -> None:
        # pick random point in the Field to spawn this Flock
        self.__center = np.array((
            uniform(-100, 100), 
            uniform(-100, 100), 
            uniform(-100, 100)
        ))
        
        # start a list of Boid
        self.__boids = []
        for _ in range(boid_count):
            # pick a random offset to place the Boid off the center of this Flock
            offset = np.array((
                uniform(-30, 30), 
                uniform(-30, 30), 
                uniform(-30, 30)
            ))
            
            # make a random velocity for the Boid to kick things off
            velocity = np.array((
                uniform(-5, 5), 
                uniform(-5, 5), 
                uniform(-5, 5)
            ))
            
            # make the Boid and use the offset and velocity values to init it
            # then add it to this Flock's list of Boids
            new_boid = Boid((self.__center + offset), velocity)
            self.__boids.append(new_boid)
        
        # set a styling for the Boid points (ex. 'ro' for red circles)
        self.__styling = boid_style
        
    
    def __get_vectors(self, b1, centers) -> np.array:
        b1_pos = b1.locate()[0]
        # get the Boid's (b1) perceived center of the flock
        vector_center = self.__center - b1_pos
        
        # set the closest distance a Boid will get to any other Boid in the flock
        # as d=
        d = 8
        
        vector_away = np.array((0.0, 0.0, 0.0))     # init - avoid others in the flock
        vector_others = np.array((0.0, 0.0, 0.0))   # init - match the direction of others in the flock
        
        # for each Boid in this Flock, get the Boid's perceived distance 
        # and direction differences and apply those to the two vectors above
        for b2 in self.__boids:
            if b1 != b2:
                b2_pos, b2_v = b2.locate()
                vector_others += b2_v
                if d > np.sqrt(np.sum((b1_pos - b2_pos)**2)):
                    vector_away -= (b2_pos - b1_pos)
        vector_others /= len(self.__boids)
        
        vector_zero = -b1_pos   # send Boid towards the center of the Field (0, 0, 0)
        
        vector_other_flocks = -(sum(centers) - self.__center)    # Boid avoids perceived center of other flocks
        
        return vector_center, vector_away, vector_others, vector_zero, vector_other_flocks
    
    
    def __set_center(self) -> np.array:
        # clear this Flock's center point
        self.__center.fill(0.0)
        
        # rebuild this Flock's center point with the updated positions of each Boid
        for boid in self.__boids:
            self.__center += boid.locate()[0]
        self.__center /= len(self.__boids)
    
    
    def flock(self, centers) -> None:
        # update center of flock to calculate Boid movements
        self.__set_center()
        
        # make a list to hold coordinate points [(x, y, z), (x, y, z)]
        coords = []
        for boid in self.__boids:
            # get updated vectors for each boid and pass them through
            boid.move(self.__get_vectors(boid, centers))
            
            # get Boid's new location and add the point to the coords list
            p = boid.locate()[0]
            coords.append(p)
        
        # transpose [(x, y, z), (x, y, z)] into [(x, x), (y, y), (z, z)]
        # for matplotlib's plot function
        coords = np.array(coords).T
        
        return coords, self.__styling, self.__center

        
        
    
