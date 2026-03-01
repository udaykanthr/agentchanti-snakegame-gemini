import random
import math
from typing import List, Tuple, Optional, Dict, Any
import pygame

WIDTH = 800
HEIGHT = 600
GRID_SIZE = 20

# Modern dark-mode colors for the backdrop
BG_COLOR = (24, 64, 27)    # Dark forest green
GRID_COLOR = (24, 100, 42)  # Slightly lighter green for grid lines

class Particle:
    """Represents a single spark in a firecracker animation with drag physics."""
    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(80, 200)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.lifetime = 0.5  
        self.initial_lifetime = 0.5

    def update(self, dt: float) -> bool:
        """Update particle position and lifetime with air resistance."""
        drag = 0.1 ** dt
        self.vx *= drag
        self.vy *= drag
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        return self.lifetime > 0

class Apple:
    """Represents the food item with pulsing animation logic."""
    def __init__(self, position: Tuple[int, int]):
        self.position = position
        self.pulse_timer = 0.0

    def update_animation(self, dt: float) -> None:
        self.pulse_timer += dt

    def get_scale(self) -> float:
        return 1.0 + 0.15 * math.sin(self.pulse_timer * 8.0)

class Snake:
    """Represents the snake with visual attributes and animation timers."""
    def __init__(self, segments: List[Tuple[int, int]]):
        self.segments = segments
        self.body_color = (152, 251, 152)
        self.head_color = (255, 182, 193)
        self.eye_color = (255, 255, 255)
        self.eat_animation_timer = 0.0
        self.pulse_timer = 0.0

    def set_cute_style(self) -> None:
        self.body_color = (152, 251, 152)
        self.head_color = (255, 182, 193)
        self.eye_color = (255, 255, 255)

    def update_animation(self, dt: float) -> None:
        self.pulse_timer += dt
        if self.eat_animation_timer > 0:
            self.eat_animation_timer = max(0.0, self.eat_animation_timer - dt)

    def get_head_scale(self) -> float:
        if self.eat_animation_timer > 0:
            return 1.0 + 0.4 * math.sin((self.eat_animation_timer / 0.2) * math.pi)
        return 1.0

    def get_segment_colors(self) -> List[Tuple[int, int, int]]:
        if not self.segments:
            return []
        colors = [self.head_color]
        for i in range(1, len(self.segments)):
            ratio = i / max(1, len(self.segments) - 1)
            r = int(self.body_color[0] * (1.0 - ratio * 0.25))
            g = int(self.body_color[1] * (1.0 - ratio * 0.25))
            b = int(self.body_color[2] * (1.0 - ratio * 0.25))
            colors.append((r, g, b))
        return colors

class Game:
    """Main game logic with state management and visual effect triggers."""
    def __init__(self, width: int = WIDTH // GRID_SIZE, height: int = HEIGHT // GRID_SIZE):
        if width < 3 or height < 3:
            raise ValueError("Game dimensions must be at least 3x3")
        self.width = width
        self.height = height
        self.margin_top = 4
        
        self.state = "PLAYING"
        self.score = 0
        self.lives = 3
        self.alive = True
        
        self._respawn_snake()
        self.direction = (0, -1)
        self.apple: Optional[Apple] = None
        self.particles: List[Particle] = []
        self.shake_amount = 0.0
        self._place_food()

    def _respawn_snake(self) -> None:
        mid_x = self.width // 2
        mid_y = (self.margin_top + self.height) // 2
        self.snake = Snake([(mid_x, mid_y), (mid_x, mid_y + 1), (mid_x, mid_y + 2)])
        self.direction = (0, -1)

    @property
    def food(self) -> Optional[Tuple[int, int]]:
        return self.apple.position if self.apple else None

    @food.setter
    def food(self, value: Optional[Tuple[int, int]]) -> None:
        if value is None:
            self.apple = None
        else:
            self.apple = Apple(value)

    def _place_food(self) -> None:
        all_positions = [(x, y) for x in range(self.width) for y in range(self.margin_top, self.height)]
        occupied = set(self.snake.segments)
        possible = [pos for pos in all_positions if pos not in occupied]
        if not possible:
            self.apple = None
        else:
            self.apple = Apple(random.choice(possible))

    def _spawn_firecracker(self, grid_x: int, grid_y: int) -> None:
        center_x = grid_x * GRID_SIZE + GRID_SIZE // 2
        center_y = grid_y * GRID_SIZE + GRID_SIZE // 2
        colors = [(255, 255, 255), (255, 220, 100), (255, 150, 50)]
        for _ in range(25):
            self.particles.append(Particle(center_x, center_y, random.choice(colors)))

    def set_direction(self, dx: int, dy: int) -> None:
        if self.state == "GAME_OVER":
            return
        if self.state == "START":
            self.state = "PLAYING"
        if (dx, dy) == (-self.direction[0], -self.direction[1]):
            return
        self.direction = (dx, dy)

    def tick(self) -> None:
        if self.state != "PLAYING" or not self.alive:
            return

        head_x, head_y = self.snake.segments[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Collision check
        if not (0 <= new_head[0] < self.width and self.margin_top <= new_head[1] < self.height) or new_head in self.snake.segments:
            self.lives -= 1
            self.shake_amount = 12.0
            if self.lives <= 0:
                self.alive = False
                self.state = "GAME_OVER"
            else:
                self._respawn_snake()
            return

        self.snake.segments.insert(0, new_head)
        if self.apple and new_head == self.apple.position:
            self.score += 10
            self.snake.eat_animation_timer = 0.2
            self.shake_amount = 4.0
            self._spawn_firecracker(new_head[0], new_head[1])
            self._place_food()
        else:
            self.snake.segments.pop()

    def reset(self) -> None:
        self.score = 0
        self.lives = 3
        self.alive = True
        self.state = "PLAYING"
        self.particles = []
        self.shake_amount = 0.0
        self._respawn_snake()
        self._place_food()

    def update_animations(self, dt: float) -> None:
        if self.apple:
            self.apple.update_animation(dt)
        self.snake.update_animation(dt)
        self.particles = [p for p in self.particles if p.update(dt)]
        if self.shake_amount > 0:
            self.shake_amount = max(0.0, self.shake_amount - dt * 30.0)

    def get_state(self) -> Dict[str, Any]:
        shake_off = (0, 0)
        if self.shake_amount > 0:
            shake_off = (random.uniform(-self.shake_amount, self.shake_amount),
                         random.uniform(-self.shake_amount, self.shake_amount))

        return {
            "snake": self.snake.segments,
            "snake_colors": self.snake.get_segment_colors(),
            "head_color": self.snake.head_color,
            "body_color": self.snake.body_color,
            "eye_color": self.snake.eye_color,
            "food": self.food,
            "food_scale": self.apple.get_scale() if self.apple else 1.0,
            "head_scale": self.snake.get_head_scale(),
            "shake_offset": shake_off,
            "alive": self.alive,
            "score": self.score,
            "lives": self.lives,
            "state": self.state,
            "margin_top": self.margin_top,
            "eat_animation_timer": self.snake.eat_animation_timer,
            "particles": [
                {
                    "pos": (p.x, p.y),
                    "color": p.color,
                    "alpha": int(255 * (p.lifetime / p.initial_lifetime))
                } for p in self.particles
            ]
        }

    def draw_grid(self, surface: pygame.Surface, offset: Tuple[float, float] = (0, 0)) -> None:
        ox, oy = offset
        for x in range(0, self.width * GRID_SIZE + 1, GRID_SIZE):
            pygame.draw.line(surface, GRID_COLOR, 
                             (x + ox, self.margin_top * GRID_SIZE + oy), 
                             (x + ox, self.height * GRID_SIZE + oy))
        for y in range(self.margin_top * GRID_SIZE, self.height * GRID_SIZE + 1, GRID_SIZE):
            pygame.draw.line(surface, GRID_COLOR, 
                             (ox, y + oy), 
                             (self.width * GRID_SIZE + ox, y + oy))

def create_game() -> Game:
    game = Game()
    game.state = "START"
    return game