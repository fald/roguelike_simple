from enum import Enum

# TODO: Add an easy way to toggle gamestates >.<

class GameStates(Enum):
    PLAYER_TURN = 1
    ENEMY_TURN = 2
    PLAYER_DEAD = 0
    MENU_SCREEN = 3
    DROP_INVENTORY = 4
