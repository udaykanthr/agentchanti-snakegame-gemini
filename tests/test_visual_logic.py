import pytest
from game import Apple, Snake, Game

def test_snake_set_cute_style_colors():
    """Verify that Snake.set_cute_style() correctly initializes the color tuples."""
    snake = Snake([(0, 0)])
    # Reset to something else first to ensure change is tracked
    snake.body_color = (0, 0, 0)
    snake.head_color = (0, 0, 0)
    snake.eye_color = (0, 0, 0)
    
    snake.set_cute_style()
    assert snake.body_color == (152, 251, 152)
    assert snake.head_color == (255, 182, 193)
    assert snake.eye_color == (255, 255, 255)

def test_apple_update_animation_increments_timer():
    """Verify that Apple.update_animation() properly increments the pulse_timer."""
    apple = Apple((10, 10))
    assert apple.pulse_timer == 0.0
    dt = 0.1
    apple.update_animation(dt)
    assert apple.pulse_timer == pytest.approx(0.1)
    apple.update_animation(dt)
    assert apple.pulse_timer == pytest.approx(0.2)

def test_snake_update_animation_timers():
    """Verify that Snake.update_animation() increments pulse_timer and decrements eat_animation_timer."""
    snake = Snake([(5, 5)])
    snake.eat_animation_timer = 0.2
    snake.pulse_timer = 0.0
    
    dt = 0.05
    snake.update_animation(dt)
    
    # Pulse timer should increase
    assert snake.pulse_timer == pytest.approx(0.05)
    # Eat animation timer should decrease
    assert snake.eat_animation_timer == pytest.approx(0.15)
    
    # Ensure eat_animation_timer doesn't go below 0
    snake.update_animation(0.2)
    assert snake.eat_animation_timer == 0.0

def test_game_update_animations_propagation():
    """Verify that Game.update_animations() updates snake, apple, and particles."""
    game = Game(width=10, height=10)
    game.food = (5, 5)
    
    # Trigger some particles
    game._spawn_firecracker(5, 5)
    initial_particle_count = len(game.particles)
    assert initial_particle_count > 0
    
    initial_snake_pulse = game.snake.pulse_timer
    initial_apple_pulse = game.apple.pulse_timer
    
    dt = 0.1
    game.update_animations(dt)
    
    assert game.snake.pulse_timer == pytest.approx(initial_snake_pulse + dt)
    assert game.apple.pulse_timer == pytest.approx(initial_apple_pulse + dt)
    # Particle lifetimes should decrease
    assert game.particles[0].lifetime == pytest.approx(0.4 - dt)

def test_game_update_animations_no_apple():
    """Verify that Game.update_animations() does not crash if there is no apple."""
    game = Game(width=10, height=10)
    game.apple = None
    
    # Should not raise AttributeError
    game.update_animations(0.1)
    assert game.snake.pulse_timer == pytest.approx(0.1)

def test_eat_animation_trigger_on_tick():
    """Verify that eat_animation_timer and particles are triggered when food is consumed."""
    game = Game(width=10, height=10)
    game.state = "PLAYING"
    
    # Setup: Snake at (5,5), Food at (5,4), Direction Up (0,-1)
    game.snake.segments = [(5, 5), (5, 6), (5, 7)]
    game.direction = (0, -1)
    game.food = (5, 4)
    
    assert game.snake.eat_animation_timer == 0.0
    assert len(game.particles) == 0
    
    game.tick()
    
    # Check that the timer was set to the specific value defined in game.py
    assert game.snake.eat_animation_timer == pytest.approx(0.2)
    assert game.score == 10
    # Particles should have been spawned
    assert len(game.particles) > 0

def test_get_state_visual_data():
    """Verify get_state contains all necessary keys for rendering animations."""
    game = Game(width=10, height=10)
    game.snake.eat_animation_timer = 0.15
    game._spawn_firecracker(2, 2)
    
    state = game.get_state()
    
    assert "head_color" in state
    assert "body_color" in state
    assert "eye_color" in state
    assert "eat_animation_timer" in state
    assert "particles" in state
    assert state["eat_animation_timer"] == pytest.approx(0.15)
    assert len(state["particles"]) > 0
    assert "alpha" in state["particles"][0]

def test_game_get_state_includes_lives():
    """Verify get_state contains lives and UI layout info like margin_top."""
    game = Game(width=10, height=10)
    state = game.get_state()
    assert "lives" in state
    assert "score" in state
    assert "margin_top" in state
    assert state["lives"] == 3