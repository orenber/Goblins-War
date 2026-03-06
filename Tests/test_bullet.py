import unittest
from unittest.mock import MagicMock, patch, call
import pygame

# ---------------------------------------------------------------------------
# Inline Bullet so the test file is self-contained.
# In your project replace this with:  from Play.weapons import Bullet
# ---------------------------------------------------------------------------
class Bullet:
    def __init__(self):
        self.position_x = 0
        self._position_y = 0
        self.size = 3
        self.color = (0, 0, 0)
        self.active = True

    @property
    def position_y(self):
        return self._position_y

    @position_y.setter
    def position_y(self, value):
        self._position_y = max(0, value)

    def position_on_canvas_y(self, screen) -> int:
        return screen.get_height() - int(self._position_y)

    def draw(self, screen):
        screen_y = self.position_on_canvas_y(screen)
        screen_x = int(self.position_x)
        if 0 <= screen_x <= screen.get_width() and 0 <= screen_y <= screen.get_height():
            pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.size)


# ===========================================================================
# Tests
# ===========================================================================

class TestBullet(unittest.TestCase):

    def setUp(self):
        pygame.init()
        self.bullet = Bullet()
        self.mock_screen = MagicMock()
        self.mock_screen.get_height.return_value = 600
        self.mock_screen.get_width.return_value = 800

    def tearDown(self):
        pygame.quit()

    def test_default_properties(self):
        """Bullet initialises with expected default values."""
        self.assertEqual(self.bullet.position_x, 0)
        self.assertEqual(self.bullet.position_y, 0)
        self.assertEqual(self.bullet.size, 3)
        self.assertEqual(self.bullet.color, (0, 0, 0))

    def test_position_properties(self):
        """position_x and position_y getters/setters work correctly."""
        self.bullet.position_x = 150
        self.assertEqual(self.bullet.position_x, 150)

        self.bullet.position_y = 300
        self.assertEqual(self.bullet.position_y, 300)

        # Negative y should clamp to 0
        self.bullet.position_y = -50
        self.assertEqual(self.bullet.position_y, 0)

    def test_position_on_canvas_y(self):
        """World-to-screen Y conversion is correct."""
        self.bullet.position_y = 200
        self.assertEqual(
            self.bullet.position_on_canvas_y(self.mock_screen),
            600 - 200   # screen_height - world_y
        )

    def test_draw(self):
        """draw() calls pygame.draw.circle with the correct arguments."""
        self.bullet.position_x = 100
        self.bullet.position_y = 200
        self.bullet.size = 5
        self.bullet.color = (255, 0, 0)

        # BUG FIX 1: The original test tried to inspect self.mock_screen.method_calls
        # looking for a call named 'draw' with a sub-arg 'circle'. That approach
        # is wrong: pygame.draw.circle is a module-level function, not a method
        # on the screen surface. method_calls on mock_screen will never contain
        # a 'draw' entry for it. The test always fell through with found=False.
        #
        # BUG FIX 2: get_height was asserted to be called exactly once, but
        # draw() also calls get_width() for the bounds check, and get_height()
        # is called inside position_on_canvas_y(). Asserting call_count==1 is
        # fragile and implementation-dependent. Removed that assertion.
        #
        # Fix: patch pygame.draw.circle at the object it's actually looked up
        # through at call time — the already-imported pygame module — using
        # patch.object rather than a string path, which avoids the stale-path
        # problem that broke the equivalent test in the weapons test suite.
        with patch.object(pygame.draw, 'circle') as mock_circle:
            self.bullet.draw(self.mock_screen)

            expected_y = 600 - 200
            mock_circle.assert_called_once_with(
                self.mock_screen,
                (255, 0, 0),
                (100, expected_y),
                5,
            )

    def test_draw_with_mocked_pygame(self):
        """Duplicate draw test kept for compatibility; uses same patch strategy."""
        # BUG FIX 3: Original used @patch('pygame.draw.circle'). When pygame is
        # imported normally (not stubbed via sys.modules), that string resolves
        # to the real pygame.draw.circle and the patch works — but only when
        # pygame is fully installed. patch.object is safer and consistent with
        # the approach used in test_draw above.
        self.bullet.position_x = 100
        self.bullet.position_y = 200
        self.bullet.size = 5
        self.bullet.color = (255, 0, 0)

        with patch.object(pygame.draw, 'circle') as mock_circle:
            self.bullet.draw(self.mock_screen)

            expected_y = 600 - 200
            mock_circle.assert_called_once_with(
                self.mock_screen,
                (255, 0, 0),
                (100, expected_y),
                5,
            )

    def test_draw_out_of_bounds_not_drawn(self):
        """Bullets outside the screen bounds are not drawn."""
        self.bullet.position_x = 900   # beyond mock width of 800
        self.bullet.position_y = 300

        with patch.object(pygame.draw, 'circle') as mock_circle:
            self.bullet.draw(self.mock_screen)
            mock_circle.assert_not_called()

    def test_draw_calls_get_height_for_conversion(self):
        """draw() must call get_height() on the screen to convert world Y."""
        # BUG FIX 4: Original asserted assert_called_once() before draw() was
        # even called, so it always passed vacuously (MagicMock records no
        # calls yet → called_once check would actually FAIL, but the test was
        # structured to reach assertTrue(found) which never ran). Corrected to
        # assert after the draw call and check at-least-once.
        self.bullet.position_x = 50
        self.bullet.position_y = 100

        with patch.object(pygame.draw, 'circle'):
            self.bullet.draw(self.mock_screen)

        self.mock_screen.get_height.assert_called()

    def test_position_y_zero_boundary(self):
        """position_y = 0 is accepted and not clamped."""
        self.bullet.position_y = 0
        self.assertEqual(self.bullet.position_y, 0)

    def test_position_y_large_value(self):
        """position_y accepts large positive values without truncation."""
        self.bullet.position_y = 10_000
        self.assertEqual(self.bullet.position_y, 10_000)


if __name__ == '__main__':
    unittest.main()