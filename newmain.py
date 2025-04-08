import dataclasses
import enum
import logging
import random
from collections import deque

import pygame as pg


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
    TOP = 0
    LEFT = 1
    BOTTOM = 2
    RIGHT = 3

    def as_tile_image(self) -> TileImage:
        return {
            Direction.TOP: TileImage.START_TOP,
            Direction.LEFT: TileImage.START_LEFT,
            Direction.BOTTOM: TileImage.START_BOTTOM,
            Direction.RIGHT: TileImage.START_RIGHT,
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
    GREEN = (0, 255, 0)
    TILE_QUEUE_SIZE = 5


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
        if current_time - self.last_move_time >= 3:  # Move every 3 seconds
            direction_vectors: dict[Direction, pg.Vector2] = {
                Direction.TOP: pg.math.Vector2(0, -1),
                Direction.LEFT: pg.math.Vector2(-1, 0),
                Direction.BOTTOM: pg.math.Vector2(0, 1),
                Direction.RIGHT: pg.math.Vector2(1, 0),
            }
            last_pos = self.path[-1]
            next_pos = last_pos + direction_vectors[self.start_direction]
            self.path.append(next_pos)
            self.last_move_time = current_time
            logger.info(f"Fluid moved to {next_pos}")


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

    def view_tile_queue(self):
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


def draw_image(game: Game, grid_xy: tuple[int, int], tile: TileImage) -> None:
    assert tile, f"Tile is None at {grid_xy}"
    img = pg.image.load("assets/" + tile.value).convert_alpha()
    img = pg.transform.scale(img, (constants.TILE_SIZE, constants.TILE_SIZE))
    game.screen.blit(img, get_draw_coords_from_grid_xy(grid_xy))

def draw_bg_tile(surface: pg.Surface, grid_xy: tuple[int, int], size: int) -> None:
    """
    Draw a single tile on the grid
    """
    radius = 8
    stroke = 2
    x, y = get_draw_coords_from_grid_xy(grid_xy)
    pg.draw.rect(surface, constants.GRID_COLOR, (x, y, size, size), border_radius=radius)
    pg.draw.rect(surface, constants.OUTLINE_COLOR, (x, y, size, size), width=stroke, border_radius=radius)
    # draw your coordinates on the tile
    font = pg.font.Font(None, 36)
    text = font.render(f"{grid_xy[0]}, {grid_xy[1]}", True, (255, 255, 255))
    surface.blit(text, (x + constants.TILE_SIZE / 2, y + constants.TILE_SIZE / 2))

def get_grid_xy_click_pos() -> tuple[int, int]:
    """
    Get the position of the mouse on the grid
    """
    mouse_pos: tuple[int, int] = pg.mouse.get_pos()
    mouse_tile_x, mouse_tile_y = mouse_pos
    grid_x = min(max(mouse_tile_x // constants.TILE_SIZE, 0), constants.GRID_COLS - 1)
    grid_y = min(max(constants.GRID_ROWS - (mouse_tile_y // constants.TILE_SIZE), 0), constants.GRID_ROWS - 1)
    draw_coords = get_draw_coords_from_grid_xy((grid_x, grid_y))
    logger.info(f"clicked {grid_x} {grid_y} from {mouse_pos} with draw coords {draw_coords}")
    return grid_x, grid_y

def get_draw_coords_from_grid_xy(grid_xy: tuple[int, int]) -> tuple[int, int]:
    return grid_xy[0] * constants.TILE_SIZE, (constants.GRID_ROWS - 1 - grid_xy[1]) * constants.TILE_SIZE + constants.MENU_HEIGHT

def draw_grid(game: Game) -> None:
    game.screen.fill(constants.BG_COLOR)

    def get_grid_xy_from_row_col(row_: int, col_: int) -> tuple[int, int]:
        return col_, constants.GRID_ROWS - 1 - row_

    for row in range(constants.GRID_ROWS):
        for col in range(constants.GRID_COLS):
            grid_xy = get_grid_xy_from_row_col(row, col)
            if game.state.grid_at(grid_xy) is None:
                 draw_bg_tile(game.screen, grid_xy, constants.TILE_SIZE)
            else:
                draw_image(game, grid_xy, game.state.grid_at(grid_xy))

def draw_tile_queue(game: Game) -> None:
    for i in range(constants.TILE_QUEUE_SIZE):
        img = pg.image.load("assets/" + game.state.view_tile_queue()[i].value).convert_alpha()
        img = pg.transform.scale(img, (constants.TILE_SIZE - 10, constants.TILE_SIZE - 10))
        game.screen.blit(img, (i * constants.TILE_SIZE, 0))

def put_tile_at_pos(game: Game, grid_xy: tuple[int, int]) -> None:
    if game.state.grid_at(grid_xy) is None:
        tile = game.state.pop_deque_and_replenish_tile()
        game.state.set_grid_at(grid_xy, tile)
        draw_image(game, grid_xy, game.state.grid_at(grid_xy))
    else:
        logger.error("TODO: handle putting tile on top of another tile")

def draw_fluid(game: Game) -> None:
    # Draw a green bar that grows over time to show the fluid moving throughout the grid.
    # Start at the game.state.fluid_position
    # If the fluid is at the edge of the grid, it should wrap around to the other side.
    if game.state.clock_ticking:
        # draw the fluid as a line that grows over time, accounting for turns and intersections
        for i in range(len(game.state.fluid_state.path) - 1):
            start_pos = game.state.fluid_state.path[i]
            end_pos = game.state.fluid_state.path[i + 1]
            start_x, start_y = start_pos
            end_x, end_y = end_pos
            # start = get_draw_coords_from_grid_xy(start_pos)
            # end = get_draw_coords_from_grid_xy(end_pos)
            draw_start_x = (start_x % constants.GRID_COLS) * constants.TILE_SIZE
            draw_start_y = ((start_y % constants.GRID_ROWS) * constants.TILE_SIZE) + constants.MENU_HEIGHT
            draw_end_x = (end_x % constants.GRID_COLS) * constants.TILE_SIZE
            draw_end_y = ((end_y % constants.GRID_ROWS) * constants.TILE_SIZE) + constants.MENU_HEIGHT

            pg.draw.line(
                game.screen,
                constants.GREEN,
                (draw_start_x, draw_start_y),
                (draw_end_x, draw_end_y),
                5
            )
            # draw text of the coords of the line for debugging

            font = pg.font.Font(None, 36)
            text = font.render(f"{start_pos} -> {end_pos}", True, (255, 0, 0))
            game.screen.blit(
                text,
                (
                    (draw_start_x),
                    (draw_start_y),
                )
            )
            # logger.info(f"Drawing fluid line from {start_pos} to {end_pos} at {draw_start_x, draw_start_y} to {draw_end_x, draw_end_y}")


def draw_next_button(game: Game) -> None:
    # Draw the next button as a bit of text that says "Next", not am image
    next_button = pg.font.Font(None, 99).render("move", True, (255, 255, 255))

    next_button = pg.transform.scale(next_button, (constants.TILE_SIZE, constants.TILE_SIZE))
    x = constants.WIDTH - constants.TILE_SIZE
    game.screen.blit(next_button, (x, 0))
    # check if mouse is over the button
    if pg.mouse.get_pos()[0] > x and pg.mouse.get_pos()[1] < constants.TILE_SIZE:
        # draw a border around the button
        pg.draw.rect(game.screen, (255, 255, 255), (x, 0, constants.TILE_SIZE, constants.TILE_SIZE), 5)


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
        draw_fluid(game)
        draw_next_button(game)

        game.state.process_time()
        event: pg.event.Event
        for event in pg.event.get():
            match event.type:
                case pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        put_tile_at_pos(game, get_grid_xy_click_pos())
                case pg.MOUSEBUTTONUP:
                    # Once they place their first tile, the clock starts.
                    game.state.clock_ticking = True
                case pg.QUIT:
                    game.state.running = False

        pg.display.flip()  # redraw
        clock.tick(60)

    pg.quit()

if __name__ == '__main__':
    main()