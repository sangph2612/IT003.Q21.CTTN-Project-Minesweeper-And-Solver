import pygame

from core.config import CELL_SIZE, COLS, FPS, MINE_COUNT, ROWS, WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from core.game_logic import GameState
from core.input_handler import InputHandler
from core.renderer import Renderer
from core.solver_bridge import SolverBridge


class App:
    """Manage application setup, the main loop, and top-level game flow."""

    def __init__(self):
        """Initialize pygame, create the window, and prepare game components."""
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.start_ticks = pygame.time.get_ticks()
        self.frozen_elapsed_seconds = None
        self.last_auto_solver_tick = 0
        self.auto_solver_interval_ms = 300
        self.auto_solver_enabled = False

        self.cell_size = CELL_SIZE

        rows = ROWS
        cols = COLS

        self.game = GameState(rows, cols, num_mines=MINE_COUNT)
        self.renderer = Renderer(self.screen, self.cell_size)
        self.input_handler = InputHandler(self.cell_size, self.renderer)
        self.solver_bridge = SolverBridge()

    def reset_timer(self):
        """Reset the in-game timer for a new match."""
        self.start_ticks = pygame.time.get_ticks()
        self.frozen_elapsed_seconds = None
        self.last_auto_solver_tick = 0

    def run(self):
        """
        Run the main application loop until the window is closed.

        Returns:
            None
        """
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

    def handle_events(self):
        """
        Process pygame events, player input, and match-ending timer freeze.

        Returns:
            None
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                previous_game_over = self.game.game_over
                previous_victory = self.game.victory

                did_reset = self.input_handler.handle_event(event, self.game, self)
                if did_reset:
                    self.reset_timer()
                    continue

                if (not previous_victory and self.game.victory) or (not previous_game_over and self.game.game_over):
                    self.frozen_elapsed_seconds = (pygame.time.get_ticks() - self.start_ticks) // 1000

    def update(self):
        """Update game state between frames and drive auto solver when enabled."""
        if not self.auto_solver_enabled:
            return
        if not self.solver_bridge.is_available():
            return
        if self.game.game_over or self.game.victory:
            return

        current_tick = pygame.time.get_ticks()
        if current_tick - self.last_auto_solver_tick < self.auto_solver_interval_ms:
            return

        result = self.solver_bridge.apply_next_move(self.game)
        self.last_auto_solver_tick = current_tick

        if result == "ERROR":
            self.auto_solver_enabled = False
            return

        if self.game.victory or self.game.game_over:
            self.frozen_elapsed_seconds = (pygame.time.get_ticks() - self.start_ticks) // 1000

    def draw(self):
        """
        Render the current game scene, UI panels, and timer information.

        Returns:
            None
        """
        if (self.game.victory or self.game.game_over) and self.frozen_elapsed_seconds is not None:
            elapsed_seconds = self.frozen_elapsed_seconds
            frozen = True
        else:
            elapsed_seconds = (pygame.time.get_ticks() - self.start_ticks) // 1000
            frozen = False

        animation_time = pygame.time.get_ticks()
        solver_available = self.solver_bridge.is_available()

        self.renderer.draw_background()
        self.renderer.draw_board(self.game.board, animation_time)
        self.renderer.draw_restart_button(self.game, self.input_handler.restart_pressed)
        self.renderer.draw_auto_solver_button(
            self.auto_solver_enabled,
            self.input_handler.auto_solver_pressed,
            available=solver_available,
        )
        self.renderer.draw_time_label(elapsed_seconds, frozen=frozen)
        self.renderer.draw_status(
            self.game,
            animation_time,
            auto_solver_enabled=self.auto_solver_enabled,
            solver_available=solver_available,
        )
