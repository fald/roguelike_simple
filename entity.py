from math import sqrt
import tcod as libtcod
from render_functions import RenderOrder

class Entity:
    """
    Base entity; generic object to represent players, enemies, items and more!
    """
    # TODO: Just have a single components library ><
    def __init__(self, x, y, char, color, name, blocks=False, render_order=RenderOrder.CORPSE, 
                fighter=None, ai=None, inventory=None, item=None, stairs=None, level=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.fighter = fighter
        self.ai = ai
        self.inventory = inventory
        self.item = item
        self.stairs = stairs
        self.render_order = render_order
        self.level = level

        # Setting the owner of the components to self for future use when
        # we may want to access the entity from the component.
        if self.fighter:
            self.fighter.owner = self
        if self.ai:
            self.ai.owner = self
        if self.item:
            self.item.owner = self
        if self.inventory:
            self.inventory.owner = self
        if self.stairs:
            self.stairs.owner = self
        if self.level:
            self.level.owner = self

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def distance(self, target_x, target_y):
        return sqrt((target_x - self.x) ** 2 + (target_y - self.y) ** 2)

    def move_towards(self, target_x, target_y, game_map, entities):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = sqrt(dx ** 2 + dy ** 2)
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        if not (game_map.is_blocked(self.x + dx, self.y + dy) or get_blocking_entities_at_location(entities, self.x + dx, self.y + dy)):
            self.move(dx, dy)

    def move_astar(self, target, entities, game_map):
        # Create FOV map with game_map's dimensions
        fov = libtcod.map_new(game_map.width, game_map.height)

        # Scan current map each turn, set all walls as blocked
        for y1 in range(game_map.height):
            for x1 in range(game_map.width):
                libtcod.map_set_properties(fov, x1, y1, not game_map.tiles[x1][y1].block_sight, not game_map.tiles[x1][y1].blocked)
        # Scan all objects to determine if they must be navigated around
        # Ensure checked that object isn't target or self
        # AI handles what to do if next to target, after all
        for entity in entities:
            if entity.blocks and entity != self and entity != target:
                # Set tile as if it was a wall
                libtcod.map_set_properties(fov, entity.x, entity.y, True, False)
        # Allocate an A* path
        diagonal_move_cost = 1.41
        my_path = libtcod.path_new_using_map(fov, diagonal_move_cost)
        # Compute path between self and target's coordinates
        libtcod.path_compute(my_path, self.x, self.y, target.x, target.y)

        # Check if this path exists, and if so, if its shorter than some tolerance
        # Path size matters if you want the monster to use alternate pathways, such as through other rooms.
        # Example, player in corridor, but limit the tolerance so mobs don't go around whole map.
        path_tolerance = 25
        if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < path_tolerance:
            # Find next coordinates in completed full path
            x, y = libtcod.path_walk(my_path, True)
            if x or y:
                # Set self coordinates to next tile (???????????)
                self.x = x
                self.y = y
        else:
            # In case of no path (ie something is temporarily blocking), at least make it move towards player, dumbly
            self.move_towards(target.x, target.y, game_map, entities)

            # Free memory, apparently we need to pay attention to that, maybe it wasn't all Atom's fault...
        libtcod.path_delete(my_path)



    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return sqrt(dx ** 2 + dy ** 2)

# This function relates to entities in general, but not to a specific entity, so
# it is not a method within the class
# TODO: Would it be easier to work it like walking into walls?
def get_blocking_entities_at_location(entities, destination_x, destination_y):
    for entity in entities:
        if entity.blocks and entity.x == destination_x and entity.y == destination_y:
            return entity

    return None
