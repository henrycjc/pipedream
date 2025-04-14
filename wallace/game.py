import dataclasses
import logging
import random
from collections import deque

import pygame as pg

from wallace import constants
from wallace.assets import TileImage, Direction
from wallace.fluid import FluidState

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


class GameState:
    tile_queue: deque[TileImage]
    _grid: list[list[TileImage | None]]
    clock_ticking: bool
    score: int
    fluid_state: FluidState

    def __init__(self):
        self.running = True
        self.start_tick = None
        self.last_update_time = 0  # Add this line
        self.tile_queue = deque(maxlen=5)
        for i in range(5):
            self.tile_queue.append(random.choice(TileImage.get_user_placeable_pieces()))
        self._grid = [[None for _ in range(constants.GRID_COLS)] for _ in range(constants.GRID_ROWS)]

        grid_x = int(random.randint(2, constants.GRID_COLS - 2))
        grid_y = int(random.randint(2, constants.GRID_ROWS - 2))
        direction = random.choice(list(Direction))
        temp_hack = True
        if temp_hack:
            grid_x = 3
            grid_y = 3
            direction = Direction.RIGHT
            self.tile_queue = deque([TileImage.TOP_LEFT, TileImage.VERTICAL, TileImage.BOTTOM_RIGHT, TileImage.HORIZONTAL, TileImage.VERTICAL], maxlen=5)

        self.set_grid_at((grid_x, grid_y), direction.as_tile_image())
        logger.info(f"Starting tile at {(grid_x, grid_y)} to {direction.as_tile_image()}")
        self.fluid_state = FluidState(
            pg.math.Vector2(grid_x, grid_y),
            direction
        )
        self.score = 0
        self.clock_ticking = False

    def get_time(self) -> float:
        if self.clock_ticking and self.start_tick is None:
            self.start_tick = pg.time.get_ticks()
        if not self.clock_ticking:
            raise ValueError("Clock not ticking")  # just to manage only one guy starts the clock.
        return (pg.time.get_ticks() - self.start_tick) / 1000

    def pieces_placed(self) -> list[TileImage]:
        return [tile for row in self._grid for tile in row if tile is not None]

    def grid_at(self, grid_xy: tuple[int, int]) -> TileImage | None:
        x = int(grid_xy[0])
        y = int(grid_xy[1])
        try:
            return self._grid[constants.GRID_ROWS - 1 - y][x]
        except IndexError as e:
            logger.error(f"Error getting grid at {grid_xy}: {e}")
            raise

    def set_grid_at(self, grid_xy: tuple[int, int], tile: TileImage) -> None:
        logger.info(f"set_grid_at {grid_xy} to {tile}")
        try:
            self._grid[constants.GRID_ROWS - 1 - grid_xy[1]][grid_xy[0]] = tile
        except IndexError as e:
            logger.error(f"Error setting grid at {grid_xy}: {e}")
            raise

    def view_tile_queue(self) -> deque[TileImage]:
        return self.tile_queue

    def pop_deque_and_replenish_tile(self) -> TileImage:
        tile = self.tile_queue.popleft()
        self.tile_queue.append(random.choice(TileImage.get_user_placeable_pieces()))
        assert tile
        return tile

    def process_time(self):
        if self.clock_ticking:
            current_time = self.get_time()
            self.fluid_state.update(self)
            self.last_update_time = current_time


@dataclasses.dataclass
class Game:
    screen: pg.Surface
    state: GameState

