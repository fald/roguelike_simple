import tcod as libtcod
from random import randint
from game_messages import Message

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


class ConfusedMonster:
    def __init__(self, previous_ai, number_of_turns=10, owner=None):
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns
        self.owner = owner

    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        if self.number_of_turns > 0:
            random_x = self.owner.x + randint(0, 2) - 1
            random_y = self.owner.y + randint(0, 2) - 1
            if random_x != self.owner.x and random_y != self.owner.y:
                self.owner.move_towards(random_x, random_y, game_map, entities)
            self.number_of_turns -= 1
        else:
            self.owner.ai = self.previous_ai
            results.append({'message': Message('The {0} is no longer confused!'.format(self.owner.name), libtcod.red)})
      
        return results
