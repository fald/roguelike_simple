import tcod as libtcod

# TODO: Better AI, dear god...

class BasicMonster:
    def __init__(self, owner=None):
        self.owner = owner

    # Currently, if the mob can be seen by the player, it moves towards the player.
    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        monster = self.owner
        
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            if monster.distance_to(target) >= 2:
                monster.move_astar(target, entities, game_map)
            elif target.fighter.current_hp > 0:
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)
        else:
            monster.move_towards(target.x, target.y, game_map, entities)
        
        return results

