import unittest
import pygame
import os
import tempfile
from unittest.mock import MagicMock, patch
from Play.characters import Human  # Replace with your actual module path


class TestHuman(unittest.TestCase):
    def setUp(self):
        # Create a mock environment
        self.mock_env = MagicMock()
        self.mock_env.win = MagicMock()
        self.mock_env.win.get_height.return_value = 600

        # Create a temporary directory for test images
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_images_path = os.path.join(self.temp_dir.name, 'Resources', 'images', 'Hero')
        os.makedirs(self.test_images_path)

        # Create test image files
        self.test_image_files = [
            'R1.png', 'R2.png', 'R3.png', 'R4.png', 'R5.png',
            'R6.png', 'R7.png', 'R8.png', 'R9.png',
            'L1.png', 'L2.png', 'L3.png', 'L4.png',
            'L5.png', 'L6.png', 'L7.png', 'L8.png', 'L9.png',
            'standing.png'
        ]

        for filename in self.test_image_files:
            # Create empty image files
            with open(os.path.join(self.test_images_path, filename), 'wb') as f:
                f.write(b'')  # Empty file

        # Initialize human with test environment
        self.human = Human(environment=self.mock_env)
        self.human.images_path = self.test_images_path

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_set_setup(self):
        test_data = {
            'position_x': 100,
            'position_y': 200,
            'high': 190,
            'width': 70,
            'walk_direction': 'left'
        }

        self.human.set_setup(**test_data)

        self.assertEqual(self.human.position_x, 100)
        self.assertEqual(self.human.position_y, 200)
        self.assertEqual(self.human.high, 190)
        self.assertEqual(self.human.width, 70)
        self.assertEqual(self.human.walk_direction, 'left')

    def test_live_property(self):
        # Test when health > 0
        self.human.health = 50
        self.assertTrue(self.human.live)

        # Test when health <= 0
        self.human.health = -10
        self.assertFalse(self.human.live)

    def test_high_property(self):
        # Test getter
        self.human.high = 180
        self.assertEqual(self.human.high, 60)  # 180 * 1/3

        # Test setter
        self.human.high = 150
        self.assertEqual(self.human._high, 150)

    def test_width_property(self):
        # Test getter
        self.human.width = 60
        self.assertEqual(self.human.width, 20)  # 60 * 1/3

        # Test setter
        self.human.width = 90
        self.assertEqual(self.human._width, 90)

    def test_position_y_property(self):
        # Test setter with positive value
        self.human.position_y = 100
        self.assertEqual(self.human.position_y, 100 + self.human.high)

        # Test setter with negative value (should clamp to 0)
        self.human.position_y = -50
        self.assertEqual(self.human.position_y, self.human.high)

        # Test when dead (should allow negative values)
        self.human.health = -10
        self.human.position_y = -50
        self.assertEqual(self.human.position_y, -50 + self.human.high)

    def test_health_property(self):
        # Test health increase
        self.human.health = 30
        self.assertEqual(self.human.health, 130)  # Starts at 100

        # Test health decrease
        self.human.health = -40
        self.assertEqual(self.human.health, 90)

        # Test health cap at 100
        self.human.health = 50
        self.assertEqual(self.human.health, 100)

        # Test health minimum at 0
        self.human.health = -150
        self.assertEqual(self.human.health, 0)

    def test_position_on_canvas_y(self):
        self.human.position_y = 100
        self.mock_env.win.get_height.return_value = 600
        self.assertEqual(self.human.position_on_canvas_y(), 500)  # 600 - 100

    @patch('pygame.image.load')
    def test_load_image(self, mock_load):
        test_image = MagicMock()
        mock_load.return_value = test_image

        # Test successful load
        result = self.human.load_image('test.png')
        self.assertEqual(result, test_image)
        mock_load.assert_called_with(os.path.join(self.test_images_path, 'test.png'))

        # Test error handling
        mock_load.side_effect = pygame.error("Test error")
        result = self.human.load_image('invalid.png')
        self.assertIsInstance(result, pygame.Surface)

    def test_create(self):
        self.human.create()

        # Check that all animation lists were populated
        self.assertEqual(len(self.human.walk_right), 9)
        self.assertEqual(len(self.human.walk_left), 9)
        self.assertEqual(len(self.human.standing), 1)

    def test_health_bar(self):
        # Mock pygame.draw.rect
        with patch('pygame.draw.rect') as mock_rect:
            self.human.health = 80  # Set health to 80%
            self.human.hitbox = (100, 100, 50, 50)  # Set hitbox
            self.human.health_bar()

            # Should draw two rectangles (background and health)
            self.assertEqual(mock_rect.call_count, 2)

    def test_draw(self):
        # Test drawing in different states
        with patch.object(self.human, 'health_bar'), \
                patch.object(self.human._environment.win, 'blit') as mock_blit:
            # Test right walk
            self.human.move_direction = 'right'
            self.human.draw()
            mock_blit.assert_called()

            # Test left walk
            mock_blit.reset_mock()
            self.human.move_direction = 'left'
            self.human.draw()
            mock_blit.assert_called()

            # Test standing
            mock_blit.reset_mock()
            self.human.move_direction = 'down'
            self.human.draw()
            mock_blit.assert_called()

    def test_walk(self):
        # Test right walk
        start_x = self.human.position_x
        self.human.walk(5)
        self.assertEqual(self.human.position_x, start_x + 5)
        self.assertEqual(self.human.move_direction, 'right')

        # Test left walk
        start_x = self.human.position_x
        self.human.walk(-3)
        self.assertEqual(self.human.position_x, start_x - 3)
        self.assertEqual(self.human.move_direction, 'left')

    @patch.object(Human, 'physics_state')
    def test_jump(self, mock_physics):
        # Configure mock physics state
        mock_physics.rt.is_running = False

        # Test jump
        self.human.jump(10, 5)
        mock_physics.set_setup.assert_called()
        mock_physics.throw.assert_called()

    def test_stop(self):
        self.human.stop()
        self.assertEqual(self.human.move_direction, 'down')

    @patch.object(Human, 'weapon')
    @patch.object(Human, 'play_sound')
    def test_attack(self, mock_play_sound, mock_weapon):
        # Test attack
        self.human.attack()
        mock_weapon.load.assert_called_with(2)
        mock_weapon.set_target.assert_called()
        mock_weapon.activate.assert_called()
        mock_play_sound.assert_called()

    def test_update_position(self):
        mock_prop = MagicMock()
        mock_prop.x = 150
        mock_prop.y = 200

        self.human.update_position(mock_prop)
        self.assertEqual(self.human.position_x, 150)
        self.assertEqual(self.human.position_y, 200)


if __name__ == '__main__':
    unittest.main()
