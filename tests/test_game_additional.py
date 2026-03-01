import pytest
from game import Game, Snake

def test_initial_food_within_bounds():
    """Food should always spawn within board limits."""
    g = Game(width=7, height=7)
    assert g.food is not None
    x, y = g.food
    assert 0 <= x < g.width and 0 <= y < g.height

def test_no_food_when_board_full():
    """When snake occupies entire board, no food should be spawned."""
    g = Game(width=3, height=3)
    # 3x3 board = 9 cells
    full_segments = [(x, y) for x in range(3) for y in range(3)]
    g.snake.segments = full_segments
    g._place_food()
    assert g.food is None

def test_tick_no_op_when_dead():
    """Ticks should not change game state if the snake is dead."""
    g = Game(width=10, height=10)
    g.alive = False
    initial_segments = list(g.snake.segments)
    g.tick()
    assert g.snake.segments == initial_segments

def test_get_state():
    """Verify get_state returns the correct dictionary representation."""
    g = Game(width=5, height=5)
    state = g.get_state()
    assert state["alive"] is True
    assert "snake" in state
    assert "food" in state
    assert "score" in state
    assert "head_color" in state
    assert "body_color" in state
    assert state["state"] == "PLAYING"

def test_food_setter_none():
    """Setting food to None should clear the apple instance."""
    g = Game()
    g.food = None
    assert g.apple is None
    assert g.food is None