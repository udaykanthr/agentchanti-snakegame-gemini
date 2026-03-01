#!/usr/bin/env python3
"""
Pygame entry point for the Snake game.
Enhanced with menus, score display, and polished animations.
"""

import sys
import math
from typing import Tuple, Optional

import pygame
from game import Game, WIDTH, HEIGHT, GRID_SIZE, BG_COLOR


def create_game() -> Game:
    """Create a new Game instance and set it to the START state."""
    game = Game(width=WIDTH // GRID_SIZE, height=HEIGHT // GRID_SIZE)
    game.state = "START"
    return game


def draw_text(screen: pygame.Surface, text: str, size: int, color: Tuple[int, int, int], y_offset: int = 0):
    """Helper to render centered text on the screen."""
    font = pygame.font.SysFont("Verdana", size, bold=True)
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    screen.blit(text_surf, text_rect)


def draw_ui(screen: pygame.Surface, game: Game):
    """Draw menus and HUD based on the current game state."""
    if game.state == "START":
        # Dim background slightly
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))
        draw_text(screen, "CUTE SNAKE", 72, (255, 182, 193), -50)
        draw_text(screen, "Press SPACE to Play", 32, (255, 255, 255), 40)

    elif game.state == "PLAYING":
        # Draw Score in top-left
        font = pygame.font.SysFont("Verdana", 24, bold=True)
        score_surf = font.render(f"Score: {game.score}", True, (255, 255, 255))
        screen.blit(score_surf, (20, 20))

    elif game.state == "GAME_OVER":
        # Semi-transparent dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        
        draw_text(screen, "GAME OVER", 72, (231, 76, 60), -60)
        draw_text(screen, f"Final Score: {game.score}", 40, (255, 255, 255), 10)
        draw_text(screen, "Press R to Restart or Q to Quit", 24, (200, 200, 200), 80)


def draw_entities(screen: pygame.Surface, game: Game) -> None:
    """Draw the snake and food with enhanced visual effects."""
    game_state = game.get_state()
    cell_size = GRID_SIZE
    eat_timer = game_state.get("eat_animation_timer", 0.0)
    
    snake_color = game_state.get("body_color", (152, 251, 152))
    head_color = game_state.get("head_color", (255, 182, 193))
    food_color = (231, 76, 60)

    # Draw food with breathing animation
    food_pos: Optional[Tuple[int, int]] = game_state.get("food")
    if food_pos is not None:
        fx, fy = food_pos
        pulse_time = pygame.time.get_ticks()
        # Scale formula: 1.0 + 0.15 * sin(ticks * 0.01)
        scale = 1.0 + 0.15 * math.sin(pulse_time * 0.01)
        
        base_size = cell_size - 4
        scaled_size = base_size * scale
        margin = (cell_size - scaled_size) / 2
        
        pygame.draw.rect(
            screen,
            food_color,
            pygame.Rect(
                int(fx * cell_size + margin), 
                int(fy * cell_size + margin), 
                int(scaled_size), 
                int(scaled_size)
            ),
            border_radius=int(scaled_size // 2),
        )

    # Draw snake segments
    snake_segments = game_state.get("snake", [])
    for i, (sx, sy) in enumerate(snake_segments):
        color = head_color if i == 0 else snake_color
        
        # Apply pop animation to head when eating
        head_scale = 1.0
        if i == 0 and eat_timer > 0:
            # Bounce effect: duration is 0.2s as defined in game.py
            head_scale = 1.0 + 0.4 * math.sin((eat_timer / 0.2) * math.pi)
        
        base_size = cell_size - 2
        draw_size = base_size * head_scale
        margin = (cell_size - draw_size) / 2
        
        rect = pygame.Rect(
            int(sx * cell_size + margin), 
            int(sy * cell_size + margin), 
            int(draw_size), 
            int(draw_size)
        )
        pygame.draw.rect(screen, color, rect, border_radius=int(draw_size // 3))
        
        if i == 0:  # Head eyes
            dx, dy = game.direction
            # Center of the current cell
            cx, cy = sx * cell_size + cell_size // 2, sy * cell_size + cell_size // 2
            # Eyes offset from center, scaled with head
            off = 4 * head_scale
            
            eye_w, eye_p = (255, 255, 255), (0, 0, 0)
            
            if dx == 0 and dy == -1:    # UP
                e1, e2 = (cx - off, cy - off), (cx + off, cy - off)
            elif dx == 0 and dy == 1:   # DOWN
                e1, e2 = (cx - off, cy + off), (cx + off, cy + off)
            elif dx == -1 and dy == 0:  # LEFT
                e1, e2 = (cx - off, cy - off), (cx - off, cy + off)
            else:                       # RIGHT
                e1, e2 = (cx + off, cy - off), (cx + off, cy + off)
            
            for e in [e1, e2]:
                pygame.draw.circle(screen, eye_w, (int(e[0]), int(e[1])), int(3 * head_scale))
                pygame.draw.circle(screen, eye_p, (int(e[0]), int(e[1])), int(1 * head_scale))


def main() -> None:
    pygame.init()
    pygame.font.init()
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cute Snake")

    game = create_game()
    clock = pygame.time.Clock()
    
    logic_timer = 0.0
    logic_interval = 0.1  # 10 ticks per second

    while True:
        dt = clock.tick(60) / 1000.0  # Run at 60 FPS for smooth animations
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if game.state == "START":
                    if event.key == pygame.K_SPACE:
                        game.state = "PLAYING"
                elif game.state == "PLAYING":
                    if event.key == pygame.K_UP: game.set_direction(0, -1)
                    elif event.key == pygame.K_DOWN: game.set_direction(0, 1)
                    elif event.key == pygame.K_LEFT: game.set_direction(-1, 0)
                    elif event.key == pygame.K_RIGHT: game.set_direction(1, 0)
                elif game.state == "GAME_OVER":
                    if event.key == pygame.K_r:
                        game.reset()
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

        # Update animations every frame
        game.update_animations(dt)

        # Update game logic at fixed interval
        if game.state == "PLAYING":
            logic_timer += dt
            if logic_timer >= logic_interval:
                game.tick()
                logic_timer = 0

        # Rendering
        screen.fill(BG_COLOR)
        game.draw_grid(screen)
        
        # Draw entities in all states (static when not playing)
        draw_entities(screen, game)
        
        # Draw UI overlays
        draw_ui(screen, game)
        
        pygame.display.flip()

if __name__ == "__main__":
    main()