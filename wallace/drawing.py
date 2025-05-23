from wallace import constants
from wallace.game import Game
from wallace.assets import TileImage

import pygame as pg


def vec3to2(vec: pg.math.Vector3) -> pg.math.Vector2:
    """
    Convert a Vector3 to a tuple of ints
    """
    return pg.math.Vector2(int(vec.x), int(vec.y))

def get_draw_coords_from_grid_xy(grid_xy: tuple[int, int]) -> tuple[int, int]:
    return grid_xy[0] * constants.TILE_SIZE, (constants.GRID_ROWS - 1 - grid_xy[1]) * constants.TILE_SIZE + constants.MENU_HEIGHT


def draw(game: "Game") -> None:
    """
    Draw the game state to the screen
    """
    game.screen.fill(constants.BG_COLOR)
    _draw_grid(game)
    _draw_tile_queue(game)
    _draw_fluid(game)
    _draw_next_button(game)


def _draw_image(game: Game, grid_xy: tuple[int, int], tile: TileImage) -> None:
    assert tile, f"Tile is None at {grid_xy}"
    img = pg.image.load("assets/" + tile.value).convert_alpha()
    img = pg.transform.scale(img, (constants.TILE_SIZE, constants.TILE_SIZE))
    game.screen.blit(img, get_draw_coords_from_grid_xy(grid_xy))

def _draw_bg_tile(surface: pg.Surface, grid_xy: tuple[int, int], size: int) -> None:
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


def _draw_grid(game: Game) -> None:
    game.screen.fill(constants.BG_COLOR)

    def get_grid_xy_from_row_col(row_: int, col_: int) -> tuple[int, int]:
        return col_, constants.GRID_ROWS - 1 - row_

    for row in range(constants.GRID_ROWS):
        for col in range(constants.GRID_COLS):
            grid_xy = get_grid_xy_from_row_col(row, col)
            if game.state.grid_at(grid_xy) is None:
                 _draw_bg_tile(game.screen, grid_xy, constants.TILE_SIZE)
            else:
                _draw_image(game, grid_xy, game.state.grid_at(grid_xy))


def _draw_tile_queue(game: Game) -> None:
    for i in range(constants.TILE_QUEUE_SIZE):
        img = pg.image.load("assets/" + game.state.view_tile_queue()[i].value).convert_alpha()
        img = pg.transform.scale(img, (constants.TILE_SIZE - 10, constants.TILE_SIZE - 10))
        game.screen.blit(img, (i * constants.TILE_SIZE, 0))


def _draw_fluid(game: Game) -> None:
    # Draw a green bar that grows over time to show the fluid moving throughout the grid.
    # Start at the game.state.fluid_position
    if game.state.clock_ticking:
        # draw the fluid as a line that grows over time, accounting for turns and intersections
        for path_vec, next_path_vec in game.state.fluid_state.get_path():
            draw_start_x, draw_start_y = get_draw_coords_from_grid_xy(vec3to2(path_vec))
            draw_end_x, draw_end_y = get_draw_coords_from_grid_xy(vec3to2(next_path_vec))

            # Interpolate the endpoint based on the z value
            interpolated_x = draw_start_x + (draw_end_x - draw_start_x) * next_path_vec.z
            interpolated_y = draw_start_y + (draw_end_y - draw_start_y) * next_path_vec.z
            # print(
            #     f"Drawing line: Start=({draw_start_x}, {draw_start_y}), "
            #     f"End=({interpolated_x}, {interpolated_y}), z={path_vec.z}"
            # )

            # Draw the animated line
            pg.draw.line(
                game.screen,
                constants.GREEN,
                (draw_start_x + constants.TILE_SIZE // 2, draw_start_y + constants.TILE_SIZE // 2),
                (interpolated_x + constants.TILE_SIZE // 2, interpolated_y + constants.TILE_SIZE // 2),
                10
            )
            # draw text of the coords of the line for debugging



def _draw_next_button(game: Game) -> None:
    # Draw the next button as a bit of text that says "Next", not am image
    next_button = pg.font.Font(None, 99).render("move", True, (255, 255, 255))

    next_button = pg.transform.scale(next_button, (constants.TILE_SIZE, constants.TILE_SIZE))
    x = constants.WIDTH - constants.TILE_SIZE
    game.screen.blit(next_button, (x, 0))
    # check if mouse is over the button
    if pg.mouse.get_pos()[0] > x and pg.mouse.get_pos()[1] < constants.TILE_SIZE:
        # draw a border around the button
        pg.draw.rect(game.screen, (255, 255, 255), (x, 0, constants.TILE_SIZE, constants.TILE_SIZE), 5)
