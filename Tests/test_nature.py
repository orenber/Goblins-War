import unittest
import pygame
import os
import tempfile
from unittest.mock import MagicMock, patch
from Play.environment import Nature  # Update with your actual import path


class TestNature(unittest.TestCase):
    def setUp(self):
        # Initialize pygame for testing
        pygame.init()

        # Create a temporary directory for test resources
        self.temp_dir = tempfile.TemporaryDirectory()

        # Create test image directory structure
        self.test_images_path = os.path.join(self.temp_dir.name, 'Resources', 'images', 'Canvas')
        os.makedirs(self.test_images_path)

        # Create a test background image
        self.test_bg_file = 'test_bg.jpg'
        test_bg_path = os.path.join(self.test_images_path, self.test_bg_file)

        # Create a dummy image file
        pygame.image.save(pygame.Surface((800, 600)), test_bg_path)

        # Create test sound directory
        self.test_sound_path = os.path.join(self.temp_dir.name, 'Resources', 'sound')
        os.makedirs(self.test_sound_path)

        # Create a dummy sound file
        self.test_sound_file = 'test_sound.mp3'
        with open(os.path.join(self.test_sound_path, self.test_sound_file), 'wb') as f:
            f.write(b'dummy sound data')

        # Initialize Nature with test paths
        self.nature = Nature()
        self.nature.images_path = ('Resources', 'images', 'Canvas')
        self.nature.sound_path = ('Resources', 'sound')
        self.nature.background_file = self.test_bg_file
        self.nature.music_file = self.test_sound_file

    def tearDown(self):
        # Clean up temporary directory
        self.temp_dir.cleanup()
        pygame.quit()

    def test_draw(self):
        """Test that draw method works without errors"""
        # Create a test display
        test_surface = pygame.Surface((500, 500))
        self.nature.win = test_surface

        # Call draw method
        try:
            self.nature.draw()
            # If we get here, it worked
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"draw() method failed with exception: {e}")

    def test_move_background(self):
        """Test background movement logic"""
        # Store initial positions
        initial_x1 = self.nature.bg_position_x1
        initial_x2 = self.nature.bg_position_x2

        # Move background
        self.nature.move_background()

        # Verify positions changed
        self.assertNotEqual(self.nature.bg_position_x1, initial_x1)
        self.assertNotEqual(self.nature.bg_position_x2, initial_x2)

        # Verify positions are properly reset when scrolled off screen
        self.nature.bg_position_x1 = -self.nature.background.get_width() - 1
        self.nature.bg_position_x2 = -self.nature.background.get_width() - 1
        self.nature.move_background()
        self.assertEqual(self.nature.bg_position_x1, self.nature.background.get_width())
        self.assertEqual(self.nature.bg_position_x2, self.nature.background.get_width())

    def test_images_path_property(self):
        """Test images_path getter/setter"""
        test_path = ('new', 'path', 'to', 'images')
        self.nature.images_path = test_path
        self.assertEqual(self.nature.images_path, os.path.abspath(os.path.join(*test_path)))

    def test_sound_path_property(self):
        """Test sound_path getter/setter"""
        test_path = ('new', 'path', 'to', 'sounds')
        self.nature.sound_path = test_path
        self.assertEqual(self.nature.sound_path, os.path.abspath(os.path.join(*test_path)))

    def test_background_property(self):
        """Test background getter/setter"""
        # Test setting a valid surface
        test_surface = pygame.Surface((100, 100))
        self.nature.background = test_surface
        self.assertEqual(self.nature.background, test_surface)

        # Test setting invalid value
        with self.assertRaises(ValueError):
            self.nature.background = "not a surface"

    def test_load_image(self):
        """Test image loading functionality"""
        # Test loading existing image
        loaded_image = self.nature.load_image(self.test_bg_file)
        self.assertIsInstance(loaded_image, pygame.Surface)

        # Test loading non-existent image
        with self.assertRaises(FileNotFoundError):
            self.nature.load_image("nonexistent.jpg")

    @patch('pygame.mixer.music.play')
    @patch('pygame.mixer.music.load')
    @patch('pygame.mixer.init')
    def test_play_sound(self, mock_init, mock_load, mock_play):
        """Test sound playback functionality"""
        # Test with default sound file
        self.nature.play_sound()
        mock_init.assert_called_once()
        mock_load.assert_called_with(os.path.join(self.nature.sound_path, self.test_sound_file))
        mock_play.assert_called_with(-1, 0.0)

        # Test with specific sound file
        mock_init.reset_mock()
        mock_load.reset_mock()
        mock_play.reset_mock()

        test_file = "custom_sound.mp3"
        self.nature.play_sound(test_file)
        mock_load.assert_called_with(os.path.join(self.nature.sound_path, test_file))

    def test_position_on_canvas_y(self):
        """Test coordinate conversion"""
        test_y = 300
        expected = self.nature.win.get_height() - test_y
        self.assertEqual(self.nature.position_on_canvas_y(test_y), expected)

    def test_initialization(self):
        """Test that initialization sets up proper defaults"""
        self.assertEqual(self.nature.width, 500)
        self.assertEqual(self.nature.high, 500)
        self.assertIsNotNone(self.nature.background)
        self.assertIsInstance(self.nature.win, pygame.Surface)


if __name__ == '__main__':
    unittest.main()