import pygame
import random
from typing import List, Dict
from Play.characters import Human, Goblin
from Play.environment import Nature
from Utility import Direction


class Game:
    def __init__(self):
        """Initialize the game with all components."""
        pygame.init()

        # Game configuration
        self.number_of_enemies = 10
        self.game_time = 60          # seconds
        self.score = 0
        self.direction = -1          # current enemy movement direction (+1 / -1)

        # Core pygame objects
        self.clock = pygame.time.Clock()
        self.environment = Nature()
        self.font           = pygame.font.SysFont("comicsansms", 22)
        self.game_over_font = pygame.font.SysFont("comicsansms", 40)
        self.game_over_font.set_bold(True)

        # Characters
        self.hero    = self.create_hero()
        self.enemies = self.create_enemies()

        # Game state
        self.remaining_time = self.game_time
        self.running = True

    # ------------------------------------------------------------------
    # Factory helpers
    # ------------------------------------------------------------------

    def create_hero(self) -> Human:
        """Create and return the hero character."""
        hero = Human(self.environment, position_x=200, position_y=60)
        hero.create()
        return hero

    def create_enemies(self) -> List[Goblin]:
        """Create and return the list of enemy Goblins."""
        enemies = []
        for _ in range(self.number_of_enemies):
            random_x = random.randint(400, 1000)
            random_y = random.randint(0, 80)
            enemy = Goblin(
                self.environment,
                position_x=random_x,
                position_y=random_y,
                walk_direction='left',
            )
            enemy.create()
            enemy.walk(random.randint(-5, -1))
            enemies.append(enemy)
        return enemies

    # ------------------------------------------------------------------
    # Collision detection
    # ------------------------------------------------------------------

    def check_collisions(self) -> Dict:
        """
        Check for collisions between the hero and every living enemy.

        Returns a dict:
            state   – True if any collision occurred
            injure  – 'Hero' | 'Enemy' | None
            enemies – list of enemies involved in the collision
        """
        collide_data: Dict = {
            'state':   False,
            'injure':  None,
            'enemies': [],
        }

        for enemy in self.enemies:
            # BUG FIX 1: Only check collisions against living enemies.
            # A dead enemy that has already been knocked off-screen can still
            # satisfy the distance check and trigger phantom damage/sounds.
            if not enemy.live:
                continue

            # Horizontal overlap: distance between the nearest facing edges
            if enemy.position_x < self.hero.position_x:
                x_dist = abs(enemy.position_x + enemy.width - self.hero.position_x)
            else:
                x_dist = abs(self.hero.position_x + self.hero.width - enemy.position_x)

            y_dist   = abs(enemy.position_y - self.hero.position_y)
            jump_dist = abs(enemy.position_y + enemy.high - self.hero.position_y)

            if y_dist < 5 and x_dist < 5:          # ground-level collision
                collide_data['state']  = True
                collide_data['injure'] = 'Hero'
                collide_data['enemies'].append(enemy)
            elif jump_dist < 10 and x_dist < 5:     # hero landed on enemy
                collide_data['state']  = True
                collide_data['injure'] = 'Enemy'
                collide_data['enemies'].append(enemy)

        return collide_data

    # ------------------------------------------------------------------
    # Enemy AI
    # ------------------------------------------------------------------

    def handle_enemy_actions(self, enemy: Goblin, injure: str) -> None:
        """React to a collision: either the hero or the enemy takes damage."""
        if injure == 'Hero':
            action = random.randint(1, 4)
            if action == 1:     # escape jump
                enemy.jump(40, 5 * -Direction[enemy.walk_direction.upper()].value)
            elif action == 2:   # attack hero
                enemy.stop()
                enemy.attack()
                # BUG FIX 2: Original wrote self.hero.health -= enemy.power.
                # The fixed health setter is an *assignment*, not additive delta.
                # Subtracting directly would set health to a negative number and
                # clamp to 0 rather than reducing by power. Use the correct
                # damage pattern: new_health = current - power.
                self.hero.health = self.hero.health - enemy.power
            elif action == 3:   # stop and wait
                enemy.stop()
            # action == 4 → enemy does nothing (continue walking)

        elif injure == 'Enemy':
            # BUG FIX 3: Same issue — health setter is assignment, not additive.
            enemy.health = enemy.health - self.hero.power
            sound = enemy.sound_dead if enemy.health <= 0 else enemy.sound_hooch
            enemy.play_sound(sound)
            enemy.jump(40, 5 * self.direction)

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def handle_input(self) -> None:
        """Process keyboard input for the hero."""
        if not self.hero.live:
            return

        keys = pygame.key.get_pressed()

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

    # ------------------------------------------------------------------
    # Enemy movement
    # ------------------------------------------------------------------

    def update_enemy_movement(self) -> None:
        """
        Move living enemies and reverse direction at screen edges.
        """
        # BUG FIX 4: Original indexed self.enemies[-1] and self.enemies[0] to
        # check screen edges. If all enemies are dead the list is empty and this
        # raises IndexError. Also, dead enemies should not be used as the
        # boundary sentinel — use only living enemies.
        living = [e for e in self.enemies if e.live]
        if not living:
            return

        # BUG FIX 5: The original compared enemies[0].position_x >= 600 to
        # reverse direction, but enemies are spawned at x 400–1000 and the
        # screen can be wider. Use the environment width as the right boundary
        # so the reversal point is always correct regardless of window size.
        if living[-1].position_x <= 0:
            self.direction = 1
        elif living[0].position_x >= self.environment.width:
            self.direction = -1

        for enemy in living:
            enemy.walk(random.randint(1, 4) * self.direction)

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw_ui(self) -> None:
        """Draw HUD elements: health bar, score, timer, and end-game messages."""
        win = self.environment.win

        # Health bar (green background, red for missing health)
        health_fraction = self.hero.health / 100
        pygame.draw.rect(win, (0, 255, 0),  (100, 16, 80, 20))
        pygame.draw.rect(win, (255, 0, 0),
                         (100 + int(80 * health_fraction), 16,
                          80 - int(80 * health_fraction), 20))

        score_text  = self.font.render(f'Score: {self.score}',                      True, (0, 0, 0))
        health_text = self.font.render(f'Health: {self.hero.health}',               True, (0, 0, 0))
        time_text   = self.font.render(f'Time: {max(0, int(self.remaining_time))}', True, (0, 0, 0))

        win.blit(score_text,  (self.environment.width - 150, 10))
        win.blit(health_text, (20, 10))
        win.blit(time_text,   (200, 10))

        alive_enemies = sum(1 for e in self.enemies if e.live)

        if not self.hero.live or self.remaining_time <= 0:
            text = self.game_over_font.render('GAME OVER', True, (10, 128, 147))
            # BUG FIX 6: Original used self.environment.high which doesn't
            # exist — the attribute is self.environment.height.
            win.blit(text, (self.environment.width / 4,
                            self.environment.height / 3))
        elif alive_enemies == 0:
            text = self.game_over_font.render('YOU WIN!', True, (12, 250, 147))
            win.blit(text, (self.environment.width / 4,
                            self.environment.height / 3))

    def redraw_window(self) -> None:
        """Composite and flip all game layers."""
        self.environment.draw()
        self.environment.move_background()
        self.draw_ui()
        self.hero.draw()
        for enemy in self.enemies:
            enemy.draw()
        pygame.display.update()

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.handle_input()

            collision = self.check_collisions()
            if collision['state']:
                # BUG FIX 7: Original passed only collision['enemies'][0] to
                # handle_enemy_actions. If multiple enemies collide in the same
                # frame only the first is handled; the rest are silently ignored,
                # meaning the hero can be hit by many enemies but only one
                # responds. Process every colliding enemy.
                for enemy in collision['enemies']:
                    self.handle_enemy_actions(enemy, collision['injure'])
                if collision['injure'] == 'Enemy':
                    self.score += 20 * len(collision['enemies'])
            else:
                self.update_enemy_movement()

            # Hero death animation: knock on-screen enemies back
            if not self.hero.live:
                for enemy in self.enemies:
                    if 0 < enemy.position_x < self.environment.width:
                        enemy.jump(30)

            # BUG FIX 8: remaining_time was decremented by exactly 1/60 every
            # loop iteration. If the machine runs slower than 60 fps the timer
            # drifts and in-game seconds pass more slowly than wall-clock seconds.
            # Use the clock's actual delta time instead.
            dt = self.clock.get_time() / 1000.0   # milliseconds → seconds
            self.remaining_time -= dt if dt > 0 else 1 / 60

            alive_enemies = sum(1 for e in self.enemies if e.live)
            if (not self.hero.live or
                    self.remaining_time <= 0 or
                    alive_enemies == 0):
                self.running = False

            self.redraw_window()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()