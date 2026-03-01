import random
import math
from typing import List, Tuple, Optional, Dict, Any
import pygame

WIDTH = 800
HEIGHT = 600
GRID_SIZE = 20
BG_COLOR = (20, 20, 30)
GRID_COLOR = (40, 40, 50)

class Particle:
    """Represents a single spark in a firecracker animation."""
    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.color = color
        # Random direction and speed
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(50, 150)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.lifetime = 0.4  # seconds
        self.initial_lifetime = 0.4

    def update(self, dt: float) -> bool:
        """Update particle position and lifetime. Returns False if dead."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        return self.lifetime > 0

class Apple:
    """Represents the food item with animation properties."""
    def __init__(self, position: Tuple[int, int]):
        self.position = position
        self.pulse_timer = 0.0

    def update_animation(self, dt: float) -> None:
        """Update the animation timer based on delta time."""
        self.pulse_timer += dt

class Snake:
    """Represents the snake in the game with visual attributes."""
    def __init__(self, segments: List[Tuple[int, int]]):
        self.segments = segments
        # Default colors
        self.body_color = (152, 251, 152)  # Pastel Green
        self.head_color = (255, 182, 193)  # Pastel Pink
        self.eye_color = (255, 255, 255)   # White eyes
        self.pulse_timer = 0.0
        self.eat_animation_timer = 0.0

    def set_cute_style(self) -> None:
        """Apply a cute color palette to the snake."""
        self.body_color = (152, 251, 152)  # Pastel Green
        self.head_color = (255, 182, 193)  # Pastel Pink
        self.eye_color = (255, 255, 255)   # White eyes

    def update_animation(self, dt: float) -> None:
        """Update the animation timers for the snake."""
        self.pulse_timer += dt
        if self.eat_animation_timer > 0:
            self.eat_animation_timer = max(0.0, self.eat_animation_timer - dt)

class Game:
    """Main game logic for Snake with state management and scoring."""
    def __init__(self, width: int = WIDTH // GRID_SIZE, height: int = HEIGHT // GRID_SIZE):
        if width < 3 or height < 3:
            raise ValueError("Game dimensions must be at least 3x3")
        self.width = width
        self.height = height
        
        # Game State attributes
        self.state = "PLAYING"  # Possible states: "START", "PLAYING", "GAME_OVER"
        self.score = 0
        self.alive = True
        
        # Initial snake: 3 segments in the middle
        mid_x, mid_y = width // 2, height // 2
        self.snake = Snake([(mid_x, mid_y), (mid_x, mid_y + 1), (mid_x, mid_y + 2)])
        
        self.direction = (0, -1)  # Initially moving Up
        self.apple: Optional[Apple] = None
        self.particles: List[Particle] = []
        self._place_food()

    @property
    def food(self) -> Optional[Tuple[int, int]]:
        """Return the position of the food."""
        return self.apple.position if self.apple else None

    @food.setter
    def food(self, value: Optional[Tuple[int, int]]) -> None:
        """Set the food position."""
        if value is None:
            self.apple = None
        else:
            self.apple = Apple(value)

    def _place_food(self) -> None:
        """Place food in a random empty cell."""
        all_positions = [(x, y) for x in range(self.width) for y in range(self.height)]
        occupied = set(self.snake.segments)
        possible = [pos for pos in all_positions if pos not in occupied]
        if not possible:
            self.apple = None
        else:
            self.apple = Apple(random.choice(possible))

    def _spawn_firecracker(self, grid_x: int, grid_y: int) -> None:
        """Create a burst of particles at the specified grid cell."""
        center_x = grid_x * GRID_SIZE + GRID_SIZE // 2
        center_y = grid_y * GRID_SIZE + GRID_SIZE // 2
        colors = [(255, 255, 255), (255, 200, 50), (255, 100, 0)] # White, Yellow, Orange
        
        for _ in range(20):
            color = random.choice(colors)
            self.particles.append(Particle(center_x, center_y, color))

    def set_direction(self, dx: int, dy: int) -> None:
        """Update direction if it is not a 180-degree turn."""
        if self.state == "GAME_OVER":
            return
        
        if self.state == "START":
            self.state = "PLAYING"

        if (dx, dy) == (-self.direction[0], -self.direction[1]):
            return
        self.direction = (dx, dy)

    def tick(self) -> None:
        """Advance the game by one step."""
        if self.state != "PLAYING" or not self.alive:
            return

        head_x, head_y = self.snake.segments[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        if not (0 <= new_head[0] < self.width and 0 <= new_head[1] < self.height):
            self.alive = False
            self.state = "GAME_OVER"
            return

        if new_head in self.snake.segments:
            self.alive = False
            self.state = "GAME_OVER"
            return

        self.snake.segments.insert(0, new_head)
        if self.apple and new_head == self.apple.position:
            self.score += 10
            # Trigger pop animation when eating
            self.snake.eat_animation_timer = 0.2
            # Trigger firecracker particles
            self._spawn_firecracker(new_head[0], new_head[1])
            self._place_food()
        else:
            self.snake.segments.pop()

    def reset(self) -> None:
        """Restore the initial game state."""
        mid_x, mid_y = self.width // 2, self.height // 2
        self.snake = Snake([(mid_x, mid_y), (mid_x, mid_y + 1), (mid_x, mid_y + 2)])
        self.direction = (0, -1)
        self.alive = True
        self.state = "PLAYING"
        self.score = 0
        self.particles = []
        self._place_food()

    def update_animations(self, dt: float) -> None:
        """Update all animation timers and particle physics."""
        if self.apple:
            self.apple.update_animation(dt)
        self.snake.update_animation(dt)
        
        # Update particles and filter out dead ones
        self.particles = [p for p in self.particles if p.update(dt)]

    def get_state(self) -> Dict[str, Any]:
        """Return the current state of the game for rendering."""
        return {
            "snake": self.snake.segments,
            "head_color": self.snake.head_color,
            "body_color": self.snake.body_color,
            "eye_color": self.snake.eye_color,
            "food": self.food,
            "alive": self.alive,
            "score": self.score,
            "state": self.state,
            "eat_animation_timer": self.snake.eat_animation_timer,
            "particles": [
                {
                    "pos": (p.x, p.y),
                    "color": p.color,
                    "alpha": int(255 * (p.lifetime / p.initial_lifetime))
                } for p in self.particles
            ]
        }

    def draw_grid(self, surface: pygame.Surface) -> None:
        """Draw vertical and horizontal lines on the provided surface."""
        for x in range(0, WIDTH + 1, GRID_SIZE):
            pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT + 1, GRID_SIZE):
            pygame.draw.line(surface, GRID_COLOR, (0, y), (WIDTH, y))