from unittest import TestCase
from Play.physics import ObjectProp


class TestObjectProp(TestCase):

    def setUp(self):
        self.obj = ObjectProp(time_stamp=0.01)

    def test_command_update(self):
        self.obj.command_update = lambda prop: update_position(prop)
        command_update = self.obj.command_update

    def test_set_setup(self):
        self.obj.set_setup(x=50, y=20, angle=30, v=90, mass=50, bottom=0, gravity=9.8,
                           surface_x=0, surface_y=0, time_stamp=0.5)
        self.assertEqual(self.obj.x, 50, 'x not match')
        self.assertEqual(self.obj.y, 20, 'y not match')
        self.assertEqual(self.obj.angle, 30, 'angle not match')
        self.assertEqual(self.obj.v, 90, 'v not match')
        self.assertEqual(self.obj.mass, 50, 'mass not match')
        self.assertEqual(self.obj.bottom, 0, 'bottom not match')
        self.assertEqual(self.obj.gravity, 9.8, 'gravity not match')
        self.assertEqual(self.obj.surface_x, 0, 'surface_x not match')
        self.assertEqual(self.obj.surface_y, 0, 'surface_y not match')
        self.assertEqual(self.obj.time_stamp, 0.5, 'time_stamp not match')

    def test_throw(self):
        self.obj.set_setup(x=50, y=20, angle=30, v=90, mass=50, bottom=10, gravity=9.8,
                           surface_x=0, surface_y=0, time_stamp=0.01)
        self.obj.command_update = lambda prop: update_position(prop)
        self.obj.throw(50,  100)

    def test_command_stop(self):
        self.obj.command_stop = lambda prop: stop_position(prop)
        command_stop = self.obj.command_stop

    def test_stop_movment(self):
        self.obj.set_setup( x=50, y=0, angle=30, v=90, mass=50, bottom=10, gravity=9.8,
                            surface_x=0, surface_y=0, time_stamp=0.1 )
        self.obj.command_update = lambda prop: update_position(prop)
        self.obj.command_stop = lambda prop: stop_position(prop)
        self.obj.throw(50, 350)


def update_position(prop):
    print( "ball_1  X:{} , Y:{}".format( prop.x, prop.y ) )

    pass


def stop_position(prop):
    print("ball_1 stop it  X:{} , Y:{}".format( prop.x, prop.y ) )

    pass