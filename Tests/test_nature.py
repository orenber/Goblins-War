import unittest
import pygame
import os
import tempfile
from unittest.mock import MagicMock, patch, call


# ---------------------------------------------------------------------------
# Inline Nature so the file is self-contained.
# In your project replace this with:  from Play.environment import Nature
# ---------------------------------------------------------------------------

class Nature:
    def __init__(self, width: int = 500, height: int = 500) -> None:
        self.__images_path = ''
        self.__sound_path = ''
        self.__background = None
        self.width = width
        self.height = height
        self.win = None

        self.bg_position_x1 = 0
        self.bg_position_y1 = 0
        self.bg_position_x2 = 0
        self.bg_position_y2 = 0

        self.images_path = ('Resources', 'images', 'Canvas')
        self.sound_path = ('Resources', 'sound')
        self.background_file = 'bg.jpg'
        self.music_file = 'music.mp3'

        self.__create()

    def __create(self) -> None:
        self.win = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Nature Environment")
        try:
            self.background = self.load_image(self.background_file)
            self.bg_position_x2 = self.background.get_width()
        except (FileNotFoundError, pygame.error) as e:
            print(f"Error loading background image: {e}")
            self.background = pygame.Surface((self.width, self.height))
            self.background.fill((0, 100, 200))
            self.bg_position_x2 = self.width

    def draw(self) -> None:
        self.win.fill((0, 0, 0))
        if self.__background:
            self.win.blit(self.__background, (self.bg_position_x1, self.bg_position_y1))
            self.win.blit(self.__background, (self.bg_position_x2, self.bg_position_y2))

    def move_background(self, speed: float = 1.4) -> None:
        self.bg_position_x1 -= speed
        self.bg_position_x2 -= speed
        bg_width = self.__background.get_width() if self.__background else self.width
        if self.bg_position_x1 + bg_width <= 0:
            self.bg_position_x1 = self.bg_position_x2 + bg_width
        if self.bg_position_x2 + bg_width <= 0:
            self.bg_position_x2 = self.bg_position_x1 + bg_width

    def position_on_canvas_y(self, position_y: float) -> float:
        if self.win is None:
            return self.height - position_y
        return self.win.get_height() - position_y

    @property
    def images_path(self) -> str:
        return self.__images_path

    @images_path.setter
    def images_path(self, images_path) -> None:
        if not images_path:
            raise ValueError("images_path must contain at least one component")
        self.__images_path = os.path.abspath(os.path.join(*images_path))
        if not os.path.exists(self.__images_path):
            print(f"Warning: Images path does not exist: {self.__images_path}")

    @property
    def sound_path(self) -> str:
        return self.__sound_path

    @sound_path.setter
    def sound_path(self, sound_path) -> None:
        if not sound_path:
            raise ValueError("sound_path must contain at least one component")
        self.__sound_path = os.path.abspath(os.path.join(*sound_path))
        if not os.path.exists(self.__sound_path):
            print(f"Warning: Sound path does not exist: {self.__sound_path}")

    @property
    def background(self):
        return self.__background

    @background.setter
    def background(self, image_background) -> None:
        if isinstance(image_background, pygame.Surface):
            self.__background = image_background
        else:
            raise ValueError("Background must be a pygame.Surface")

    def load_image(self, file: str) -> pygame.Surface:
        path = os.path.join(self.images_path, file)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Image file not found: {path}")
        image = pygame.image.load(path)
        return image.convert_alpha() if image.get_alpha() else image.convert()

    def play_sound(self, file=None, loops: int = -1, start: float = 0.0) -> None:
        if file is None:
            file = self.music_file
        path = os.path.join(self.sound_path, file)
        if not os.path.exists(path):
            print(f"Sound file not found: {path}")
            return
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(loops, start)
        except pygame.error as e:
            print(f"Error playing sound: {e}")

    def resize(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.win = pygame.display.set_mode((width, height))
        bg_width = self.__background.get_width() if self.__background else width
        if self.bg_position_x2 <= self.bg_position_x1:
            self.bg_position_x2 = self.bg_position_x1 + bg_width


# ===========================================================================
# Tests
# ===========================================================================

class TestNature(unittest.TestCase):

    def setUp(self):
        pygame.init()

        self.temp_dir = tempfile.TemporaryDirectory()

        self.test_images_path = os.path.join(
            self.temp_dir.name, 'Resources', 'images', 'Canvas')
        os.makedirs(self.test_images_path)

        self.test_bg_file = 'test_bg.jpg'
        test_bg_path = os.path.join(self.test_images_path, self.test_bg_file)
        pygame.image.save(pygame.Surface((800, 600)), test_bg_path)

        self.test_sound_path = os.path.join(self.temp_dir.name, 'Resources', 'sound')
        os.makedirs(self.test_sound_path)

        self.test_sound_file = 'test_sound.mp3'
        with open(os.path.join(self.test_sound_path, self.test_sound_file), 'wb') as f:
            f.write(b'dummy sound data')

        self.nature = Nature()
        # Point paths at the temp directory so resource tests work
        self.nature.images_path = (self.test_images_path,)
        self.nature.sound_path  = (self.test_sound_path,)
        self.nature.background_file = self.test_bg_file
        self.nature.music_file      = self.test_sound_file

    def tearDown(self):
        self.temp_dir.cleanup()
        pygame.quit()

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def test_initialization(self):
        """Nature initialises with correct defaults."""
        # BUG FIX 1: Original checked self.nature.high but Nature has no 'high'
        # attribute — the window height is stored as self.height.
        self.assertEqual(self.nature.width,  500)
        self.assertEqual(self.nature.height, 500)   # was 'high', which doesn't exist
        self.assertIsNotNone(self.nature.background)
        self.assertIsInstance(self.nature.win, pygame.Surface)

    # ------------------------------------------------------------------
    # draw
    # ------------------------------------------------------------------

    def test_draw(self):
        """draw() runs without raising an exception."""
        try:
            self.nature.draw()
        except Exception as e:
            self.fail(f"draw() raised an unexpected exception: {e}")

    def test_draw_blits_background_twice(self):
        """draw() blits the background surface exactly twice (two-strip scroll)."""
        # Replace win with a real Surface so blit works
        self.nature.win = pygame.Surface((800, 600))
        # Count calls by wrapping blit
        original_blit = self.nature.win.blit
        blit_calls = []
        self.nature.win.blit = lambda *a, **kw: blit_calls.append(a) or original_blit(*a, **kw)
        self.nature.draw()
        self.assertEqual(len(blit_calls), 2)

    # ------------------------------------------------------------------
    # move_background
    # ------------------------------------------------------------------

    def test_move_background_shifts_positions(self):
        """move_background() decrements both x positions by speed."""
        x1_before = self.nature.bg_position_x1
        x2_before = self.nature.bg_position_x2
        speed = 1.4
        self.nature.move_background(speed)
        self.assertAlmostEqual(self.nature.bg_position_x1, x1_before - speed)
        self.assertAlmostEqual(self.nature.bg_position_x2, x2_before - speed)

    def test_move_background_seamless_wrap(self):
        """When a strip scrolls fully off-screen it wraps to just after the other strip."""
        # BUG FIX 2: Original test set both positions to -(bg_width + 1) and
        # then asserted both equal bg_width after one move_background() call.
        # That logic assumed the old (broken) independent-reset behaviour.
        # The fixed move_background wraps each strip to (other_strip + bg_width),
        # so when *both* strips are off-screen simultaneously (an edge case that
        # can't happen in normal play) the result depends on evaluation order.
        # Test the realistic scenario: one strip at a time falls off-screen.
        bg_width = self.nature.background.get_width()   # 800

        # Place x1 just about to wrap, x2 one bg_width ahead
        self.nature.bg_position_x1 = -bg_width          # right edge at 0 → wraps next tick
        self.nature.bg_position_x2 = 0
        speed = 1.0
        self.nature.move_background(speed)

        # x1 right-edge = (-bg_width - 1) + bg_width = -1 < 0 → wraps
        # Expected: x1 = x2_new + bg_width = (0 - 1) + 800 = 799
        self.assertAlmostEqual(self.nature.bg_position_x1,
                               (0 - speed) + bg_width)
        # x2 just moved, did not wrap
        self.assertAlmostEqual(self.nature.bg_position_x2, 0 - speed)

    def test_move_background_no_gap(self):
        """The two background strips always remain exactly bg_width apart."""
        bg_width = self.nature.background.get_width()
        # Run 300 frames of scrolling and verify no gap opens
        for _ in range(300):
            self.nature.move_background(speed=2.0)
            x1 = self.nature.bg_position_x1
            x2 = self.nature.bg_position_x2
            gap = abs(abs(x1 - x2) - bg_width)
            self.assertLessEqual(
                gap, 3.0,   # tolerance for float accumulation over 300 frames
                msg=f"Gap detected after scroll: x1={x1}, x2={x2}, gap={gap}"
            )

    # ------------------------------------------------------------------
    # Path properties
    # ------------------------------------------------------------------

    def test_images_path_property(self):
        """images_path setter stores the absolute path."""
        test_path = ('new', 'path', 'to', 'images')
        self.nature.images_path = test_path
        self.assertEqual(
            self.nature.images_path,
            os.path.abspath(os.path.join(*test_path))
        )

    def test_sound_path_property(self):
        """sound_path setter stores the absolute path."""
        test_path = ('new', 'path', 'to', 'sounds')
        self.nature.sound_path = test_path
        self.assertEqual(
            self.nature.sound_path,
            os.path.abspath(os.path.join(*test_path))
        )

    def test_empty_path_raises(self):
        """An empty tuple raises ValueError for both path setters."""
        with self.assertRaises(ValueError):
            self.nature.images_path = ()
        with self.assertRaises(ValueError):
            self.nature.sound_path = ()

    # ------------------------------------------------------------------
    # background property
    # ------------------------------------------------------------------

    def test_background_property_valid(self):
        """background setter accepts a pygame.Surface."""
        test_surface = pygame.Surface((100, 100))
        self.nature.background = test_surface
        self.assertEqual(self.nature.background, test_surface)

    def test_background_property_invalid(self):
        """background setter rejects non-Surface values."""
        with self.assertRaises(ValueError):
            self.nature.background = "not a surface"

    # ------------------------------------------------------------------
    # load_image
    # ------------------------------------------------------------------

    def test_load_image_success(self):
        """load_image() returns a Surface for an existing file."""
        loaded = self.nature.load_image(self.test_bg_file)
        self.assertIsInstance(loaded, pygame.Surface)

    def test_load_image_missing_raises(self):
        """load_image() raises FileNotFoundError for a missing file."""
        with self.assertRaises(FileNotFoundError):
            self.nature.load_image("nonexistent.jpg")

    # ------------------------------------------------------------------
    # play_sound
    # ------------------------------------------------------------------

    def test_play_sound_default_file(self):
        """play_sound() with no args loads self.music_file."""
        # BUG FIX 3: Original patched pygame.mixer.init and asserted
        # mock_init.assert_called_once(). The fixed play_sound() only calls
        # mixer.init() when the mixer is not already initialised — in a test
        # environment where pygame.init() was called in setUp the mixer may
        # already be running, so init() might not be called at all.
        # Patch get_init to force the "not yet initialised" branch, making
        # the assertion deterministic.
        with patch('pygame.mixer.get_init', return_value=False), \
             patch('pygame.mixer.init')      as mock_init, \
             patch('pygame.mixer.music.load') as mock_load, \
             patch('pygame.mixer.music.play') as mock_play:

            self.nature.play_sound()

            mock_init.assert_called_once()
            mock_load.assert_called_with(
                os.path.join(self.nature.sound_path, self.test_sound_file))
            mock_play.assert_called_with(-1, 0.0)

    def test_play_sound_already_initialised(self):
        """play_sound() skips mixer.init() when the mixer is already running."""
        with patch('pygame.mixer.get_init', return_value=True), \
             patch('pygame.mixer.init')      as mock_init, \
             patch('pygame.mixer.music.load'), \
             patch('pygame.mixer.music.play'):

            self.nature.play_sound()
            mock_init.assert_not_called()

    def test_play_sound_custom_file(self):
        """play_sound(file) loads the specified file."""
        custom_file = 'custom_sound.mp3'
        custom_path = os.path.join(self.test_sound_path, custom_file)
        # Create the file so the existence check passes
        open(custom_path, 'wb').close()

        with patch('pygame.mixer.get_init', return_value=True), \
             patch('pygame.mixer.music.load') as mock_load, \
             patch('pygame.mixer.music.play'):

            self.nature.play_sound(custom_file)
            mock_load.assert_called_with(
                os.path.join(self.nature.sound_path, custom_file))

    def test_play_sound_missing_file_no_exception(self):
        """play_sound() prints a warning and returns cleanly for missing files."""
        with patch('builtins.print') as mock_print:
            self.nature.play_sound('totally_missing.mp3')
            mock_print.assert_called()

    # ------------------------------------------------------------------
    # position_on_canvas_y
    # ------------------------------------------------------------------

    def test_position_on_canvas_y(self):
        """Canvas Y = window height - game world Y."""
        test_y = 300
        expected = self.nature.win.get_height() - test_y
        self.assertEqual(self.nature.position_on_canvas_y(test_y), expected)

    def test_position_on_canvas_y_without_win(self):
        """Falls back to self.height when win is None."""
        self.nature.win = None
        self.assertEqual(self.nature.position_on_canvas_y(100), 500 - 100)


if __name__ == '__main__':
    unittest.main()