from unittest import TestCase
from Play.weapons import *

class TestGun(TestCase):

    def setUp(self):
        self.gun = Gun()

    def test_create(self):
        self.fail()

    def test_update_animation(self):
        self.fail()

    def test_load(self):
        bullets = 6
        self.gun.load(bullets)
        self.assertEqual(len(self.gun.bullets), bullets)

    def test_activate(self):
        bullets = 6
        self.gun.load(bullets)
        self.gun.activate(10,10)

