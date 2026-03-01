import pytest
from game import Game, WIDTH, HEIGHT, GRID_SIZE

def test_tick_updates_head_position(monkeypatch):
    """
    After a tick, the snake's head should move one cell forward 
    in the current direction. Verified with default board dimensions (40x30).
    """
    # Mock food placement to avoid interference with segment length logic
    monkeypatch.setattr("random.choice", lambda x: (0, 0))
    g = Game() # Default dimensions: 40x30
    g.state = "PLAYING"
    
    # Initial head is at (20, 15), default direction is Up (0, -1)
    g.snake.segments = [(20, 15), (20, 16), (20, 17)]
    g.tick()
    
    # Head should move from 15 to 14
    assert g.snake.segments[0] == (20, 14)
    # Length should remain 3 as it didn't eat food
    assert len(g.snake.segments) == 3

def test_food_consumption_and_growth():
    """
    When the snake moves onto a food cell, it should grow by one segment
    and a new food should be placed.
    """
    g = Game()
    g.state = "PLAYING"
    head_x, head_y = g.snake.segments[0]
    # Place food directly in front of the head (Up)
    food_pos = (head_x, head_y - 1)
    g.food = food_pos
    
    old_length = len(g.snake.segments)
    g.tick()
    
    # Snake should grow
    assert len(g.snake.segments) == old_length + 1
    # New head should be at food position
    assert g.snake.segments[0] == food_pos
    # Food should have moved to a new location
    assert g.food != food_pos

def test_death_on_wall_collision_top():
    """Moving the snake out of the top grid boundary (y < 0) should end the game."""
    g = Game() # 40x30 grid
    g.state = "PLAYING"
    # Place head at the very top row
    g.snake.segments = [(20, 0), (20, 1), (20, 2)]
    g.direction = (0, -1) # Move Up
    
    g.tick()
    assert g.alive is False
    assert g.state == "GAME_OVER"

def test_death_on_wall_collision_bottom():
    """Moving the snake out of the bottom grid boundary (y >= height) should end the game."""
    g = Game() # 40x30 grid
    g.state = "PLAYING"
    # Place head at the very bottom row (height is 30, so max index is 29)
    bottom_y = g.height - 1
    g.snake.segments = [(20, bottom_y), (20, bottom_y - 1), (20, bottom_y - 2)]
    g.direction = (0, 1) # Move Down
    
    g.tick()
    assert g.alive is False
    assert g.state == "GAME_OVER"

def test_death_on_wall_collision_left():
    """Moving the snake out of the left grid boundary (x < 0) should end the game."""
    g = Game() # 40x30 grid
    g.state = "PLAYING"
    # Place head at the far left column
    g.snake.segments = [(0, 15), (1, 15), (2, 15)]
    g.direction = (-1, 0) # Move Left
    
    g.tick()
    assert g.alive is False
    assert g.state == "GAME_OVER"

def test_death_on_wall_collision_right():
    """Moving the snake out of the right grid boundary (x >= width) should end the game."""
    g = Game() # 40x30 grid
    g.state = "PLAYING"
    # Place head at the far right column (width is 40, so max index is 39)
    right_x = g.width - 1
    g.snake.segments = [(right_x, 15), (right_x - 1, 15), (right_x - 2, 15)]
    g.direction = (1, 0) # Move Right
    
    g.tick()
    assert g.alive is False
    assert g.state == "GAME_OVER"

def test_self_collision_ends_game():
    """Moving the snake into its own body should end the game."""
    g = Game()
    g.state = "PLAYING"
    # Create a snake that is coiled such that a move Up hits its own segment
    # Head at (5, 5), segments at (5, 4) would be a collision
    g.snake.segments = [(5, 5), (4, 5), (4, 4), (5, 4), (6, 4)]
    g.direction = (0, -1) # Move Up into (5, 4)
    
    g.tick()
    assert g.alive is False
    assert g.state == "GAME_OVER"