#!/usr/bin/env python3
"""
Pygame entry point for the Snake game.
Renders the arena, entities, and UI including a scoreboard in the top margin.
"""

import sys
import pygame
from typing import Tuple, Optional
from game import Game, WIDTH, HEIGHT, GRID_SIZE, BG_COLOR


def create_game() -> Game:
    """Initialize a new game instance with the cute style applied."""
    game = Game(width=WIDTH // GRID_SIZE, height=HEIGHT // GRID_SIZE)
    game.snake.set_cute_style()
    game.state = "START"
    return game


def draw_text(screen: pygame.Surface, text: str, size: int, color: Tuple[int, int, int], x: int, y: int, center: bool = True):
    """Utility to render text at a specific position."""
    font = pygame.font.SysFont("Verdana", size, bold=True)
    text_surf = font.render(text, True, color)
    if center:
        text_rect = text_surf.get_rect(center=(x, y))
    else:
        text_rect = text_surf.get_rect(topleft=(x, y))
    screen.blit(text_surf, text_rect)


def draw_ui(screen: pygame.Surface, game: Game):
    """Render UI overlays and the scoreboard based on the current game state."""
    game_state = game.get_state()
    margin_px = game_state["margin_top"] * GRID_SIZE

    # Always draw the scoreboard background in the top margin
    pygame.draw.rect(screen, (18, 48, 20), pygame.Rect(0, 0, WIDTH, margin_px))
    pygame.draw.line(screen, (255, 255, 255, 50), (0, margin_px), (WIDTH, margin_px), 2)

    # Render Score and Lives
    draw_text(screen, f"SCORE: {game_state['score']}", 24, (255, 255, 255), 20, margin_px // 2, center=False)
    
    # Draw Lives as cute hearts or circles
    lives_x = WIDTH - 150
    draw_text(screen, "LIVES:", 20, (255, 182, 193), lives_x, margin_px // 2, center=False)
    for i in range(game_state["lives"]):
        pygame.draw.circle(screen, (231, 76, 60), (lives_x + 85 + i * 25, margin_px // 2 + 2), 8)

    if game.state == "START":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))
        draw_text(screen, "CUTE SNAKE", 72, (255, 182, 193), WIDTH // 2, HEIGHT // 2 - 50)
        draw_text(screen, "Press SPACE to Play", 32, (255, 255, 255), WIDTH // 2, HEIGHT // 2 + 40)

    elif game.state == "GAME_OVER":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        draw_text(screen, "GAME OVER", 72, (231, 76, 60), WIDTH // 2, HEIGHT // 2 - 60)
        draw_text(screen, f"Final Score: {game_state['score']}", 40, (255, 255, 255), WIDTH // 2, HEIGHT // 2 + 10)
        draw_text(screen, "Press R to Restart or Q to Quit", 24, (200, 200, 200), WIDTH // 2, HEIGHT // 2 + 80)


def draw_entities(screen: pygame.Surface, game: Game) -> None:
    """Render all game entities using the visual state provided by the game logic."""
    game_state = game.get_state()
    shake_x, shake_y = game_state.get("shake_offset", (0, 0))
    
    # Draw background grid with shake
    game.draw_grid(screen, offset=(shake_x, shake_y))
    
    cell_size = GRID_SIZE
    food_pos: Optional[Tuple[int, int]] = game_state.get("food")
    food_scale = game_state.get("food_scale", 1.0)
    
    # Draw food (Apple)
    if food_pos is not None:
        fx, fy = food_pos
        base_size = cell_size - 4
        scaled_size = base_size * food_scale
        margin = (cell_size - scaled_size) / 2
        
        pygame.draw.rect(
            screen,
            (231, 76, 60),
            pygame.Rect(
                int(fx * cell_size + margin + shake_x), 
                int(fy * cell_size + margin + shake_y), 
                int(scaled_size), 
                int(scaled_size)
            ),
            border_radius=int(scaled_size // 2),
        )

    # Draw snake
    snake_segments = game_state.get("snake", [])
    snake_colors = game_state.get("snake_colors", [])
    head_scale = game_state.get("head_scale", 1.0)
    eye_color = game_state.get("eye_color", (255, 255, 255))
    
    for i, (sx, sy) in enumerate(snake_segments):
        color = snake_colors[i] if i < len(snake_colors) else (152, 251, 152)
        seg_scale = head_scale if i == 0 else 1.0
        
        base_size = cell_size - 2
        draw_size = base_size * seg_scale
        margin = (cell_size - draw_size) / 2
        
        rect = pygame.Rect(
            int(sx * cell_size + margin + shake_x), 
            int(sy * cell_size + margin + shake_y), 
            int(draw_size), 
            int(draw_size)
        )
        pygame.draw.rect(screen, color, rect, border_radius=int(draw_size // 3))
        
        if i == 0:  # Head Eyes
            dx, dy = game.direction
            cx = sx * cell_size + cell_size // 2 + shake_x
            cy = sy * cell_size + cell_size // 2 + shake_y
            off = 4 * seg_scale
            
            if dx == 0 and dy == -1: e1, e2 = (cx - off, cy - off), (cx + off, cy - off)
            elif dx == 0 and dy == 1: e1, e2 = (cx - off, cy + off), (cx + off, cy + off)
            elif dx == -1 and dy == 0: e1, e2 = (cx - off, cy - off), (cx - off, cy + off)
            else: e1, e2 = (cx + off, cy - off), (cx + off, cy + off)
            
            for e in [e1, e2]:
                pygame.draw.circle(screen, eye_color, (int(e[0]), int(e[1])), int(3 * seg_scale))
                pygame.draw.circle(screen, (0, 0, 0), (int(e[0]), int(e[1])), int(1 * seg_scale))

    # Draw particles
    for p in game_state.get("particles", []):
        pos, color, alpha = p["pos"], p["color"], p["alpha"]
        p_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(p_surf, (*color, alpha), (2, 2), 2)
        screen.blit(p_surf, (int(pos[0] - 2 + shake_x), int(pos[1] - 2 + shake_y)))


def main() -> None:
    """Primary game loop and event handling."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cute Snake")

    game = create_game()
    clock = pygame.time.Clock()
    logic_timer = 0.0
    logic_interval = 0.1 

    while True:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if game.state == "START" and event.key == pygame.K_SPACE:
                    game.state = "PLAYING"
                elif game.state == "PLAYING":
                    if event.key == pygame.K_UP: game.set_direction(0, -1)
                    elif event.key == pygame.K_DOWN: game.set_direction(0, 1)
                    elif event.key == pygame.K_LEFT: game.set_direction(-1, 0)
                    elif event.key == pygame.K_RIGHT: game.set_direction(1, 0)
                elif game.state == "GAME_OVER":
                    if event.key == pygame.K_r: game.reset()
                    elif event.key == pygame.K_q: pygame.quit(); sys.exit()

        game.update_animations(dt)
        
        if game.state == "PLAYING":
            logic_timer += dt
            if logic_timer >= logic_interval:
                game.tick()
                logic_timer = 0

        screen.fill(BG_COLOR)
        draw_entities(screen, game)
        draw_ui(screen, game)
        pygame.display.flip()

if __name__ == "__main__":
    main()