import dataclasses
import enum
import itertools
import logging
import random
from collections import deque
from typing import Iterable

from wallace import constants
from wallace.assets import TileImage
from wallace.assets import Direction
import pygame as pg


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)



def get_next_direction(coming_from_direction: Direction, tile: TileImage) -> Direction:
    """
    Get the next fluid direction from the in movement into the tile.
    :param coming_from_direction: the fluid flow direction (i.e. left meanings it is coming from the left)
    :param tile:
    :return: fluid's direction
    """
    if tile in (TileImage.HORIZONTAL, TileImage.VERTICAL, TileImage.INTERSECTION):
        return coming_from_direction
    elif tile == TileImage.TOP_LEFT:
        if coming_from_direction not in (Direction.TOP, Direction.LEFT):
            raise ValueError(f"Invalid direction {coming_from_direction} for tile {tile}")
        return Direction.TOP if coming_from_direction == Direction.LEFT else Direction.LEFT
    elif tile == TileImage.TOP_RIGHT:
        if coming_from_direction not in (Direction.TOP, Direction.RIGHT):
            raise ValueError(f"Invalid direction {coming_from_direction} for tile {tile}")
        return Direction.TOP if coming_from_direction == Direction.RIGHT else Direction.RIGHT
    elif tile == TileImage.BOTTOM_LEFT:
        if coming_from_direction not in (Direction.BOTTOM, Direction.LEFT):
            raise ValueError(f"Invalid direction {coming_from_direction} for tile {tile}")
        return Direction.BOTTOM if coming_from_direction == Direction.LEFT else Direction.LEFT
    elif tile == TileImage.BOTTOM_RIGHT:
        if coming_from_direction not in (Direction.BOTTOM, Direction.RIGHT):
            raise ValueError(f"Invalid direction {coming_from_direction} for tile {tile}")
        return Direction.BOTTOM if coming_from_direction == Direction.RIGHT else Direction.RIGHT
    raise ValueError(f"Invalid tile {tile}")


class FluidState:
    last_move_time: float
    """Time since the fluid last moved"""

    path: list[pg.math.Vector3]
    """List of positions the fluid has moved through with the z coordinate (0 to 1) representing how full it is"""

    def __init__(self, start_pos: pg.Vector2, start_direction: Direction):
        self.start_pos = start_pos
        logger.info(f"FluidState init at {start_pos} with {start_direction}")
        self.start_direction = start_direction
        self.path = [pg.Vector3(*start_pos, 0.0)]  # Start with the initial position and a z coordinate of 0
        self.last_move_time = 0.0  # Track the last move time

    def get_path(self) -> Iterable[tuple[pg.math.Vector3, pg.math.Vector3]]:
        # Return the path as a list of tuples of positions
        return itertools.pairwise(self.path)

    def get_pos(self) -> pg.Vector2:
        x, y, z = self.path[-1]
        return pg.Vector2(x, y)

    def update(self, gamestate: "GameState") -> None:
        """
        Need to move the fluid around like water moving through a pipe.
        Each TileImage represents a pipe that takes water from one {Direction} and sends it in another {Direction}
        The fluid will move in the direction of the last tile placed.
        For example, for our 3x3 grid starting at 0,0 with a UP tile placed at 1,0 and and a LEFT tile placed at 1,1
            +---+---+---+
            |   |<- |   |
            +---+---+---+
            | ->| ^ |   |
            +---+---+---+
        The fluid will flow 0,0 -> 1,0 -> 1,1 -> 2,1 (BUST! No tile).
        In the case of 4 way intersections, the fluid will continue straight and not spill out the sides.
        """
        """
        Update the fluid's position based on its current direction and the game state.
        """
        current_time = gamestate.get_time()
        STEP = 1
        time_since = (current_time - self.last_move_time)
        if time_since >= STEP:  # Move every 2 seconds
            direction_vectors: dict[tuple[int, int], Direction] = {
                (0, 1): Direction.TOP,
                (-1, 0): Direction.LEFT,
                (0, -1): Direction.BOTTOM,
                (1, 0): Direction.RIGHT,
            }

            # Determine the incumbent direction
            if len(self.path) > 1:
                last_pos = self.path[-1]
                prev_pos = self.path[-2]
                direction_vector = (int(last_pos.x - prev_pos.x), int(last_pos.y - prev_pos.y))

                logger.info(f"Dir vec {direction_vector}")
                incumbent_direction = direction_vectors.get(direction_vector, self.start_direction)
                logger.info(f"Incumbent {incumbent_direction}")
            else:
                incumbent_direction = self.start_direction

            # Calculate the next position
            direction_offsets: dict[Direction, pg.Vector3] = {
                Direction.TOP: pg.math.Vector3(0, 1, 0),
                Direction.LEFT: pg.math.Vector3(-1, 0, 0),
                Direction.BOTTOM: pg.math.Vector3(0, -1, 0),
                Direction.RIGHT: pg.math.Vector3(1, 0, 0),
            }
            last_pos = self.path[-1]
            next_pos = last_pos + direction_offsets[incumbent_direction]

            # Check if the next position is valid
            if next_pos.x < 0 or next_pos.x >= constants.GRID_COLS or next_pos.y < 0 or next_pos.y >= constants.GRID_ROWS:
                logger.info(f"Fluid hit the wall at {next_pos}")
                return

            self.path.append(next_pos)
            self.last_move_time = current_time
            logger.info(f"Fluid moved to {next_pos}")
        else:
            # Set the z coordinate to 0 to 1 based on time to the next move
            x, y, z = self.path[-1]
            # logger.info(f"Updated fluid strength to {time_since / STEP}")
            self.path[-1] = pg.Vector3(x, y, (time_since / STEP))