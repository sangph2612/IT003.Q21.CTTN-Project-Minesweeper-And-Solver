import pygame


class InputHandler:
    """Translate mouse and keyboard input into game actions."""

    def __init__(self, cell_size, renderer=None):
        """Store rendering context and input-related state."""
        self.cell_size = cell_size
        self.renderer = renderer
        self.restart_pressed = False

    def mouse_to_grid(self, mouse_x, mouse_y):
        """
        Convert mouse coordinates on screen into board row and column indices.

        Args:
            mouse_x (int): Horizontal mouse position in pixels.
            mouse_y (int): Vertical mouse position in pixels.

        Returns:
            tuple[int, int]: Row and column indices on the board.
        """
        origin_x = 0
        origin_y = 0

        if self.renderer is not None:
            origin_x = self.renderer.board_origin_x
            origin_y = self.renderer.board_origin_y

        row = (mouse_y - origin_y) // self.cell_size
        col = (mouse_x - origin_x) // self.cell_size
        return row, col

    def handle_mouse_down(self, event, game_state):
        """
        Handle mouse press events for reset, reveal, and flag actions.

        Args:
            event (pygame.event.Event): Mouse button event from pygame.
            game_state (GameState): Current game state to update.

        Returns:
            bool: True if the game was reset, otherwise False.
        """
        mouse_x, mouse_y = event.pos

        if self.renderer is not None and self.renderer.restart_button_rect.collidepoint(mouse_x, mouse_y):
            self.restart_pressed = True
            game_state.reset_game()
            return True

        row, col = self.mouse_to_grid(mouse_x, mouse_y)

        if not game_state.board.is_inside(row, col):
            return False

        if event.button == 1:
            game_state.reveal_cell(row, col)
        elif event.button == 3:
            game_state.toggle_flag(row, col)
        return False

    def handle_mouse_up(self, event):
        """Reset button press visuals when the left mouse button is released."""
        if event.button == 1:
            self.restart_pressed = False

    def handle_key(self, event, game_state):
        """
        Handle keyboard shortcuts such as restarting the current match.

        Args:
            event (pygame.event.Event): Keyboard event from pygame.
            game_state (GameState): Current game state to update.

        Returns:
            bool: True if the game was reset, otherwise False.
        """
        if event.key == pygame.K_r:
            game_state.reset_game()
            self.restart_pressed = False
            return True
        return False

    def handle_event(self, event, game_state):
        """
        Dispatch a pygame event to the appropriate input handler.

        Args:
            event (pygame.event.Event): Event to process.
            game_state (GameState): Current game state to update.

        Returns:
            bool: True if the game was reset, otherwise False.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            return self.handle_mouse_down(event, game_state)
        if event.type == pygame.MOUSEBUTTONUP:
            self.handle_mouse_up(event)
            return False
        if event.type == pygame.KEYDOWN:
            return self.handle_key(event, game_state)
        return False
