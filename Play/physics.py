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
        self.speed = 0.1
        self.velocity = 0
        self.mass = 1
        self.time_stamp = 0.01
        self._stable = True
        self.bottom = 0

        self.gravity = 9.8
        self.surface_x = 0
        self.surface_y = 0
        self.surface_z = 0
        self.rt = RepeatedTimer(self.time_stamp, self._movement)

        # protected
        self.__command = []
        self.__command_stop =[]

        self.set_setup(**attr)
        pass

    @property
    def command_update(self):
        return self.__command

    @command_update.setter
    def command_update(self, command):
        # check if the command is lambda expression
        if callable(command):

            self.__command = command

    @property
    def command_stop(self):
        return self.__command_stop

    @command_stop.setter
    def command_stop(self, command):
        # check if the command is lambda expression
        if callable(command):

            self.__command_stop = command

    def set_setup(self, **prop):

        default = ['x', 'y', 'z', 'angle', 'v', 't', 'mass', 'bottom', 'gravity',
                   'surface_x', 'surface_y', 'surface_z', 'time_stamp', 'command']
        # check if filed value is inside defulte filed
        fileds = list(prop.keys())
        (state, diff) = is_member(fileds, default)
        print(diff)

        assert state, 'their is no such member '
        # setup = default.copy()
        # setup.update(prop)
        for name in prop.keys():
            self.__setattr__(name, prop[name])

    def throw(self,vx: float = 0, vy: float = 0):
        print("starting...")
        self.rt.start_input_args = vx, vy
        self.rt.stop_function = self._stop_movment

        try:
            self.rt.start()

            # your long-running job goes here...

        finally:
            print('finis')

            #self.rt.stop()

    def _movement(self, vx: float = 0, vy: float = 0,vz: float = 0):
        self._stable = self.rt.is_running
        self.t += self.time_stamp + self.speed
        t = self.t
        # self.z = self.surface_z + vz * t
        self.x = self.surface_x + vx * t
        self.y = self.surface_y + vy * t - 0.5 * self.gravity * math.pow(t, 2)

        if self.bottom >= self.y:

            self.rt.stop()
            self._stable = True
            self.t = 0

        self.update()

    def _stop_movment(self):
        if callable(self.command_stop):
            self.command_stop(self)

    def update(self):
        if callable(self.command_update):
            self.command_update(self)




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


def stop_ball(prop2):
    print( "ball_2 stop it  X:{} , Y:{}".format( prop2.x, prop2.y ) )


def main():

    ball = ObjectProp(time_stamp=0.01)
    ball.command_update = lambda prop: update_position(prop)

    ball2 = ObjectProp(time_stamp=0.01)
    ball2.command_update = lambda prop: update_position2(prop)
    ball2.command_update = lambda prop: update_position2(prop)
    ball2.command_stop = lambda prop: stop_ball(prop)

    ball.throw(10,10)
    ball2.throw(150,10)


if __name__ == "__main__":
    main()



