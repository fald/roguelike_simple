import tcod as libtcod
# TODO: Better AI, dear god...
class BasicMonster:
    # Currently, if the mob can be seen by the player, it moves towards the player.
    def take_turn(self, target, fov_map, game_map, entities):
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            if monster.distance_to(target) >= 2:
                monster.move_towards(target.x, target.y, game_map, entities)
            elif target.fighter.current_hp > 0:
                print("The {0} insults you! Your ego is damaged!".format(monster.name))
        else:
            pass
