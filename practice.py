import pygame
from Play.environment import Nature
from typing import Tuple


class GameOverAnimation:
    def __init__(self):
        """Initialize the game over animation"""
        pygame.init()

        # Game configuration
        self.clock = pygame.time.Clock()
        self.environment = Nature()

        # Animation properties
        self.font = pygame.font.SysFont("comicsansms", 40)
        self.font.set_bold(True)
        self.text_color = (10, 128, 147)
        self.text = "GAME OVER"
        self.position_y = 0
        self.animation_speed = 1
        self.running = True

        # Create the text surface once
        self.game_over_text = self.font.render(self.text, True, self.text_color)

        # Calculate text position for centering
        self.text_width = self.game_over_text.get_width()
        self.text_height = self.game_over_text.get_height()
        self.target_y = self.environment.high // 3

        # Animation state
        self.current_y = -self.text_height  # Start above the screen
        self.final_position = False

    def handle_events(self) -> None:
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_RETURN and self.final_position:
                    self.running = False

    def update_animation(self) -> None:
        """Update the animation position"""
        if not self.final_position:
            self.current_y += self.animation_speed

            # Check if we've reached the target position
            if self.current_y >= self.target_y:
                self.current_y = self.target_y
                self.final_position = True

                # Add a subtle color change when animation completes
                self.text_color = (15, 150, 170)
                self.game_over_text = self.font.render(self.text, True, self.text_color)

    def draw(self) -> None:
        """Draw all elements to the screen"""
        # Clear screen
        self.environment.draw()
        self.environment.move_background()

        # Draw the game over text
        text_x = (self.environment.width - self.text_width) // 2
        self.environment.win.blit(self.game_over_text, (text_x, self.current_y))

        # Add additional effects when animation completes
        if self.final_position:
            # Draw a subtle shadow
            shadow = self.font.render(self.text, True, (50, 50, 50))
            self.environment.win.blit(shadow, (text_x + 3, self.current_y + 3))

            # Draw restart prompt
            prompt_font = pygame.font.SysFont("comicsansms", 20)
            prompt = prompt_font.render("Press ENTER to exit", True, (200, 200, 200))
            prompt_x = (self.environment.width - prompt.get_width()) // 2
            self.environment.win.blit(prompt, (prompt_x, self.current_y + self.text_height + 20))

        pygame.display.update()

    def run(self) -> None:
        """Main animation loop"""
        while self.running:
            # Cap the frame rate
            self.clock.tick(60)

            # Handle events
            self.handle_events()

            # Update animation
            self.update_animation()

            # Draw everything
            self.draw()

        pygame.quit()


if __name__ == "__main__":
    animation = GameOverAnimation()
    animation.run()