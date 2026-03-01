import pytest
from game import Game, WIDTH, HEIGHT, GRID_SIZE

def test_default_initialization():
    """Verify the game initializes with default dimensions derived from 800x600 and grid size 20."""
    g = Game()
    # 800 // 20 = 40
    # 600 // 20 = 30
    expected_width = WIDTH // GRID_SIZE
    expected_height = HEIGHT // GRID_SIZE
    
    assert g.width == expected_width
    assert g.height == expected_height
    assert g.width == 40
    assert g.height == 30

def test_invalid_dimensions_raises():
    """Creating a game with dimensions smaller than 3x3 must raise ValueError."""
    with pytest.raises(ValueError):
        Game(width=2, height=5)
    with pytest.raises(ValueError):
        Game(width=5, height=2)
    with pytest.raises(ValueError):
        Game(width=0, height=0)

def test_initial_state_dimensions():
    """Verify the game board dimensions are correctly assigned when provided explicitly."""
    g = Game(width=10, height=15)
    assert g.width == 10
    assert g.height == 15

def test_initial_snake_setup_with_defaults():
    """
    Verify that a newly created game with default dimensions (40x30) has a snake
    placed in the middle of the playable board (margin_top=4).
    """
    g = Game()
    # Default mid points for 40x30 with margin_top 4: 
    # mid_x = 20, mid_y = (4 + 30) // 2 = 17
    mid_x, mid_y = 20, 17
    expected_segments = [(mid_x, mid_y), (mid_x, mid_y + 1), (mid_x, mid_y + 2)]
    
    assert g.snake.segments == expected_segments
    assert len(g.snake.segments) == 3
    assert g.direction == (0, -1)  # Initial direction Up
    assert g.alive is True

def test_initial_snake_setup_custom():
    """
    Verify that a newly created game with custom dimensions has a snake
    placed in the middle of the playable board.
    """
    width, height = 20, 20
    g = Game(width=width, height=height)
    
    mid_x, mid_y = width // 2, (g.margin_top + height) // 2
    expected_segments = [(mid_x, mid_y), (mid_x, mid_y + 1), (mid_x, mid_y + 2)]
    
    assert g.snake.segments == expected_segments
    assert len(g.snake.segments) == 3

def test_set_direction_logic():
    """
    Setting a direction that is not the reverse of the current one should
    update the snake's direction. Reverses should be ignored.
    """
    g = Game(width=10, height=20)
    # Current direction is Up (0, -1)
    
    # Valid: Right
    g.set_direction(1, 0)
    assert g.direction == (1, 0)

    # Invalid: Left (reverse of Right)
    g.set_direction(-1, 0)
    assert g.direction == (1, 0)

    # Valid: Down
    g.set_direction(0, 1)
    assert g.direction == (0, 1)

    # Invalid: Up (reverse of Down)
    g.set_direction(0, -1)
    assert g.direction == (0, 1)

def test_set_direction_ignore_dead_game():
    """set_direction must be ignored if the game is over."""
    g = Game(width=10, height=20)
    # set_direction checks for self.state == "GAME_OVER"
    g.state = "GAME_OVER"
    g.alive = False
    old_dir = g.direction
    
    # Attempt to set a new valid direction
    g.set_direction(1, 0)
    assert g.direction == old_dir