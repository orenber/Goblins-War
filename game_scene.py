import pygame
import numpy as np
import random
from typing import List, Dict, Optional
from Play.characters import Human, Goblin
from Play.environment import Nature
from Utility import Direction


class Game:
    def __init__(self):
        """Initialize the game with all components"""
        pygame.init()

        # Game configuration
        self.number_of_enemies = 10
        self.game_time = 60  # seconds
        self.score = 0
        self.direction = -1  # Initial enemy movement direction

        # Initialize game components
        self.clock = pygame.time.Clock()
        self.environment = Nature()
        self.font = pygame.font.SysFont("comicsansms", 22)
        self.game_over_font = pygame.font.SysFont("comicsansms", 40)
        self.game_over_font.set_bold(True)

        # Create characters
        self.hero = self.create_hero()
        self.enemies = self.create_enemies()

        # Game state
        self.remaining_time = self.game_time
        self.running = True

    def create_hero(self) -> Human:
        """Create and initialize the hero character"""
        hero = Human(self.environment, position_x=200, position_y=60)
        hero.create()
        return hero

    def create_enemies(self) -> List[Goblin]:
        """Create and initialize enemy characters"""
        enemies = []
        for _ in range(self.number_of_enemies):
            random_x = random.randint(400, 1000)
            random_y = random.randint(0, 80)
            enemy = Goblin(
                self.environment,
                position_x=random_x,
                position_y=random_y,
                walk_direction='left'
            )
            enemy.create()
            enemy.walk(random.randint(-5, -1))
            enemies.append(enemy)
        return enemies

    def check_collisions(self) -> Dict:
        """
        Check for collisions between hero and enemies

        Returns:
            Dictionary with collision state:
            - 'state': bool (whether collision occurred)
            - 'injure': str ('Hero' or 'Enemy' who gets injured)
            - 'enemies': list of colliding enemies
        """
        collide_data = {
            'state': False,
            'injure': None,
            'enemies': []
        }

        for enemy in self.enemies:
            # Calculate horizontal distance
            if enemy.position_x < self.hero.position_x:
                x_dist = abs(enemy.position_x + enemy.width - self.hero.position_x)
            else:
                x_dist = abs(self.hero.position_x + self.hero.width - enemy.position_x)

            # Calculate vertical distances
            y_dist = abs(enemy.position_y - self.hero.position_y)
            jump_dist = abs(enemy.position_y + enemy.high - self.hero.position_y)

            # Check collision types
            if y_dist < 5 and x_dist < 5:  # Standard collision
                collide_data['state'] = True
                collide_data['injure'] = 'Hero'
                collide_data['enemies'].append(enemy)
            elif jump_dist < 10 and x_dist < 5:  # Jump attack collision
                collide_data['state'] = True
                collide_data['injure'] = 'Enemy'
                collide_data['enemies'].append(enemy)

        return collide_data

    def handle_enemy_actions(self, enemy: Goblin, injure: str) -> None:
        """Handle enemy behavior based on collision type"""
        if injure == 'Hero':
            action = random.randint(1, 4)
            if action == 1:  # Escape
                enemy.jump(40, 5 * -Direction[enemy.walk_direction].value)
            elif action == 2:  # Attack
                enemy.stop()
                enemy.attack()
                self.hero.health -= enemy.power
            elif action == 3:  # Stop
                enemy.stop()
        elif injure == 'Enemy':
            enemy.health -= self.hero.power
            sound = enemy.sound_dead if enemy.health <= 0 else enemy.sound_hooch
            enemy.play_sound(sound)
            enemy.jump(40, 5 * self.direction)

    def handle_input(self) -> None:
        """Process player input"""
        keys = pygame.key.get_pressed()

        if not self.hero.live:
            return

        if keys[pygame.K_LEFT]:
            self.hero.walk(-5)
        if keys[pygame.K_RIGHT]:
            self.hero.walk(5)
        if keys[pygame.K_DOWN]:
            self.hero.stop()
        if keys[pygame.K_UP]:
            self.hero.jump(50, 5)
        if keys[pygame.K_SPACE]:
            self.hero.attack()

    def update_enemy_movement(self) -> None:
        """Update enemy movement patterns"""
        # Reverse direction if enemies reach screen edges
        if self.enemies[-1].position_x <= 0:
            self.direction = 1
        elif self.enemies[0].position_x >= 600:
            self.direction = -1

        # Move all living enemies
        for enemy in self.enemies:
            if enemy.live:
                enemy.walk(random.randint(1, 4) * self.direction)

    def draw_ui(self) -> None:
        """Draw user interface elements"""
        # Health bar
        pygame.draw.rect(
            self.environment.win,
            (0, 255, 0),
            (100, 16, 80, 20)
        )
        pygame.draw.rect(
            self.environment.win,
            (255, 0, 0),
            (100, 16, 80 * (1 - self.hero.health / 100), 20)
        )

        # Score and time
        score_text = self.font.render(f'Score: {self.score}', True, (0, 0, 0))
        health_text = self.font.render(f'Health: {self.hero.health}', True, (0, 0, 0))
        time_text = self.font.render(f'Time: {max(0, int(self.remaining_time))}', True, (0, 0, 0))

        self.environment.win.blit(score_text, (self.environment.width - 150, 10))
        self.environment.win.blit(health_text, (20, 10))
        self.environment.win.blit(time_text, (200, 10))

        # Game over messages
        alive_enemies = sum(1 for e in self.enemies if e.live)

        if not self.hero.live or self.remaining_time <= 0:
            game_over_text = self.game_over_font.render('GAME OVER', True, (10, 128, 147))
            self.environment.win.blit(
                game_over_text,
                (self.environment.width / 4, self.environment.high / 3)
            )
        elif alive_enemies == 0:
            victory_text = self.game_over_font.render('YOU WIN!', True, (12, 250, 147))
            self.environment.win.blit(
                victory_text,
                (self.environment.width / 4, self.environment.high / 3)
            )

    def redraw_window(self) -> None:
        """Redraw all game elements"""
        self.environment.draw()
        self.environment.move_background()
        self.draw_ui()

        self.hero.draw()
        for enemy in self.enemies:
            enemy.draw()

        pygame.display.update()

    def run(self) -> None:
        """Main game loop"""
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Update game state
            self.handle_input()

            # Check for collisions
            collision = self.check_collisions()
            if collision['state']:
                self.handle_enemy_actions(
                    collision['enemies'][0],
                    collision['injure']
                )
                if collision['injure'] == 'Enemy':
                    self.score += 20
            else:
                self.update_enemy_movement()

            # Handle hero death
            if not self.hero.live:
                for enemy in self.enemies:
                    if 0 < enemy.position_x < self.environment.width:
                        enemy.jump(30)

            # Update timer
            self.remaining_time -= 1 / 60

            # Check win/lose conditions
            alive_enemies = sum(1 for e in self.enemies if e.live)
            if (not self.hero.live or self.remaining_time <= 0 or
                    alive_enemies == 0):
                self.running = False

            # Redraw everything
            self.redraw_window()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()