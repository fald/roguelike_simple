from enum import Enum

# TODO: Add an easy way to toggle gamestates >.<

class GameStates(Enum):
    PLAYER_DEAD = 0
    PLAYER_TURN = 1
    ENEMY_TURN = 2
    MENU_SCREEN = 3
    DROP_INVENTORY = 4
    TARGETING = 5
