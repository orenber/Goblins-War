from Utility.timer_utility import RepeatedTimer
import math
import matplotlib.pyplot as plt
from Utility import is_member


class ObjectProp(object):

    def __init__(self, **attr):

        self.x = 0
        self.y = 0
        self.z = 0
        self.t = 0
        self.angle = 0
        self.velocity = 0
        self.mass = 1
        self.time_stamp = 0.01
        self._stable = True

        self.gravety = 9.8
        self.surface_x = 0
        self.surface_y = 0
        self.surface_z = 0
        self.rt = RepeatedTimer(self.time_stamp, self.movement)

        # protected
        self.__command = []

        self.set_setup(**attr)
        pass

    @property
    def command(self):
        return self.__command

    @command.setter
    def command(self, command):
        # check if the command is lambda expression
        if callable(command):

            self.__command = command

    def set_setup(self, **prop):

        default = {'x':  0, 'y': 0, 'z': 0, 'angle': 0, 'v': 0, 't': 0, 'mass': 1
        , 'surface_x': 0, 'surface_y': 0, 'surface_z': 0, 'time_stamp': 0.01, 'command':''}
        # check if filed value is inside defulte filed
        fileds = list(prop.keys())
        state = is_member(fileds, default.keys())

        assert state, 'thar is no such member '
        # setup = default.copy()
        # setup.update(prop)
        for name in prop.keys():
            self.__setattr__(name, prop[name])

    def throw(self,vx: float = 0, vy: float = 0):
        print( "starting..." )
        self.rt.args = (vx, vy)
        try:
            self.rt.start()

            # your long-running job goes here...



        finally:
            print('finis')

            #self.rt.stop()

    def movement(self, vx: float = 0, vy: float = 0,vz: float = 0):
        self._stable = self.rt.is_running
        self.t = self.time_stamp + self.t+0.1
        t = self.t

        self.z = self.surface_z + vz * t
        self.x = self.surface_x + vx * t
        self.y = self.surface_y + vy * t - 0.5 * self.gravety * math.pow(t, 2)

        if  0 >= self.y:

            self.rt.stop()
            self._stable = True
            self.t = 0

        self.update()


    def update(self):
        self.command(self)

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



