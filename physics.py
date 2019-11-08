from timer_utility import RepeatedTimer
import math
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from time import sleep
from multiprocessing import Process




class ObjectProp(object):

    def __init__(self,**attr):

        setup = self.set_setup(attr)
        self.x = setup['x']
        self.y = setup['y']
        self.z = setup['z']
        self.t = setup['t']
        self.angle = setup['angle']
        self.velocity = setup['v']
        self.mass = setup['mass']
        self.time_stamp = setup['time_stamp']
        self._stable = False

        self.gravety = 9.8
        self.surface_x = setup['surface_x']
        self.surface_y = setup['surface_y']
        self.surface_z = setup['surface_z']

        # protected
        self._command = []
        pass

    @property
    def command(self):
        return self.__command

    @command.setter
    def command(self, command):
        # check if the command is lambda expression
        if callable(command):

            self._command = command

    def set_setup(self, prop: dict)->dict:

        default = {'x':  0, 'y': 0, 'z': 0, 'angle': 0, 'v': 0, 't': 0, 'mass': 1
        ,'surface_x': 0, 'surface_y': 0, 'surface_z': 0, 'time_stamp': 0.01, 'command':''}
        setup = default.copy()
        setup.update(prop)
        return setup

    def throw(self,vx: float = 0, vy: float = 0):
        print( "starting..." )
        self.__rt = RepeatedTimer(self.time_stamp, self.movement, vx, vy)
        try:
            self.__rt.start()

            # your long-running job goes here...



        finally:
            print('finis')
            #self.__rt.stop()

    def movement(self, vx: float = 0, vy: float = 0,vz: float = 0):
        self._stable = False
        self.t = self.time_stamp + self.t+0.05
        t = self.t

        self.z = self.surface_z + vz * t
        self.x = self.surface_x + vx * t
        self.y = self.surface_y + vy * t - 0.5 * self.gravety * math.pow(t, 2)

        if  self.surface_y >= self.y:

            self.__rt.stop()
            self._stable = True

        self.update()

    def update(self):
        self._command(self)

        pass


fig = plt.figure()
ax = plt.axes( xlim=(0, 10000), ylim=(0, 10000) )
ball_scatter = ax.scatter( 0, 0, c='r', marker='o' )
ball_scatter2 = ax.scatter( 0, 0, c='g', marker='o' )

def update_position(prop):
    print( "ball_1  X:{} , Y:{}".format( prop.x, prop.y ) )
    pass

def update_position2(prop2):
    print("ball_2  X:{} , Y:{}".format(prop2.x, prop2.y))
    pass


def main():

    ball = ObjectProp()
    ball.command = lambda prop: update_position(prop)

    ball2 = ObjectProp()
    ball2.command = lambda prop: update_position2(prop)
    ball.throw(100,100)
    ball2.throw(1500,100)



if __name__ == "__main__":
    main()



