import dataclasses
import enum
import logging
import random
from collections import deque

from wallace import constants
from wallace.assets import TileImage
from wallace.assets import Direction
import pygame as pg


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


class FluidState:
    pos: pg.math.Vector2
    time: float
    path: list[pg.math.Vector2]

    def __init__(self, start_pos: pg.Vector2, start_direction: Direction):
        self.start_pos = start_pos
        logger.info(f"FluidState init at {start_pos} with {start_direction}")
        self.start_direction = start_direction
        self.path = [start_pos]
        self.last_move_time = 0  # Track the last move time

    def get_pos(self) -> pg.Vector2:
        return self.path[-1]

    def update(self, gamestate: "GameState") -> None:
        current_time = gamestate.get_time()
        if current_time - self.last_move_time >= 2:  # Move every 2 seconds
            direction_vectors: dict[Direction, pg.Vector2] = {
                Direction.TOP: pg.math.Vector2(0, 1),
                Direction.LEFT: pg.math.Vector2(-1, 0),
                Direction.BOTTOM: pg.math.Vector2(0, -1),
                Direction.RIGHT: pg.math.Vector2(1, 0),
            }
            last_pos = self.path[-1]
            next_pos = last_pos + direction_vectors[self.start_direction]
            # Check if the next position is valid
            if next_pos.x < 0 or next_pos.x >= constants.GRID_COLS or next_pos.y < 0 or next_pos.y >= constants.GRID_ROWS:
                logger.info(f"Fluid hit the wall at {next_pos}")
                return
            self.path.append(next_pos)
            self.last_move_time = current_time
            logger.info(f"Fluid moved to {next_pos}")