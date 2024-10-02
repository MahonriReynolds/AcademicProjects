
from matplotlib import pyplot as plt
import numpy as np
from Flock import Flock


class Field():
    def __init__(self, flock_sizes) -> None:
        # make an array of center points to record each Flock's center
        self.__centers = np.array([])
        # make a list of Flocks
        self.__flocks = []
        
        # for each flock size passed in, assign a matplotlib styling
        # and make a Flock of that size
        for size, style in zip(flock_sizes, ('bo', 'gs', 'rp', 'go', 'rs', 'bp')):
            new_flock = Flock(size, style)
            # add new Flock to flocks list
            self.__flocks.append(new_flock)
        
        # make matplotlib figure and 3d subplot
        self.__fig = plt.figure(figsize=(12, 8))
        self.__subplot = self.__fig.add_subplot(projection='3d')


    def view(self) -> None:   
        # clear current points to not overlap with new points
        self.__subplot.clear()
        # plot out the center of the map for reference
        self.__subplot.plot(0, 0, 0, 'ko')
                
        # make a temporary list of center points
        centers = []
        for flock in self.__flocks:
            # grab all the data returned by the flock method
            coords, styling, center = flock.flock(self.__centers)
            # plot out all the points in the current Flock
            self.__subplot.plot(*coords, styling)
            # add the Flock's center to the temporary centers list
            centers.append(center)
                
        # update this Field's centers with the temporary centers list
        self.__centers = np.array(centers)

        # set the dimensions of the 3d plot so it doesn't auto adjust
        # setting plt.autoscale(False) didn't work?
        self.__subplot.set_xlim3d([-200, 200])
        self.__subplot.set_xlabel('X')
        self.__subplot.set_ylim3d([-200, 200])
        self.__subplot.set_ylabel('Y')
        self.__subplot.set_zlim3d([-200, 200])
        self.__subplot.set_zlabel('Z')
            
        # update the plot and pause just long enough to see it
        self.__fig.canvas.flush_events()
        plt.pause(0.01)
        # self.__fig.show()
     
