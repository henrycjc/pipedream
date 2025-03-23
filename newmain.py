import dataclasses
import enum
import queue
from collections import deque
import random
from typing import Final

import pygame as pg
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)



class TileImage(enum.Enum):
    INTERSECTION = "intersection.png"
    HORIZONTAL = "horizontal.png"
    VERTICAL = "vertical.png"
    TOP_LEFT = "topleft.png"
    TOP_RIGHT = "topright.png"
    BOTTOM_LEFT = "bottomleft.png"
    BOTTOM_RIGHT = "bottomright.png"


class constants:
    WIDTH, HEIGHT = 1280, 1000  # Window size
    GRID_COLS, GRID_ROWS = 10, 7
    TILE_SIZE = WIDTH // GRID_COLS  # 128 # Ensuring a perfect fit
    MENU_HEIGHT = TILE_SIZE
    # Colors
    BG_COLOR = (30, 30, 30)  # Dark background
    GRID_COLOR = (200, 200, 200)  # Light gray for tiles
    OUTLINE_COLOR = (100, 100, 100)  # Darker outline


class GameState:
    tile_queue: deque[TileImage]
    _grid: list[list[TileImage | None]]

    def __init__(self):
        self._grid = [[None for _ in range(constants.GRID_COLS)] for _ in range(constants.GRID_ROWS)]
        self.init_queue()
        self.score = 0

    def grid_at(self, pos: tuple[int, int]) -> TileImage | None:
        return self._grid[constants.GRID_ROWS - 1 - pos[1]][pos[0]]

    def set_grid_at(self, pos: tuple[int, int], tile: TileImage) -> None:
        try:
            self._grid[constants.GRID_ROWS - 1 - pos[1]][pos[0]] = tile
        except IndexError as e:
            logger.error(f"Error setting grid at {pos}: {e} where constants.GRID_ROWS = {constants.GRID_ROWS} take away 1, take away {pos[1]} = {constants.GRID_ROWS - 1 - pos[1]}")
            raise

    def init_queue(self):
        self.tile_queue = deque(maxlen=5)
        for i in range(5):
            self.tile_queue.append(random.choice(list(TileImage)))

    def get_tile_deque(self):
        return self.tile_queue

    def pop_deque_and_replenish_tile(self):
        tile = self.tile_queue.popleft()
        self.tile_queue.append(random.choice(list(TileImage)))
        return tile


@dataclasses.dataclass
class Game:
    screen: pg.Surface
    state: GameState

# Function to draw a single tile
def draw_bg_tile(surface: pg.Surface, pos: tuple[int, int], size: int) -> None:
    """
    Draw a single tile on the grid
    """
    radius = 8
    stroke = 2
    x, y = get_x_y_from_grid_pos(pos)
    pg.draw.rect(surface, constants.GRID_COLOR, (x, y, size, size), border_radius=radius)
    pg.draw.rect(surface, constants.OUTLINE_COLOR, (x, y, size, size), width=stroke, border_radius=radius)
    # draw your coordinates on the tile
    font = pg.font.Font(None, 36)
    text = font.render(f"{pos[0]}, {pos[1]}", True, (255, 255, 255))
    surface.blit(text, (x + constants.TILE_SIZE / 2, y + constants.TILE_SIZE / 2))



def get_click_pos_on_grid() -> tuple[int, int]:
    """
    Get the position of the mouse on the grid
    """
    mouse_pos: tuple[int, int] = pg.mouse.get_pos()
    mouse_tile_x, mouse_tile_y = mouse_pos
    (67, 939)
    grid_x = min(max(mouse_tile_x // constants.TILE_SIZE, 0), constants.GRID_COLS - 1)
    grid_y = min(max(constants.GRID_ROWS - (mouse_tile_y // constants.TILE_SIZE), 0), constants.GRID_ROWS - 1)
    logger.info(f"clicked {grid_x} {grid_y} from {mouse_pos}")
    return grid_x, grid_y

def get_x_y_from_grid_pos(pos: tuple[int, int]) -> tuple[int, int]:
    return pos[0] * constants.TILE_SIZE, (constants.GRID_ROWS - 1 - pos[1]) * constants.TILE_SIZE + constants.MENU_HEIGHT

def draw_grid(game: Game) -> None:
    game.screen.fill(constants.BG_COLOR)
    def make_pos_from_grid_x_y(row_: int, col_: int) -> tuple[int, int]:
        return col_, constants.GRID_ROWS - 1 - row_

    for row in range(constants.GRID_ROWS):
        for col in range(constants.GRID_COLS):
            pos = make_pos_from_grid_x_y(row, col)
            if game.state.grid_at(pos) is None:
                 draw_bg_tile(game.screen, pos, constants.TILE_SIZE)
            else:
                img = pg.image.load("assets/" + (game.state.grid_at(pos).value or 'intersection.png')).convert_alpha()
                img = pg.transform.scale(img, (constants.TILE_SIZE, constants.TILE_SIZE))
                game.screen.blit(img, get_x_y_from_grid_pos(pos))

def draw_tile_queue(game: Game) -> None:
    tiles = 5
    for i in range(tiles):
        x = i * constants.TILE_SIZE
        y = 0
        img = pg.image.load("assets/" + game.state.get_tile_deque()[i].value).convert_alpha()
        img = pg.transform.scale(img, (constants.TILE_SIZE - 10, constants.TILE_SIZE - 10))
        game.screen.blit(img, (x, y))

def put_tile_at_pos(game: Game, pos: tuple[int, int]) -> None:
    tile = game.state.pop_deque_and_replenish_tile()
    game.state.set_grid_at(pos, tile)
    img = pg.image.load("assets/" + tile.value).convert_alpha()
    img = pg.transform.scale(img, (constants.TILE_SIZE, constants.TILE_SIZE))
    game.screen.blit(img, get_x_y_from_grid_pos(pos))


def process_left_click(game: Game) -> None:
    # If pos is in the menu, print the menu position, if its on the grid, print the grid position
    x, y = get_click_pos_on_grid()
    put_tile_at_pos(game, (x, y))


def main():
    pg.init()
    screen: pg.Surface = pg.display.set_mode((constants.WIDTH, constants.HEIGHT))
    pg.display.set_caption("Pipe Dream")
    clock: pg.time.Clock = pg.time.Clock()
    # Main loop
    running = True
    state = GameState()

    game = Game(screen, state)
    while running:
        draw_grid(game)
        draw_tile_queue(game)

        event: pg.event.Event
        for event in pg.event.get():
            # logger.info(f"Detected {event} at {get_click_pos_on_grid()}")

            match event.type:
                case pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        process_left_click(game)
                case pg.MOUSEBUTTONUP:
                    pass
                case pg.QUIT:
                    running = False
            if event.type == pg.QUIT:
                running = False

        pg.display.flip()
        clock.tick(60)

    pg.quit()

if __name__ == '__main__':
    main()