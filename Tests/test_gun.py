import unittest
from unittest.mock import MagicMock, patch
from Play.weapons import Gun, Bullet

from Utility import Direction


class TestGun(unittest.TestCase):
    def setUp(self):
        # Create a mock environment
        self.mock_env = MagicMock()
        self.mock_env.win = MagicMock()

        # Initialize gun with mock environment
        self.gun = Gun(environment=self.mock_env)

        # Mock bullet class
        self.bullet_patcher = patch('Play.weapons.Bullet')
        self.mock_bullet = self.bullet_patcher.start()
        self.mock_bullet_instance = MagicMock()
        self.mock_bullet.return_value = self.mock_bullet_instance

    def tearDown(self):
        self.bullet_patcher.stop()

    def test_load(self):
        """Test loading bullets into the gun"""
        bullets_to_load = 6
        self.gun.load(bullets_to_load)

        # Verify correct number of bullets were created
        self.assertEqual(len(self.gun.bullets), bullets_to_load)
        self.assertEqual(self.mock_bullet.call_count, bullets_to_load)

    def test_activate_with_bullets(self):
        """Test activating gun with bullets available"""
        # Load some bullets
        self.gun.load(3)

        # Set initial state
        initial_bullets = len(self.gun.bullets)
        initial_moving = len(self.gun.bullets_moving)

        # Activate gun
        pos_x, pos_y = 10, 10
        self.gun.activate(pos_y, pos_x)

        # Verify bullet was moved from bullets to bullets_moving
        self.assertEqual(len(self.gun.bullets), initial_bullets - 1)
        self.assertEqual(len(self.gun.bullets_moving), initial_moving + 1)

        # Verify physics object was created
        self.assertEqual(len(self.gun.physics_objects), 1)

        # Verify bullet position was updated
        self.mock_bullet_instance.position_x = pos_x
        self.mock_bullet_instance.position_y = pos_y

    def test_activate_without_bullets(self):
        """Test activating gun when out of ammo"""
        # Don't load any bullets
        with patch('builtins.print') as mock_print:
            self.gun.activate(10, 10)
            mock_print.assert_called_with('gun out of ammo')

    def test_update_position(self):
        """Test updating bullet position from physics"""
        # Add a mock bullet to moving list
        mock_bullet = MagicMock()
        self.gun.bullets_moving.append(mock_bullet)

        # Create a mock physics prop
        mock_prop = MagicMock()
        mock_prop.x = 100
        mock_prop.y = 200

        # Call update
        self.gun.update_position(mock_prop)

        # Verify bullet position was updated
        self.assertEqual(mock_bullet.position_x, 100)
        self.assertEqual(mock_bullet.position_y, 200)

    def test_stop_position(self):
        """Test stopping a bullet's movement"""
        # Add a mock bullet to moving list
        mock_bullet = MagicMock()
        self.gun.bullets_moving.append(mock_bullet)

        # Create a mock physics prop
        mock_prop = MagicMock()

        # Call stop
        self.gun.stop_position(mock_prop)

        # Verify bullet was removed
        self.assertEqual(len(self.gun.bullets_moving), 0)

    def test_draw(self):
        """Test drawing the gun and bullets"""
        # Add some mock bullets to moving list
        mock_bullet1 = MagicMock()
        mock_bullet2 = MagicMock()
        self.gun.bullets_moving.extend([mock_bullet1, mock_bullet2])

        # Call draw
        self.gun.draw()

        # Verify each bullet was drawn
        mock_bullet1.draw.assert_called_with(self.mock_env.win)
        mock_bullet2.draw.assert_called_with(self.mock_env.win)

    def test_velocity_properties(self):
        """Test velocity property getters/setters"""
        # Test velocity_x
        self.gun.velocity_x = 30
        self.assertEqual(self.gun.velocity_x, 30)

        # Test velocity_y
        self.gun.velocity_y = 20
        self.assertEqual(self.gun.velocity_y, 20)

    def test_target_properties(self):
        """Test target direction property getters/setters"""
        # Test target_x
        self.gun.target_x = Direction['right']
        self.assertEqual(self.gun.target_x, Direction['right'].value)

        # Test target_y
        self.gun.target_y = Direction['down']
        self.assertEqual(self.gun.target_y, Direction['down'].value)

    def test_set_target(self):
        """Test setting both target directions at once"""
        self.gun.set_target(Direction['left'], Direction['up'])
        self.assertEqual(self.gun.target_x, Direction['left'].value)
        self.assertEqual(self.gun.target_y, Direction['up'].value)


if __name__ == '__main__':
    unittest.main()

