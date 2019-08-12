import time
import math



class ObjectProp(object):

    def __init__(self,**attr):

        setup = self.set_setup(attr)
        self.x = setup['x']
        self.y = setup['y']
        self.z = setup['z']
        self.angle = setup['angle']
        self.velocity = setup['v']
        self.mass = setup['mass']
        self._stable = False

        self.gravety = 9.8
        self.surface_x = setup['surface_x']
        self.surface_y = setup['surface_y']
        self.surface_z = setup['surface_z']
        pass


    def set_setup(self, prop: dict)->dict:

        default = {'x':  0, 'y': 0, 'z': 0, 'angle': 0, 'v': 0, 'mass': 1
        ,'surface_x': 0, 'surface_y': 0, 'surface_z': 0}
        setup = default.copy()
        setup.update(prop)
        return setup

    def throw(self,vx:float = 0, vy:float = o):

        t = self.time
        x0 = self.x
        y0 = self.y

        self.x = x0 + vx*t
        self.y = y0  +vy* t-0.5*self.gravety * math.pow(t,2)

        if self.surface_x == self.x and self.surface_y == self.y:
           self._stable = True

        else:
            self._stable = False

        pass



