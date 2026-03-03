from enum import Enum


class Position(str, Enum):

    TOP_LEFT = "top_left"

    TOP_CENTER = "top_center"

    TOP_RIGHT = "top_right"

    CENTER = "center"

    BOTTOM_LEFT = "bottom_left"

    BOTTOM_CENTER = "bottom_center"

    BOTTOM_RIGHT = "bottom_right"
