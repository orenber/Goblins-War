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
        self.win = None  # Will be initialized in __create()

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

    def __create(self) -> None:
        """Initialize the display and load resources."""
        # Initialize pygame display
        self.win = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Nature Environment")

        # Load background image
        try:
            self.background = self.load_image(self.background_file)
            self.bg_position_x2 = self.background.get_width()
        except (FileNotFoundError, pygame.error) as e:
            print(f"Error loading background image: {e}")
            # Create a fallback background
            self.background = pygame.Surface((self.width, self.height))
            self.background.fill((0, 100, 200))  # Blue fallback background
            self.bg_position_x2 = self.width

    def draw(self) -> None:
        """Draw the background and all elements to the window."""
        self.win.fill((0, 0, 0))  # Clear screen with black

        # Draw the two background images for seamless scrolling
        if self.background:
            self.win.blit(self.background, (self.bg_position_x1, self.bg_position_y1))
            self.win.blit(self.background, (self.bg_position_x2, self.bg_position_y2))

    def move_background(self, speed: float = 1.4) -> None:
        """
        Move the background for scrolling effect.

        Args:
            speed: The speed at which the background should scroll
        """
        self.bg_position_x1 -= speed
        self.bg_position_x2 -= speed

        # Reset positions when images scroll completely off screen
        bg_width = self.background.get_width() if self.background else self.width
        if self.bg_position_x1 < -bg_width:
            self.bg_position_x1 = bg_width
        if self.bg_position_x2 < -bg_width:
            self.bg_position_x2 = bg_width

    def position_on_canvas_y(self, position_y: float) -> float:
        """
        Convert a game-world y-coordinate to pygame canvas y-coordinate.

        Args:
            position_y: The game-world y-coordinate

        Returns:
            The corresponding pygame canvas y-coordinate
        """
        return self.win.get_height() - position_y

    @property
    def images_path(self) -> str:
        """Get the absolute path to the images directory."""
        return self.__images_path

    @images_path.setter
    def images_path(self, images_path: Tuple[str, ...]) -> None:
        """
        Set the path to the images directory.

        Args:
            images_path: Tuple of path components (e.g., ('Resources', 'images'))
        """
        self.__images_path = os.path.abspath(os.path.join(*images_path))
        if not os.path.exists(self.__images_path):
            print(f"Warning: Images path does not exist: {self.__images_path}")

    @property
    def sound_path(self) -> str:
        """Get the absolute path to the sounds directory."""
        return self.__sound_path

    @sound_path.setter
    def sound_path(self, sound_path: Tuple[str, ...]) -> None:
        """
        Set the path to the sounds directory.

        Args:
            sound_path: Tuple of path components (e.g., ('Resources', 'sound'))
        """
        self.__sound_path = os.path.abspath(os.path.join(*sound_path))
        if not os.path.exists(self.__sound_path):
            print(f"Warning: Sound path does not exist: {self.__sound_path}")

    @property
    def background(self) -> Optional[pygame.Surface]:
        """Get the current background surface."""
        return self.__background

    @background.setter
    def background(self, image_background: pygame.Surface) -> None:
        """Set the background surface."""
        if isinstance(image_background, pygame.Surface):
            self.__background = image_background
        else:
            raise ValueError("Background must be a pygame.Surface")

    def load_image(self, file: str) -> pygame.Surface:
        """
        Load an image from the images directory.

        Args:
            file: The filename of the image to load

        Returns:
            The loaded pygame Surface

        Raises:
            FileNotFoundError: If the image file doesn't exist
            pygame.error: If pygame fails to load the image
        """
        path = os.path.join(self.images_path, file)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Image file not found: {path}")

        image = pygame.image.load(path)
        # Convert for better performance
        return image.convert_alpha() if image.get_alpha() else image.convert()

    def play_sound(self, file: Optional[str] = None, loops: int = -1, start: float = 0.0) -> None:
        """
        Play background music.

        Args:
            file: The sound file to play (defaults to music_file)
            loops: Number of times to loop (-1 for infinite)
            start: Position to start playback (in seconds)
        """
        if file is None:
            file = self.music_file

        path = os.path.join(self.sound_path, file)
        if not os.path.exists(path):
            print(f"Sound file not found: {path}")
            return

        try:
            pygame.mixer.init()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(loops, start)
        except pygame.error as e:
            print(f"Error playing sound: {e}")

    def resize(self, width: int, height: int) -> None:
        """
        Resize the display window.

        Args:
            width: New width of the window
            height: New height of the window
        """
        self.width = width
        self.height = height
        self.win = pygame.display.set_mode((width, height))


# Initialize pygame
pygame.init()

# Create nature environment
env = Nature(width=800, height=600)

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Scroll the background
    env.move_background(speed=2)

    # Draw everything
    env.draw()
    pygame.display.flip()

    # Control frame rate
    clock.tick(60)

pygame.quit()

