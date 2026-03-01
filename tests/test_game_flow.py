import pytest
from game import Game, create_game

def test_create_game_initial_state():
    """Verify that create_game helper initializes the game in START state with score 0 and 3 lives."""
    g = create_game()
    assert g.state == "START"
    assert g.score == 0
    assert g.lives == 3
    assert g.alive is True
    # Default dimensions: WIDTH(800) // GRID_SIZE(20) = 40
    assert g.width == 40
    assert g.height == 30

def test_transition_start_to_playing_via_direction():
    """Verify that setting a direction when in START state transitions the game to PLAYING."""
    g = create_game()
    assert g.state == "START"
    
    # Change direction to Right
    g.set_direction(1, 0)
    
    assert g.state == "PLAYING"
    assert g.direction == (1, 0)

def test_tick_inactive_states():
    """Verify that tick() does not move the snake if the state is not PLAYING."""
    g = create_game()
    assert g.state == "START"
    initial_segments = list(g.snake.segments)
    
    # Tick in START state
    g.tick()
    assert g.snake.segments == initial_segments
    
    # Tick in GAME_OVER state
    g.state = "GAME_OVER"
    g.alive = False
    g.tick()
    assert g.snake.segments == initial_segments

def test_score_increment_flow():
    """Verify score increases correctly when the snake eats food during game ticks."""
    g = Game(width=10, height=20)
    g.state = "PLAYING"
    g.score = 0
    
    # Position snake head at (5, 10)
    g.snake.segments = [(5, 10), (5, 11), (5, 12)]
    g.direction = (0, -1) # Up
    
    # Place food at (5, 9)
    g.food = (5, 9)
    
    g.tick()
    
    assert g.score == 10
    assert g.snake.segments[0] == (5, 9)
    assert len(g.snake.segments) == 4
    # Food should be relocated
    assert g.food != (5, 9)

def test_game_over_flow_wall_collision():
    """Verify the transition to GAME_OVER when hitting a boundary with 1 life remaining."""
    g = Game(width=10, height=20)
    g.state = "PLAYING"
    g.lives = 1
    
    # Place head at the left edge
    g.snake.segments = [(0, 10), (1, 10), (2, 10)]
    g.direction = (-1, 0) # Move Left into wall
    
    g.tick()
    
    assert g.state == "GAME_OVER"
    assert g.alive is False

def test_reset_functionality():
    """Verify that reset() restores all game attributes to their starting values."""
    g = Game(width=20, height=20)
    g.state = "GAME_OVER"
    g.score = 150
    g.lives = 0
    g.alive = False
    g.direction = (1, 0)
    
    g.reset()
    
    assert g.state == "PLAYING"
    assert g.score == 0
    assert g.lives == 3
    assert g.alive is True
    assert g.direction == (0, -1) # Default Up
    assert len(g.snake.segments) == 3
    # Snake should be centered for 20x20 with margin_top 4: (10, 12), (10, 13), (10, 14)
    assert g.snake.segments[0] == (10, 12)

def test_set_direction_ignored_in_game_over():
    """Verify that direction cannot be changed once the state is GAME_OVER."""
    g = Game()
    g.state = "GAME_OVER"
    original_direction = g.direction
    
    # Try to change direction
    g.set_direction(1, 0)
    
    assert g.direction == original_direction