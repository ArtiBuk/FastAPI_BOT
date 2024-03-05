from enum import Enum, unique
from functools import lru_cache


class City(Enum):
    NORILSK = "Норильск"
    TALNAH = "Талнах"
    KAIRKAN = "Кайркан"
    DUDINKA = "Дудинка"


class ObjectCategory(Enum):
    RESTAURANT = "Рестаран"
    FAST_FOOD = "Fast food"
    HOSTEL = "Хостел"
    CHILD_CENTER = "Десткий центр"

