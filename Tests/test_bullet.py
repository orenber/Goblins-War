import unittest
from unittest.mock import MagicMock, patch
import pygame
from Play.weapons import Bullet  # Update with your actual import path


class TestBullet(unittest.TestCase):
    def setUp(self):
        # Initialize pygame for testing (needed for surface creation)
        pygame.init()

        # Create a test bullet instance
        self.bullet = Bullet()

        # Create a mock screen surface
        self.mock_screen = MagicMock()
        self.mock_screen.get_height.return_value = 600

    def tearDown(self):
        pygame.quit()

    def test_draw(self):
        """Test drawing the bullet on a surface"""
        # Set bullet properties
        self.bullet.position_x = 100
        self.bullet.position_y = 200  # Will be converted to canvas y
        self.bullet.size = 5
        self.bullet.color = (255, 0, 0)  # Red

        # Call draw method
        self.bullet.draw(self.mock_screen)

        # Verify pygame.draw.circle was called with correct parameters
        # Calculate expected canvas y position
        expected_y = self.mock_screen.get_height() - self.bullet.position_y

        # Check if pygame.draw.circle was called correctly
        self.mock_screen.get_height.assert_called_once()

        # Get all calls to pygame.draw.circle
        draw_calls = [args[0] for args, _ in self.mock_screen.method_calls if args[0] == 'draw']

        # Verify at least one draw call was made
        self.assertGreaterEqual(len(draw_calls), 1)

        # Alternative verification method
        found = False
        for call in self.mock_screen.method_calls:
            if call[0] == 'draw' and len(call[1]) > 0 and call[1][0] == 'circle':
                # Verify circle drawing parameters
                args = call[1]
                self.assertEqual(args[1], (100, expected_y))  # position
                self.assertEqual(args[2], 5)  # size
                found = True
        self.assertTrue(found, "pygame.draw.circle not called with expected parameters")

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

    def test_default_properties(self):
        """Test default property values"""
        self.assertEqual(self.bullet.position_x, 0)
        self.assertEqual(self.bullet.position_y, 0)
        self.assertEqual(self.bullet.size, 3)  # Default from your implementation
        self.assertEqual(self.bullet.color, (0, 0, 0))  # Default black

    @patch('pygame.draw.circle')
    def test_draw_with_mocked_pygame(self, mock_draw):
        """Alternative draw test with mocked pygame.draw"""
        # Set bullet properties
        self.bullet.position_x = 100
        self.bullet.position_y = 200
        self.bullet.size = 5
        self.bullet.color = (255, 0, 0)

        # Setup mock screen
        mock_screen = MagicMock()
        mock_screen.get_height.return_value = 600

        # Call draw
        self.bullet.draw(mock_screen)

        # Verify pygame.draw.circle was called
        expected_y = 600 - 200  # screen height - position_y
        mock_draw.assert_called_once_with(
            mock_screen,
            (255, 0, 0),  # color
            (100, expected_y),  # position
            5  # radius
        )


if __name__ == '__main__':
    unittest.main()
