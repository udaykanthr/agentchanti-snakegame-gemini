import pytest
from game import Game, WIDTH, HEIGHT, GRID_SIZE

def test_tick_updates_head_position(monkeypatch):
    """
    After a tick, the snake's head should move one cell forward 
    in the current direction. Verified with default board dimensions (40x30).
    """
    # Mock food placement to avoid interference with segment length logic
    monkeypatch.setattr("random.choice", lambda x: (20, 4))
    g = Game() # Default dimensions: 40x30, margin_top: 4
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

def test_life_loss_on_wall_collision_top():
    """Colliding with the top wall should decrement lives and respawn the snake."""
    g = Game() # 40x30 grid, margin_top = 4
    g.state = "PLAYING"
    g.lives = 3
    # Place head at the very top playable row
    g.snake.segments = [(20, g.margin_top), (20, g.margin_top + 1), (20, g.margin_top + 2)]
    g.direction = (0, -1) # Move Up
    
    g.tick()
    # Should lose a life but stay playing (respawn)
    assert g.lives == 2
    assert g.alive is True
    assert g.state == "PLAYING"
    # Head should not be at the out-of-bounds position
    assert g.snake.segments[0] != (20, g.margin_top - 1)

def test_life_loss_on_wall_collision_bottom():
    """Colliding with the bottom wall should decrement lives and respawn the snake."""
    g = Game()
    g.state = "PLAYING"
    g.lives = 3
    bottom_y = g.height - 1
    g.snake.segments = [(20, bottom_y), (20, bottom_y - 1), (20, bottom_y - 2)]
    g.direction = (0, 1) # Move Down
    
    g.tick()
    assert g.lives == 2
    assert g.alive is True
    assert g.state == "PLAYING"
    assert g.snake.segments[0] != (20, bottom_y + 1)

def test_life_loss_on_wall_collision_left():
    """Colliding with the left wall should decrement lives and respawn the snake."""
    g = Game()
    g.state = "PLAYING"
    g.lives = 3
    g.snake.segments = [(0, 15), (1, 15), (2, 15)]
    g.direction = (-1, 0) # Move Left
    
    g.tick()
    assert g.lives == 2
    assert g.alive is True
    assert g.state == "PLAYING"
    assert g.snake.segments[0] != (-1, 15)

def test_life_loss_on_wall_collision_right():
    """Colliding with the right wall should decrement lives and respawn the snake."""
    g = Game()
    g.state = "PLAYING"
    g.lives = 3
    right_x = g.width - 1
    g.snake.segments = [(right_x, 15), (right_x - 1, 15), (right_x - 2, 15)]
    g.direction = (1, 0) # Move Right
    
    g.tick()
    assert g.lives == 2
    assert g.alive is True
    assert g.state == "PLAYING"
    assert g.snake.segments[0] != (right_x + 1, 15)

def test_game_over_after_all_lives_lost():
    """Colliding when lives are 1 should trigger GAME_OVER."""
    g = Game()
    g.state = "PLAYING"
    g.lives = 1
    # Trigger a wall collision
    g.snake.segments = [(0, 15), (1, 15), (2, 15)]
    g.direction = (-1, 0)
    
    g.tick()
    assert g.lives == 0
    assert g.alive is False
    assert g.state == "GAME_OVER"

def test_self_collision_ends_game():
    """
    Moving the snake into its own body should result in life loss or game over.
    Following the current logic of life reduction on collision.
    """
    g = Game()
    g.state = "PLAYING"
    g.lives = 1
    # Create a snake that is coiled such that a move Up hits its own segment
    # Head at (5, 10), segments at (5, 9) would be a collision
    g.snake.segments = [(5, 10), (4, 10), (4, 9), (5, 9), (6, 9)]
    g.direction = (0, -1) # Move Up into (5, 9)
    
    g.tick()
    # Since lives was 1, it should be Game Over
    assert g.lives == 0
    assert g.alive is False
    assert g.state == "GAME_OVER"