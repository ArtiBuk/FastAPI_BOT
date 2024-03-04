from enum import Enum, unique
from functools import lru_cache


class City(Enum):
    NORILSK = "norilsk"
    TALNAH = "talnah"
    KAIRKAN = "kairkan"
    DUDINKA = "dudinka"


class ObjectCategory(Enum):
    RESTAURANT = "restaurant"
    FAST_FOOD = "fast_food"
    HOSTEL = "hostel"
    CHILD_CENTER = "child_center"

