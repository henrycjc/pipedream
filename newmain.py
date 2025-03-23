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

    START_TOP = "start_top.png"
    START_RIGHT = "start_right.png"
    START_BOTTOM = "start_bottom.png"
    START_LEFT = "start_left.png"

    @staticmethod
    def get_start_tiles() -> list["TileImage"]:
        return [
            TileImage.START_TOP,
            TileImage.START_RIGHT,
            TileImage.START_BOTTOM,
            TileImage.START_LEFT,
        ]

    @staticmethod
    def get_user_placeable_pieces() -> list["TileImage"]:
        return [
            TileImage.INTERSECTION,
            TileImage.HORIZONTAL,
            TileImage.VERTICAL,
            TileImage.TOP_LEFT,
            TileImage.TOP_RIGHT,
            TileImage.BOTTOM_LEFT,
            TileImage.BOTTOM_RIGHT
        ]


class Direction(enum.Enum):
    TOP = "top"
    LEFT = 1
    BOTTOM = 2
    RIGHT = 3

    def as_tile_image(self) -> TileImage:
        return {
            Direction.TOP: TileImage.VERTICAL,
            Direction.LEFT: TileImage.HORIZONTAL,
            Direction.BOTTOM: TileImage.VERTICAL,
            Direction.RIGHT: TileImage.HORIZONTAL,
        }[self]

class constants:
    WIDTH, HEIGHT = 1280, 1000  # Window size
    GRID_COLS, GRID_ROWS = 10, 7
    TILE_SIZE = WIDTH // GRID_COLS  # 128 # Ensuring a perfect fit
    MENU_HEIGHT = TILE_SIZE
    # Colors
    BG_COLOR = (30, 30, 30)  # Dark background
    GRID_COLOR = (200, 200, 200)  # Light gray for tiles
    OUTLINE_COLOR = (100, 100, 100)  # Darker outline

    TILE_QUEUE_SIZE = 5

@dataclasses.dataclass
class FluidPosition:
    x: int
    y: int
    z: Direction

class GameState:
    tile_queue: deque[TileImage]
    _grid: list[list[TileImage | None]]
    clock_ticking: bool
    score: int
    starting_fluid_position: Final[FluidPosition]
    current_whole_second: int

    def __init__(self):
        self.running = True
        self.start_tick = None
        self.tile_queue = deque(maxlen=5)
        for i in range(5):
            self.tile_queue.append(random.choice(TileImage.get_user_placeable_pieces()))

        self._grid = [[None for _ in range(constants.GRID_COLS)] for _ in range(constants.GRID_ROWS)]
        x = int(random.randint(2, constants.GRID_COLS - 2))
        y = int(random.randint(2, constants.GRID_ROWS - 2))
        direction: Direction = random.choice(list(Direction))
        self.set_grid_at((x, y), random.choice(TileImage.get_start_tiles()))
        self._fluid_position = FluidPosition(x, y, direction)
        self.starting_fluid_position = FluidPosition(x, y, direction)
        self.score = 0
        self.clock_ticking = False
        self.current_whole_second = 0

    def get_time(self) -> float:
        if self.clock_ticking and self.start_tick is None:
            self.start_tick = pg.time.get_ticks()
        if not self.clock_ticking:
            raise ValueError("Clock not ticking")
        return (pg.time.get_ticks() - self.start_tick) / 1000

    def pieces_placed(self) -> list[TileImage]:
        return [tile for row in self._grid for tile in row if tile is not None]

    def grid_at(self, pos: tuple[int, int]) -> TileImage | None:
        return self._grid[constants.GRID_ROWS - 1 - pos[1]][pos[0]]

    def set_grid_at(self, pos: tuple[int, int], tile: TileImage) -> None:
        try:
            self._grid[constants.GRID_ROWS - 1 - pos[1]][pos[0]] = tile
        except IndexError as e:
            logger.error(f"Error setting grid at {pos}: {e}")
            raise

    def view_tile_queue(self):
        return self.tile_queue

    def pop_deque_and_replenish_tile(self):
        tile = self.tile_queue.popleft()
        self.tile_queue.append(random.choice(TileImage.get_user_placeable_pieces()))
        return tile

    def _get_next_fluid_position(self) -> FluidPosition:
        if self.fluid_position is self.starting_fluid_position:
            # Safe to just move, because we always spawn away from the edges.
            match self.fluid_position.z:
                case Direction.TOP:
                    return FluidPosition(self.fluid_position.x, self.fluid_position.y - 1, Direction.TOP)
                case Direction.LEFT:
                    return FluidPosition(self.fluid_position.x - 1, self.fluid_position.y, Direction.LEFT)
                case Direction.BOTTOM:
                    return FluidPosition(self.fluid_position.x, self.fluid_position.y + 1, Direction.BOTTOM)
                case Direction.RIGHT:
                    return FluidPosition(self.fluid_position.x + 1, self.fluid_position.y, Direction.RIGHT)
                case _:
                    raise ValueError("Invalid direction")
        else:
            # TODO: Implement fluid flow - eventually trains moving.
            return FluidPosition(self.fluid_position.x + 1, self.fluid_position.y, self.fluid_position.z)

    def _move_fluid(self):
        self.fluid_position = self._get_next_fluid_position()

    def process_time(self):
        if self.clock_ticking:
            # try to print once a second
            self.current_whole_second = round(self.get_time())
            if self.current_whole_second > self.get_time():
                logger.info(f"Time: {self.current_whole_second}")
            if self.current_whole_second > 10:
                self._move_fluid()


@dataclasses.dataclass
class Game:
    screen: pg.Surface
    state: GameState


def draw_image(game: Game, pos: tuple[int, int], tile: TileImage) -> None:
    img = pg.image.load("assets/" + tile.value).convert_alpha()
    img = pg.transform.scale(img, (constants.TILE_SIZE, constants.TILE_SIZE))
    game.screen.blit(img, get_x_y_from_grid_pos(pos))


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
                draw_image(game, pos, game.state.grid_at(pos))

def draw_tile_queue(game: Game) -> None:
    for i in range(constants.TILE_QUEUE_SIZE):
        img = pg.image.load("assets/" + game.state.view_tile_queue()[i].value).convert_alpha()
        img = pg.transform.scale(img, (constants.TILE_SIZE - 10, constants.TILE_SIZE - 10))
        game.screen.blit(img, (i * constants.TILE_SIZE, 0))

def put_tile_at_pos(game: Game, pos: tuple[int, int]) -> None:
    if game.state.grid_at(pos) is None:
        tile = game.state.pop_deque_and_replenish_tile()
        game.state.set_grid_at(pos, tile)
        draw_image(game, pos, game.state.grid_at(pos))
    else:
        logger.error("TODO: handle putting tile on top of another tile")


def main():
    pg.init()
    screen: pg.Surface = pg.display.set_mode((constants.WIDTH, constants.HEIGHT))
    pg.display.set_caption("Pipe Dream")
    clock: pg.time.Clock = pg.time.Clock()
    state = GameState()
    game = Game(screen, state)

    while game.state.running:
        draw_grid(game)
        draw_tile_queue(game)

        game.state.process_time()
        event: pg.event.Event
        for event in pg.event.get():
            match event.type:
                case pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        put_tile_at_pos(game, get_click_pos_on_grid())
                case pg.MOUSEBUTTONUP:
                    # Once they place their first tile, the clock starts.
                    game.state.clock_ticking = True
                case pg.QUIT:
                    game.state.running = False

        pg.display.flip()
        clock.tick(60)

    pg.quit()

if __name__ == '__main__':
    main()