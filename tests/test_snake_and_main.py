import pytest
from game import Snake
from main import create_game

def test_snake_initial_colors():
    """Verify default snake colors are correctly set before styling."""
    s = Snake([(0, 0)])
    # Matching the default pastel colors defined in game.py Snake.__init__
    assert s.body_color == (152, 251, 152)  # Pastel Green
    assert s.head_color == (255, 182, 193)  # Pastel Pink
    assert s.eye_color == (255, 255, 255)

def test_snake_cute_style():
    """Verify cute style color changes apply the correct palette."""
    s = Snake([(0, 0)])
    s.set_cute_style()
    assert s.body_color == (152, 251, 152)  # Pastel Green
    assert s.head_color == (255, 182, 193)  # Pastel Pink
    assert s.eye_color == (255, 255, 255)

def test_create_game_helper():
    """Verify create_game helper initializes game with cute style and proper snake position."""
    # main.create_game() does not accept width/height arguments
    g = create_game()
    # Default dimensions from WIDTH // GRID_SIZE and HEIGHT // GRID_SIZE
    assert g.width == 40
    assert g.height == 30
    
    # Check if cute style was applied
    assert g.snake.body_color == (152, 251, 152)
    
    # Check if snake is placed in the middle (40//2, (4+30)//2)
    mid_x, mid_y = 20, 17
    expected = [(mid_x, mid_y), (mid_x, mid_y + 1), (mid_x, mid_y + 2)]
    assert g.snake.segments == expected
    
    # Check if food is placed
    assert g.food is not None