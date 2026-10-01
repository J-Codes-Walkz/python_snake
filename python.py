"""
Snake
A polished, smooth-running Snake game built with Python's tkinter.

Controls
    Arrow keys / WASD   move
    Space               start / restart
    P                   pause / resume
    Esc                 quit
"""

import json
import os
import random
import tkinter as tk
from typing import Dict, List, Optional, Tuple

#config
CELL_SIZE = 22
GRID_COLS = 24
GRID_ROWS = 24
CANVAS_WIDTH = CELL_SIZE * GRID_COLS
CANVAS_HEIGHT = CELL_SIZE * GRID_ROWS

INITIAL_LENGTH = 3
INITIAL_DELAY_MS = 130
MIN_DELAY_MS = 65
SPEED_UP_EVERY_N_POINTS = 3
SPEED_UP_STEP_MS = 4

HIGH_SCORE_FILE = os.path.join(os.path.expanduser("~"), ".snake_game_highscore.json")

# -- Palette
COLOR_WINDOW_BG = "#0d1117"
COLOR_BORDER = "#30363d"
COLOR_GRID_LINE = "#161b22"
COLOR_CANVAS_BG = "#0d1117"
COLOR_SNAKE_HEAD = "#56f29a"
COLOR_SNAKE_TAIL = "#13522b"
COLOR_SNAKE_EYE = "#0d1117"
COLOR_FOOD_OUTER = "#ff6b6b"
COLOR_FOOD_INNER = "#ffb3b3"
COLOR_TEXT_MAIN = "#e6edf3"
COLOR_TEXT_SUB = "#8b949e"
COLOR_ACCENT = "#58a6ff"
COLOR_DANGER = "#f85149"
COLOR_OVERLAY_BG = "#161b22"

FONT_TITLE = ("Segoe UI", 22, "bold")
FONT_SCORE = ("Segoe UI", 16, "bold")
FONT_BODY = ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 9)

DIRECTIONS: Dict[str, Tuple[int, int]] = {
    "Up": (0, -1),
    "Down": (0, 1),
    "Left": (-1, 0),
    "Right": (1, 0),
}
OPPOSITE: Dict[str, str] = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
KEY_TO_DIRECTION: Dict[str, str] = {
    "Up": "Up", "Down": "Down", "Left": "Left", "Right": "Right",
    "w": "Up", "a": "Left", "s": "Down", "d": "Right",
    "W": "Up", "A": "Left", "S": "Down", "D": "Right",
}
EYE_OFFSETS: Dict[str, Tuple[Tuple[float, float], Tuple[float, float]]] = {
    "Right": ((0.68, 0.30), (0.68, 0.70)),
    "Left": ((0.32, 0.30), (0.32, 0.70)),
    "Up": ((0.30, 0.32), (0.70, 0.32)),
    "Down": ((0.30, 0.68), (0.70, 0.68)),
}


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _lerp_color(color_a: str, color_b: str, t: float) -> str:
    """Linearly interpolate between two '#rrggbb' colors."""
    t = _clamp(t, 0.0, 1.0)
    a = tuple(int(color_a[i:i + 2], 16) for i in (1, 3, 5))
    b = tuple(int(color_b[i:i + 2], 16) for i in (1, 3, 5))
    mixed = tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))
    return "#%02x%02x%02x" % mixed


#game
class SnakeGame:
    """Encapsulates all state and widgets for the Snake game."""

    STATE_INTRO = "intro"
    STATE_RUNNING = "running"
    STATE_PAUSED = "paused"
    STATE_OVER = "game_over"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.high_score = self._load_high_score()

        self.state = self.STATE_INTRO
        self.direction = "Right"
        self.next_direction = "Right"
        self.score = 0
        self.delay_ms = INITIAL_DELAY_MS
        self.after_id: Optional[str] = None

        self.snake: List[Tuple[int, int]] = []
        self.body_items: List[int] = []
        self.eye_items: List[int] = []
        self.food: Optional[Tuple[int, int]] = None
        self.food_items: List[int] = []
        self._pulse_step = 0

        self._build_window()
        self._build_widgets()
        self._draw_grid()
        self._show_overlay(
            "SNAKE",
            "Press SPACE to start\nArrows / WASD to move  \u2022  P to pause  \u2022  Esc to quit",
            COLOR_ACCENT,
        )

        self.root.bind("<KeyPress>", self._on_key_press)

   #window set up 
    def _build_window(self) -> None:
        self.root.title("Snake")
        self.root.configure(bg=COLOR_WINDOW_BG)
        self.root.resizable(False, False)

    def _build_widgets(self) -> None:
        outer = tk.Frame(self.root, bg=COLOR_WINDOW_BG, padx=16, pady=14)
        outer.pack()

        header = tk.Frame(outer, bg=COLOR_WINDOW_BG)
        header.pack(fill="x", pady=(0, 10))

        tk.Label(
            header, text="Snake", font=FONT_TITLE, bg=COLOR_WINDOW_BG, fg=COLOR_TEXT_MAIN,
        ).pack(side="left")

        score_panel = tk.Frame(header, bg=COLOR_WINDOW_BG)
        score_panel.pack(side="right")

        self.score_var = tk.StringVar(value="Score: 0")
        self.best_var = tk.StringVar(value=f"Best: {self.high_score}")

        tk.Label(
            score_panel, textvariable=self.score_var, font=FONT_SCORE,
            bg=COLOR_WINDOW_BG, fg=COLOR_TEXT_MAIN,
        ).pack(anchor="e")
        tk.Label(
            score_panel, textvariable=self.best_var, font=FONT_BODY,
            bg=COLOR_WINDOW_BG, fg=COLOR_TEXT_SUB,
        ).pack(anchor="e")

        board_frame = tk.Frame(outer, bg=COLOR_BORDER, padx=2, pady=2)
        board_frame.pack()

        self.canvas = tk.Canvas(
            board_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT,
            bg=COLOR_CANVAS_BG, highlightthickness=0,
        )
        self.canvas.pack()

        footer = tk.Frame(outer, bg=COLOR_WINDOW_BG)
        footer.pack(fill="x", pady=(10, 0))

        tk.Label(
            footer,
            text="Arrow keys / WASD to move   \u2022   P to pause   \u2022   Esc to quit",
            font=FONT_SMALL, bg=COLOR_WINDOW_BG, fg=COLOR_TEXT_SUB,
        ).pack(side="left")

        self.state_var = tk.StringVar(value="Ready")
        tk.Label(
            footer, textvariable=self.state_var, font=FONT_SMALL,
            bg=COLOR_WINDOW_BG, fg=COLOR_ACCENT,
        ).pack(side="right")

        self.root.update_idletasks()
        self._center_window()

    def _center_window(self) -> None:
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _draw_grid(self) -> None:
        for col in range(1, GRID_COLS):
            x = col * CELL_SIZE
            self.canvas.create_line(x, 0, x, CANVAS_HEIGHT, fill=COLOR_GRID_LINE, tags="grid")
        for row in range(1, GRID_ROWS):
            y = row * CELL_SIZE
            self.canvas.create_line(0, y, CANVAS_WIDTH, y, fill=COLOR_GRID_LINE, tags="grid")

    #score
    @staticmethod
    def _load_high_score() -> int:
        try:
            with open(HIGH_SCORE_FILE, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                return int(data.get("high_score", 0))
        except (OSError, ValueError, json.JSONDecodeError):
            return 0

    @staticmethod
    def _save_high_score(value: int) -> None:
        try:
            with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as fh:
                json.dump({"high_score": value}, fh)
        except OSError:
            pass

   #game lifecycle 
    def _start_new_game(self) -> None:
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.canvas.delete("snake")
        self.canvas.delete("food")
        self._hide_overlay()

        center_col, center_row = GRID_COLS // 2, GRID_ROWS // 2
        self.snake = [(center_col - i, center_row) for i in range(INITIAL_LENGTH)]
        self.body_items = []
        self.eye_items = []
        self.direction = "Right"
        self.next_direction = "Right"
        self.score = 0
        self.delay_ms = INITIAL_DELAY_MS
        self.state = self.STATE_RUNNING
        self._pulse_step = 0

        self.score_var.set("Score: 0")
        self.state_var.set("Running")

        self.food = self._spawn_food()
        self._render_snake()
        self._tick()

    def _pause(self) -> None:
        if self.state != self.STATE_RUNNING:
            return
        self.state = self.STATE_PAUSED
        self.state_var.set("Paused")
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self._show_overlay("PAUSED", "Press P to resume", COLOR_ACCENT)

    def _resume(self) -> None:
        if self.state != self.STATE_PAUSED:
            return
        self.state = self.STATE_RUNNING
        self.state_var.set("Running")
        self._hide_overlay()
        self._tick()

    def _end_game(self, won: bool = False) -> None:
        self.state = self.STATE_OVER
        self.state_var.set("Game over")
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score(self.high_score)
            self.best_var.set(f"Best: {self.high_score}")

        title = "YOU WIN!" if won else "GAME OVER"
        subtitle = f"Score: {self.score}   \u2022   Best: {self.high_score}\nPress SPACE to play again"
        self._show_overlay(title, subtitle, COLOR_ACCENT if won else COLOR_DANGER)

    #main game loop
    def _tick(self) -> None:
        if self.state != self.STATE_RUNNING:
            return

        self.direction = self.next_direction
        dx, dy = DIRECTIONS[self.direction]
        head_col, head_row = self.snake[0]
        new_head = (head_col + dx, head_row + dy)

        if self._hits_wall(new_head) or self._hits_self(new_head):
            self._end_game()
            return

        growing = self.food is not None and new_head == self.food
        self.snake.insert(0, new_head)
        if growing:
            self.score += 1
            self.score_var.set(f"Score: {self.score}")
            if self.score % SPEED_UP_EVERY_N_POINTS == 0:
                self.delay_ms = max(MIN_DELAY_MS, self.delay_ms - SPEED_UP_STEP_MS)
            self.food = self._spawn_food()
        else:
            self.snake.pop()

        self._render_snake()

        if growing and self.food is None:
            self._end_game(won=True)
            return

        self._animate_food()
        self.after_id = self.root.after(self.delay_ms, self._tick)

    def _hits_wall(self, cell: Tuple[int, int]) -> bool:
        col, row = cell
        return col < 0 or col >= GRID_COLS or row < 0 or row >= GRID_ROWS

    def _hits_self(self, new_head: Tuple[int, int]) -> bool:
        # If this move eats the food, the tail won't move away this turn,
        # so it still counts as occupied.
        body_to_check = self.snake if new_head == self.food else self.snake[:-1]
        return new_head in body_to_check

   
    def _cell_bounds(self, cell: Tuple[int, int], pad: float = 2.0) -> Tuple[float, float, float, float]:
        col, row = cell
        x1 = col * CELL_SIZE + pad
        y1 = row * CELL_SIZE + pad
        x2 = x1 + CELL_SIZE - 2 * pad
        y2 = y1 + CELL_SIZE - 2 * pad
        return x1, y1, x2, y2

    def _render_snake(self) -> None:
        count = len(self.snake)

        while len(self.body_items) < count:
            item = self.canvas.create_oval(0, 0, 0, 0, outline="", tags="snake")
            self.body_items.append(item)
        while len(self.body_items) > count:
            self.canvas.delete(self.body_items.pop())

        for index, cell in enumerate(self.snake):
            x1, y1, x2, y2 = self._cell_bounds(cell, pad=1.5)
            item = self.body_items[index]
            self.canvas.coords(item, x1, y1, x2, y2)
            t = index / max(1, count - 1)
            color = COLOR_SNAKE_HEAD if index == 0 else _lerp_color(COLOR_SNAKE_HEAD, COLOR_SNAKE_TAIL, t)
            self.canvas.itemconfig(item, fill=color)

        self._render_eyes()

    def _render_eyes(self) -> None:
        while len(self.eye_items) < 2:
            self.eye_items.append(
                self.canvas.create_oval(0, 0, 0, 0, fill=COLOR_SNAKE_EYE, outline="", tags="snake")
            )

        x1, y1, x2, y2 = self._cell_bounds(self.snake[0], pad=1.5)
        width, height = x2 - x1, y2 - y1
        for item, (fx, fy) in zip(self.eye_items, EYE_OFFSETS[self.direction]):
            ex, ey = x1 + width * fx, y1 + height * fy
            r = 1.6
            self.canvas.coords(item, ex - r, ey - r, ex + r, ey + r)

    def _spawn_food(self) -> Optional[Tuple[int, int]]:
        occupied = set(self.snake)
        free_cells = [
            (c, r) for c in range(GRID_COLS) for r in range(GRID_ROWS) if (c, r) not in occupied
        ]
        self.canvas.delete("food")
        if not free_cells:
            self.food_items = []
            return None

        cell = random.choice(free_cells)
        x1, y1, x2, y2 = self._cell_bounds(cell, pad=3)
        outer = self.canvas.create_oval(x1, y1, x2, y2, fill=COLOR_FOOD_OUTER, outline="", tags="food")
        ix1, iy1, ix2, iy2 = self._cell_bounds(cell, pad=6)
        inner = self.canvas.create_oval(ix1, iy1, ix2, iy2, fill=COLOR_FOOD_INNER, outline="", tags="food")
        self.food_items = [outer, inner]
        return cell

    def _animate_food(self) -> None:
        if not self.food or not self.food_items:
            return
        self._pulse_step = (self._pulse_step + 1) % 20
        pulse = abs(10 - self._pulse_step) / 10.0  # triangle wave 0 -> 1 -> 0
        pad = 3 - pulse * 1.5
        x1, y1, x2, y2 = self._cell_bounds(self.food, pad=pad)
        self.canvas.coords(self.food_items[0], x1, y1, x2, y2)

   
    def _show_overlay(self, title: str, subtitle: str, accent: str) -> None:
        self.canvas.delete("overlay")
        cx, cy = CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2
        box_w, box_h = CANVAS_WIDTH * 0.8, 150
        self.canvas.create_rectangle(
            cx - box_w / 2, cy - box_h / 2, cx + box_w / 2, cy + box_h / 2,
            fill=COLOR_OVERLAY_BG, outline=accent, width=2, tags="overlay",
        )
        self.canvas.create_text(cx, cy - 24, text=title, fill=accent, font=FONT_TITLE, tags="overlay")
        self.canvas.create_text(
            cx, cy + 20, text=subtitle, fill=COLOR_TEXT_SUB, font=FONT_BODY,
            justify="center", tags="overlay",
        )

    def _hide_overlay(self) -> None:
        self.canvas.delete("overlay")


    def _on_key_press(self, event: "tk.Event") -> None:
        key = event.keysym

        if key == "Escape":
            self.root.destroy()
            return

        if key == "space":
            if self.state in (self.STATE_INTRO, self.STATE_OVER):
                self._start_new_game()
            return

        if key in ("p", "P"):
            if self.state == self.STATE_RUNNING:
                self._pause()
            elif self.state == self.STATE_PAUSED:
                self._resume()
            return

        if self.state == self.STATE_RUNNING and key in KEY_TO_DIRECTION:
            new_direction = KEY_TO_DIRECTION[key]
            if new_direction != OPPOSITE[self.direction]:
                self.next_direction = new_direction


def main() -> None:
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()