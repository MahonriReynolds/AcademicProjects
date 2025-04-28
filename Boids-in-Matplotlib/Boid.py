
import numpy as np


class Boid():
    def __init__(self, position, velocity) -> None:
        self.__position = position
        self.__velocity = velocity

    # take in the various velocities calculated in flock and
    # apply them to the boid's velocity & position
    def move(self, vectors) -> None:
        self.__velocity += vectors[0] / 300     # go to center of flock
        self.__velocity += vectors[1] * 600     # avoid others in flock
        self.__velocity += vectors[2] / 10      # match direction of flock
        self.__velocity += vectors[3] / 225     # go to center of map
        self.__velocity += vectors[4] / 250     # avoid other flocks
        
        self.__velocity /= np.linalg.norm(self.__velocity) / 4  # uniform speed 
        
        self.__position += self.__velocity  # update position

    # getter for boid's values
    def locate(self) -> np.array:
        return self.__position, self.__velocity
    
