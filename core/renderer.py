import pygame

from core.config import BOTTOM_BAR_HEIGHT, BOARD_PADDING, TOP_BAR_HEIGHT, WINDOW_HEIGHT, WINDOW_WIDTH


class Renderer:
    """Render the Minesweeper board, interface panels, and status indicators."""

    def __init__(self, screen, cell_size):
        """Load drawing resources and precompute layout rectangles."""
        self.screen = screen
        self.cell_size = cell_size
        self.title_font = pygame.font.SysFont("segoe ui", 24, bold=True)
        self.font = pygame.font.SysFont("segoe ui", 20)
        self.small_font = pygame.font.SysFont("segoe ui", 17)
        self.tiny_font = pygame.font.SysFont("segoe ui", 15)

        self.bg_color = (235, 244, 239)
        self.panel_color = (248, 251, 249)
        self.card_color = (255, 255, 255)
        self.border_color = (191, 219, 205)
        self.soft_border = (214, 229, 220)
        self.text_color = (31, 41, 55)
        self.subtle_text = (107, 114, 128)
        self.accent_color = (34, 197, 94)
        self.danger_color = (239, 68, 68)
        self.cell_border_color = (211, 223, 216)
        self.shadow_color = (170, 190, 179)

        self.tile = pygame.image.load("assets/tile.png").convert_alpha()
        self.flag_image = pygame.image.load("assets/flag.png").convert_alpha()
        self.mine_image = pygame.image.load("assets/cut.png").convert_alpha()
        self.revealed_image = [
            pygame.image.load(("assets/{}.png").format(i)).convert_alpha()
            for i in range(9)
        ]

        self.tile = pygame.transform.scale(self.tile, (cell_size, cell_size))
        self.flag_image = pygame.transform.scale(self.flag_image, (cell_size, cell_size))
        self.mine_image = pygame.transform.scale(self.mine_image, (cell_size, cell_size))
        self.revealed_image = [
            pygame.transform.scale(image, (cell_size, cell_size))
            for image in self.revealed_image
        ]

        self.board_origin_x = BOARD_PADDING
        self.board_origin_y = TOP_BAR_HEIGHT + BOARD_PADDING
        board_width = WINDOW_WIDTH - BOARD_PADDING * 2
        board_height = WINDOW_HEIGHT - TOP_BAR_HEIGHT - BOTTOM_BAR_HEIGHT - BOARD_PADDING * 2

        self.header_rect = pygame.Rect(12, 10, WINDOW_WIDTH - 24, TOP_BAR_HEIGHT - 16)
        self.footer_rect = pygame.Rect(12, WINDOW_HEIGHT - BOTTOM_BAR_HEIGHT + 6, WINDOW_WIDTH - 24, BOTTOM_BAR_HEIGHT - 16)
        self.board_frame_rect = pygame.Rect(
            self.board_origin_x - 8,
            self.board_origin_y - 8,
            board_width + 16,
            board_height + 16,
        )
        self.restart_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 26, 14, 52, 52)

    def draw_rounded_panel(self, rect, fill_color, border_color=None, radius=18, shadow_offset=4):
        """Draw a rounded panel with an optional border and drop shadow."""
        shadow_rect = rect.move(0, shadow_offset)
        pygame.draw.rect(self.screen, self.shadow_color, shadow_rect, border_radius=radius)
        pygame.draw.rect(self.screen, fill_color, rect, border_radius=radius)
        if border_color is not None:
            pygame.draw.rect(self.screen, border_color, rect, width=1, border_radius=radius)

    def draw_background(self):
        """Draw the window background and the static interface panels."""
        self.screen.fill(self.bg_color)
        self.draw_rounded_panel(self.header_rect, self.panel_color, self.soft_border, radius=20, shadow_offset=3)
        self.draw_rounded_panel(self.footer_rect, self.panel_color, self.soft_border, radius=20, shadow_offset=3)
        self.draw_rounded_panel(self.board_frame_rect, self.card_color, self.border_color, radius=20, shadow_offset=5)

        self.draw_text("Minesweeper", self.header_rect.x + 16, self.header_rect.y + 15, self.title_font, self.text_color)
        self.draw_text("Clean mode", self.header_rect.x + 16, self.header_rect.y + 40, self.tiny_font, self.subtle_text)

    def get_cell_rect(self, row, col):
        """Return the screen rectangle for a board cell at the given coordinates."""
        x = col * self.cell_size + self.board_origin_x
        y = row * self.cell_size + self.board_origin_y
        return pygame.Rect(x, y, self.cell_size, self.cell_size)

    def draw_board(self, board, animation_time=0):
        """
        Draw all visible cells of the current board state.

        Args:
            board (Board): Board object containing the cells to render.
            animation_time (int): Current tick count used for simple animation effects.

        Returns:
            None
        """
        pulse = 0
        if animation_time:
            pulse = (animation_time % 1200) / 1200.0

        for row in range(board.rows):
            for col in range(board.cols):
                cell = board.get_cell(row, col)
                self.draw_cell(cell, row, col, pulse)

    def draw_cell(self, cell, row, col, pulse=0):
        """
        Draw one cell, including revealed values, mines, flags, and effects.

        Args:
            cell (Cell): Cell object to render.
            row (int): Row index of the cell.
            col (int): Column index of the cell.
            pulse (float): Animation factor used for zero-cell glow effects.

        Returns:
            None
        """
        rect = self.get_cell_rect(row, col)

        if cell.is_revealed:
            if cell.is_mine:
                self.screen.blit(self.mine_image, rect.topleft)
            else:
                self.screen.blit(self.revealed_image[cell.neighbor_mines], rect.topleft)
        else:
            self.screen.blit(self.tile, rect.topleft)
            if cell.is_flagged:
                self.screen.blit(self.flag_image, rect.topleft)

        pygame.draw.rect(self.screen, self.cell_border_color, rect, 1, border_radius=6)

        if cell.is_revealed and not cell.is_mine and cell.neighbor_mines == 0 and pulse > 0:
            glow_alpha = int(20 * pulse)
            glow_surface = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
            glow_surface.fill((120, 255, 180, glow_alpha))
            self.screen.blit(glow_surface, rect.topleft)

    def draw_text(self, text, x, y, font=None, color=None):
        """Render a text string to the screen using the chosen font and color."""
        if font is None:
            font = self.font
        if color is None:
            color = self.text_color
        surface = font.render(str(text), True, color)
        self.screen.blit(surface, (x, y))

    def draw_restart_button(self, game_state, pressed=False):
        """
        Draw the smiley restart button with an expression matching the game state.

        Args:
            game_state (GameState): Current game state used to choose the button face.
            pressed (bool): Whether the button is currently being pressed.

        Returns:
            None
        """
        button_rect = self.restart_button_rect.copy()
        if pressed:
            button_rect.y += 2

        shadow_rect = button_rect.move(0, 3)
        pygame.draw.ellipse(self.screen, (189, 204, 194), shadow_rect)
        pygame.draw.ellipse(self.screen, (255, 230, 109), button_rect)
        pygame.draw.ellipse(self.screen, (217, 177, 37), button_rect, 2)

        left_eye = (button_rect.x + 17, button_rect.y + 18)
        right_eye = (button_rect.x + 35, button_rect.y + 18)
        pygame.draw.circle(self.screen, self.text_color, left_eye, 3)
        pygame.draw.circle(self.screen, self.text_color, right_eye, 3)

        mouth_rect = pygame.Rect(
            button_rect.x + 13,
            button_rect.y + 22,
            26,
            14,
        )

        if game_state.victory:
            pygame.draw.arc(self.screen, self.text_color, mouth_rect, 3.24, 6.0, 3)
        elif game_state.game_over:
            pygame.draw.arc(self.screen, self.text_color, mouth_rect, 0.1, 3.04, 3)
        else:
            pygame.draw.arc(self.screen, self.text_color, mouth_rect, 0.35, 2.79, 3)

    def draw_time_label(self, elapsed_seconds, frozen=False):
        """
        Draw the elapsed time label and highlight it when the timer is frozen.

        Args:
            elapsed_seconds (int): Number of elapsed seconds to display.
            frozen (bool): Whether the timer should be shown in a frozen state.

        Returns:
            None
        """
        label_color = self.subtle_text
        value_color = self.text_color if not frozen else self.accent_color
        self.draw_text("Time", self.header_rect.right - 110, self.header_rect.y + 10, self.tiny_font, label_color)
        self.draw_text(f"{elapsed_seconds:03}", self.header_rect.right - 110, self.header_rect.y + 28, self.title_font, value_color)

    def draw_status(self, game_state, animation_time=0):
        """
        Draw the footer message and simple animation based on the current result.

        Args:
            game_state (GameState): Current game state used to choose status text.
            animation_time (int): Current tick count used for simple animation effects.

        Returns:
            None
        """
        if game_state.victory:
            text = "You cleared the board"
            color = self.accent_color
        elif game_state.game_over:
            text = "Boom, tap the smile to try again"
            color = self.danger_color
        else:
            text = "Left click to reveal, right click to flag"
            color = self.subtle_text

        self.draw_text(text, self.footer_rect.x + 18, self.footer_rect.y + 18, self.small_font, color)

        if game_state.victory:
            sparkle_x = self.footer_rect.right - 38 + (animation_time // 120 % 6)
            sparkle_y = self.footer_rect.y + 20
            pygame.draw.circle(self.screen, self.accent_color, (sparkle_x, sparkle_y), 4)
            pygame.draw.circle(self.screen, self.accent_color, (sparkle_x + 18, sparkle_y + 10), 3)
        elif game_state.game_over:
            shake = (animation_time // 120) % 2
            dot_x = self.footer_rect.right - 34 + shake * 2
            dot_y = self.footer_rect.y + 26
            pygame.draw.circle(self.screen, self.danger_color, (dot_x, dot_y), 4)
