import enum


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
