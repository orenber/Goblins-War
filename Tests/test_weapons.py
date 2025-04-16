import unittest
from unittest.mock import MagicMock, patch
import pygame
from Play.weapons import Weapon, Gun, Bullet  # Update with your import path
from Utility import Direction


class TestWeaponsBase(unittest.TestCase):
    def setUp(self):
        # Mock environment
        self.mock_env = MagicMock()
        self.mock_env.win = MagicMock()

        # Test weapon
        self.weapon = Weapon(environment=self.mock_env)

    def test_initialization(self):
        """Test base weapon initialization"""
        self.assertEqual(self.weapon.velocity, 0)
        self.assertEqual(self.weapon.power, 0)
        self.assertEqual(self.weapon._environment, self.mock_env)
        self.assertIsNone(self.weapon.owner)


class TestGun(unittest.TestCase):
    def setUp(self):
        # Mock environment
        self.mock_env = MagicMock()
        self.mock_env.win = MagicMock()

        # Test gun
        self.gun = Gun(environment=self.mock_env)

        # Mock bullet
        self.bullet_patcher = patch('Play.weapons.Bullet')
        self.mock_bullet = self.bullet_patcher.start()
        self.mock_bullet_instance = MagicMock()
        self.mock_bullet.return_value = self.mock_bullet_instance

    def tearDown(self):
        self.bullet_patcher.stop()

    def test_initialization(self):
        """Test gun initialization values"""
        self.assertEqual(self.gun.power, 8)
        self.assertEqual(self.gun.velocity_x, 20)
        self.assertEqual(self.gun.velocity_y, 20)
        self.assertEqual(self.gun.target_x, Direction['left'].value)
        self.assertEqual(self.gun.target_y, Direction['up'].value)
        self.assertEqual(len(self.gun.bullets), 0)
        self.assertEqual(len(self.gun.bullets_moving), 0)
        self.assertEqual(len(self.gun.physics_objects), 0)

    def test_velocity_properties(self):
        """Test velocity property getters/setters"""
        # Test velocity_x
        self.gun.velocity_x = 30
        self.assertEqual(self.gun.velocity_x, 30)

        # Test velocity_y
        self.gun.velocity_y = 20
        self.assertEqual(self.gun.velocity_y, 20)

    def test_target_properties(self):
        """Test target direction properties"""
        # Test target_x
        self.gun.target_x = Direction['right']
        self.assertEqual(self.gun.target_x, Direction['right'].value)

        # Test target_y
        self.gun.target_y = Direction['down']
        self.assertEqual(self.gun.target_y, Direction['down'].value)

    def test_set_target(self):
        """Test setting both target directions"""
        self.gun.set_target(Direction['left'], Direction['up'])
        self.assertEqual(self.gun.target_x, Direction['left'].value)
        self.assertEqual(self.gun.target_y, Direction['up'].value)

    def test_load_bullets(self):
        """Test loading bullets into the gun"""
        bullets_to_load = 6
        self.gun.load(bullets_to_load)

        # Verify correct number of bullets were created
        self.assertEqual(len(self.gun.bullets), bullets_to_load)
        self.assertEqual(self.mock_bullet.call_count, bullets_to_load)

    def test_activate_with_bullets(self):
        """Test firing the gun with bullets available"""
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
        """Test firing the gun when out of ammo"""
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


class TestBullet(unittest.TestCase):
    def setUp(self):
        # Initialize pygame for testing
        pygame.init()

        # Create a test bullet
        self.bullet = Bullet()

        # Create a mock screen
        self.mock_screen = MagicMock()
        self.mock_screen.get_height.return_value = 600

    def tearDown(self):
        pygame.quit()

    def test_initial_properties(self):
        """Test default bullet properties"""
        self.assertEqual(self.bullet.position_x, 0)
        self.assertEqual(self.bullet.position_y, 0)
        self.assertEqual(self.bullet.size, 3)
        self.assertEqual(self.bullet.color, (0, 0, 0))

    def test_position_properties(self):
        """Test position property getters/setters"""
        # Test position_x
        test_x = 150
        self.bullet.position_x = test_x
        self.assertEqual(self.bullet.position_x, test_x)

        # Test position_y with positive value
        test_y = 300
        self.bullet.position_y = test_y
        self.assertEqual(self.bullet.position_y, test_y)

        # Test position_y with negative value (should clamp to 0)
        self.bullet.position_y = -50
        self.assertEqual(self.bullet.position_y, 0)

    def test_position_on_canvas_y(self):
        """Test canvas y-position conversion"""
        # Set test values
        screen_height = 600
        bullet_y = 200
        self.mock_screen.get_height.return_value = screen_height

        # Test conversion
        self.bullet.position_y = bullet_y
        expected_canvas_y = screen_height - bullet_y
        self.assertEqual(self.bullet.position_on_canvas_y(self.mock_screen), expected_canvas_y)

    @patch('pygame.draw.circle')
    def test_draw(self, mock_draw):
        """Test bullet drawing"""
        # Set bullet properties
        self.bullet.position_x = 100
        self.bullet.position_y = 200
        self.bullet.size = 5
        self.bullet.color = (255, 0, 0)  # Red

        # Call draw
        self.bullet.draw(self.mock_screen)

        # Verify pygame.draw.circle was called
        expected_y = 600 - 200  # screen height - position_y
        mock_draw.assert_called_once_with(
            self.mock_screen,
            (255, 0, 0),  # color
            (100, expected_y),  # position
            5  # radius
        )


if __name__ == '__main__':
    unittest.main()
