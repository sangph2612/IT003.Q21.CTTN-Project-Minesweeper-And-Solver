import pygame

from core.config import CELL_SIZE, COLS, FPS, MINE_COUNT, ROWS, WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from core.game_logic import GameState
from core.input_handler import InputHandler
from core.renderer import Renderer


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

        self.cell_size = CELL_SIZE

        rows = ROWS
        cols = COLS

        self.game = GameState(rows, cols, num_mines=MINE_COUNT)
        self.renderer = Renderer(self.screen, self.cell_size)
        self.input_handler = InputHandler(self.cell_size, self.renderer)

    def reset_timer(self):
        """Reset the in-game timer for a new match."""
        self.start_ticks = pygame.time.get_ticks()
        self.frozen_elapsed_seconds = None

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

                did_reset = self.input_handler.handle_event(event, self.game)
                if did_reset:
                    self.reset_timer()
                    continue

                if (not previous_victory and self.game.victory) or (not previous_game_over and self.game.game_over):
                    self.frozen_elapsed_seconds = (pygame.time.get_ticks() - self.start_ticks) // 1000

    def update(self):
        """Update game state between frames if future logic is needed."""
        pass

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

        self.renderer.draw_background()
        self.renderer.draw_board(self.game.board, animation_time)
        self.renderer.draw_restart_button(self.game, self.input_handler.restart_pressed)
        self.renderer.draw_time_label(elapsed_seconds, frozen=frozen)
        self.renderer.draw_status(self.game, animation_time)
