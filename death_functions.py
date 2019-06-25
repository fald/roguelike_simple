import tcod as libtcod
from game_states import GameStates
from render_functions import RenderOrder
from game_messages import Message

def kill_player(player):
    player.char = '%'
    player.color = libtcod.dark_red

    return Message('You died!', libtcod.red), GameStates.PLAYER_DEAD

def kill_monster(monster):
    death_message = Message("{0} died!".format(monster.name.capitalize()), libtcod.orange)
    monster.color = libtcod.dark_crimson
    monster.ai = None
    monster.fighter = None
    monster.blocks = False
    monster.name = "Remains of {0}".format(monster.name)
    monster.render_order = RenderOrder.CORPSE

    return death_message