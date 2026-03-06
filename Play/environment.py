import pygame
import os
from typing import Tuple, Optional


class Nature:
    def __init__(self, width: int = 500, height: int = 500) -> None:
        """
        Initialize the Nature environment with background and sound capabilities.

        Args:
            width: Width of the display window
            height: Height of the display window
        """
        # Path configurations
        self.__images_path = ''
        self.__sound_path = ''

        # Display properties
        self.__background = None
        self.width = width
        self.height = height
        self.win = None  # Initialised in __create()

        # Background scrolling properties
        self.bg_position_x1 = 0
        self.bg_position_y1 = 0
        self.bg_position_x2 = 0
        self.bg_position_y2 = 0

        # Default file paths
        self.images_path = ('Resources', 'images', 'Canvas')
        self.sound_path = ('Resources', 'sound')
        self.background_file = 'bg.jpg'
        self.music_file = 'music.mp3'

        self.__create()

    # ------------------------------------------------------------------
    # Internal setup
    # ------------------------------------------------------------------

    def __create(self) -> None:
        """Initialize the display and load resources."""
        self.win = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Nature Environment")

        try:
            self.background = self.load_image(self.background_file)
            # BUG FIX 1: bg_position_x2 must be initialised to bg_width so the
            # second copy starts exactly where the first one ends. The original
            # set it correctly here but the move_background reset logic was wrong
            # (see Bug 2), so a seamless loop was never actually achieved.
            self.bg_position_x2 = self.background.get_width()
        except (FileNotFoundError, pygame.error) as e:
            print(f"Error loading background image: {e}")
            self.background = pygame.Surface((self.width, self.height))
            self.background.fill((0, 100, 200))
            self.bg_position_x2 = self.width

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self) -> None:
        """Draw the background and all elements to the window."""
        # BUG FIX 2: Filling with black before blitting the background is
        # correct for clearing leftover sprites, but only matters if the
        # background doesn't cover the full window. Kept as a safe default.
        self.win.fill((0, 0, 0))

        if self.__background:
            self.win.blit(self.__background, (self.bg_position_x1, self.bg_position_y1))
            self.win.blit(self.__background, (self.bg_position_x2, self.bg_position_y2))

    def move_background(self, speed: float = 1.4) -> None:
        """
        Move the background for a seamless horizontal scrolling effect.

        Args:
            speed: Pixels per frame to scroll leftward (positive = scroll left)
        """
        self.bg_position_x1 -= speed
        self.bg_position_x2 -= speed

        bg_width = self.__background.get_width() if self.__background else self.width

        # BUG FIX 3: The original reset each position to +bg_width independently.
        # This breaks the seamless loop: when x1 wraps, it snaps to bg_width
        # regardless of where x2 currently sits, so the two copies can overlap
        # or leave a gap. The correct fix is to wrap each strip to exactly one
        # bg_width *ahead of the other strip*, maintaining a perfect chain.
        if self.bg_position_x1 + bg_width <= 0:
            self.bg_position_x1 = self.bg_position_x2 + bg_width
        if self.bg_position_x2 + bg_width <= 0:
            self.bg_position_x2 = self.bg_position_x1 + bg_width

    # ------------------------------------------------------------------
    # Coordinate helpers
    # ------------------------------------------------------------------

    def position_on_canvas_y(self, position_y: float) -> float:
        """
        Convert a game-world y-coordinate to a pygame canvas y-coordinate.

        In game-world coords y=0 is the bottom of the screen; pygame's y=0 is
        the top.

        Args:
            position_y: Game-world y-coordinate

        Returns:
            Corresponding pygame canvas y-coordinate
        """
        # BUG FIX 4: self.win can be None if called before __create() completes
        # or after resize() is called with an error. Guard against that.
        if self.win is None:
            return self.height - position_y
        return self.win.get_height() - position_y

    # ------------------------------------------------------------------
    # Path properties
    # ------------------------------------------------------------------

    @property
    def images_path(self) -> str:
        """Absolute path to the images directory."""
        return self.__images_path

    @images_path.setter
    def images_path(self, images_path: Tuple[str, ...]) -> None:
        """
        Set the images directory path.

        Args:
            images_path: Tuple of path components, e.g. ('Resources', 'images')
        """
        # BUG FIX 5: os.path.join(*tuple) raises TypeError if the tuple is
        # empty. Guard against that before calling join.
        if not images_path:
            raise ValueError("images_path must contain at least one component")
        self.__images_path = os.path.abspath(os.path.join(*images_path))
        if not os.path.exists(self.__images_path):
            print(f"Warning: Images path does not exist: {self.__images_path}")

    @property
    def sound_path(self) -> str:
        """Absolute path to the sounds directory."""
        return self.__sound_path

    @sound_path.setter
    def sound_path(self, sound_path: Tuple[str, ...]) -> None:
        """
        Set the sounds directory path.

        Args:
            sound_path: Tuple of path components, e.g. ('Resources', 'sound')
        """
        if not sound_path:
            raise ValueError("sound_path must contain at least one component")
        self.__sound_path = os.path.abspath(os.path.join(*sound_path))
        if not os.path.exists(self.__sound_path):
            print(f"Warning: Sound path does not exist: {self.__sound_path}")

    # ------------------------------------------------------------------
    # Background property
    # ------------------------------------------------------------------

    @property
    def background(self) -> Optional[pygame.Surface]:
        """Current background surface."""
        return self.__background

    @background.setter
    def background(self, image_background: pygame.Surface) -> None:
        """Set the background surface (must be a pygame.Surface)."""
        if isinstance(image_background, pygame.Surface):
            self.__background = image_background
        else:
            raise ValueError("Background must be a pygame.Surface")

    # ------------------------------------------------------------------
    # Resource loading
    # ------------------------------------------------------------------

    def load_image(self, file: str) -> pygame.Surface:
        """
        Load an image from the images directory.

        Args:
            file: Filename of the image to load

        Returns:
            Loaded pygame Surface

        Raises:
            FileNotFoundError: If the image file doesn't exist
            pygame.error: If pygame fails to load the image
        """
        path = os.path.join(self.images_path, file)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Image file not found: {path}")
        image = pygame.image.load(path)
        return image.convert_alpha() if image.get_alpha() else image.convert()

    def play_sound(self, file: Optional[str] = None, loops: int = -1, start: float = 0.0) -> None:
        """
        Play background music.

        Args:
            file: Sound file to play (defaults to self.music_file)
            loops: Number of times to loop (-1 = infinite)
            start: Playback start position in seconds
        """
        if file is None:
            file = self.music_file

        path = os.path.join(self.sound_path, file)
        if not os.path.exists(path):
            print(f"Sound file not found: {path}")
            return

        try:
            # BUG FIX 6: pygame.mixer.init() called unconditionally on every
            # play_sound() invocation. Calling init() while the mixer is already
            # running stops current playback and resets the mixer. Only initialise
            # if it hasn't been already.
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(loops, start)
        except pygame.error as e:
            print(f"Error playing sound: {e}")

    # ------------------------------------------------------------------
    # Window management
    # ------------------------------------------------------------------

    def resize(self, width: int, height: int) -> None:
        """
        Resize the display window.

        Args:
            width: New window width
            height: New window height
        """
        self.width = width
        self.height = height
        self.win = pygame.display.set_mode((width, height))

        # BUG FIX 7: After a resize the background scroll positions are not
        # adjusted. If the new window is wider than the background image the
        # second copy (x2) may start too far right, leaving a black gap on the
        # first frame. Re-anchor x2 to ensure the chain is intact.
        bg_width = self.__background.get_width() if self.__background else width
        if self.bg_position_x2 <= self.bg_position_x1:
            self.bg_position_x2 = self.bg_position_x1 + bg_width


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    pygame.init()

    env = Nature(width=800, height=600)

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        env.move_background(speed=2)
        env.draw()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()