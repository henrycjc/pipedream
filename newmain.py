import logging

import pygame as pg

from wallace import constants, drawing
from wallace.game import Game, GameState


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def get_grid_xy_click_pos() -> tuple[int, int]:
    """
    Get the position of the mouse on the grid
    """
    mouse_pos: tuple[int, int] = pg.mouse.get_pos()
    mouse_tile_x, mouse_tile_y = mouse_pos
    grid_x = min(max(mouse_tile_x // constants.TILE_SIZE, 0), constants.GRID_COLS - 1)
    grid_y = min(max(constants.GRID_ROWS - (mouse_tile_y // constants.TILE_SIZE), 0), constants.GRID_ROWS - 1)
    draw_coords = drawing.get_draw_coords_from_grid_xy((grid_x, grid_y))
    logger.info(f"clicked {grid_x} {grid_y} from {mouse_pos} with draw coords {draw_coords}")
    return grid_x, grid_y


def put_tile_at_pos(game: Game, grid_xy: tuple[int, int]) -> None:
    if game.state.grid_at(grid_xy) is None:
        tile = game.state.pop_deque_and_replenish_tile()
        game.state.set_grid_at(grid_xy, tile)
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
        drawing.draw(game)
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