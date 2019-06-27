from map_objects.tile import Tile
from map_objects.rectangle import Rect
from random import randint
from entity import Entity
import tcod as libtcod
from components.ai import BasicMonster
from components.fighter import Fighter
from components.item import Item
from render_functions import RenderOrder
from components.item_functions import heal

# TODO: Double check logic on room overlaps?
# TODO: random map generation, also random mazes. Also? Rooms within mazes!
# Ideas for generation past basic stuff:
# Have randomized width pathways between rooms, within a range.
#   example: 1-3 wide path is 'small', randomizes width for each step and position
# TODO: Non-rect rooms?
# TODO: Various levels of blocked? Implement vision ranges and such into environment.
# TODO: Allow graphics in place of characters; still simple, no real animation.
# TODO: More elegant way to random generate rooms?
# TODO: Just use len(rooms) instead of num_room variable...?

class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]

        return tiles

    def make_map(self, max_rooms, min_size, max_size, map_width, map_height, player, entities, max_monsters_per_room, max_items_per_room):
        rooms = []
        # num_rooms = 0
        failures_in_a_row = 0
        max_failures_in_a_row = 20

        # This entire while loop is an attempt to make more rooms from less
        while len(rooms) <= max_rooms and failures_in_a_row < max_failures_in_a_row:
            w, h = randint(min_size, max_size), randint(min_size, max_size)
            x, y = randint(0, map_width - w - 1), randint(0, map_height - h - 1)
            new_room = Rect(x, y, w, h)

            for room in rooms:
                if new_room.intersect(room):
                    failures_in_a_row += 1
                    break
            else:
                failures_in_a_row = 0
                self.create_room(new_room)
                new_x, new_y = new_room.center()
                if len(rooms) == 0:
                    player.x, player.y = new_x, new_y
                else:
                    prev_x, prev_y = rooms[-1].center()
                    if randint(0, 1) == 0:
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                self.place_entities(new_room, entities, max_monsters_per_room, max_items_per_room)
                rooms.append(new_room)
                # num_rooms += 1

        # for i in range(max_rooms):
        #     # random w, h
        #     w = randint(min_size, max_size)
        #     h = randint(min_size, max_size)
        #     # random position within map bounds
        #     x = randint(0, map_width - w - 1)
        #     y = randint(0, map_height - h - 1)
        #
        #     new_room = Rect(x, y, w, h)
        #     for room in rooms:
        #         # Anyone else not sure 'room' is a word any more?
        #         if new_room.intersect(room):
        #             break
        #     else:
        #         # No intersections, room is valid.
        #         self.create_room(new_room)
        #         new_x, new_y = new_room.center()
        #         if num_rooms == 0:
        #             # Place player in center of 1st room
        #             player.x = new_x
        #             player.y = new_y
        #         else:
        #             # All other rooms get to have tunnels joined to prev room
        #             prev_x, prev_y = rooms[-1].center()
        #             # Determine order to move; horiz/vert or vert/horiz
        #             if randint(0, 1) == 0:
        #                 self.create_h_tunnel(prev_x, new_x, prev_y)
        #                 self.create_v_tunnel(prev_y, new_y, new_x)
        #             else:
        #                 self.create_v_tunnel(prev_y, new_y, prev_x)
        #                 self.create_h_tunnel(prev_x, new_x, new_y)
        #         rooms.append(new_room)
        #         num_rooms += 1
        return

    def create_room(self, room):
        # go through the tiles in the rectangle to make them passable
        # room is a Rect (map_objects.rectangle)
        # +1 is to ensure walls exist when rooms are immediately beside each other.
        # Kind of gross, I guess, but can work out a better way later.
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y] = Tile(False)

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y] = Tile(False)

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y] = Tile(False)

    def is_blocked(self, x, y):
        # Can be shortened, but will apparently be modifying it soon enough to not be necessary
        if self.tiles[x][y].blocked:
            return True

        return False

    def place_entities(self, room, entities, max_monsters_per_room, max_items_per_room):
        # Items
        num_items = randint(0, max_items_per_room)
        for i in range(num_items):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)
            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                item_component = Item(use_function=heal, amount=4)
                item = Entity(x, y, '!', libtcod.violet, 'Potion of Healing', blocks=False, render_order=RenderOrder.ITEM, item=item_component)
                entities.append(item)

        # Mobs
        num_monsters = randint(0, max_monsters_per_room)
        for i in range(num_monsters):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)
            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                # If not overlapping another monster...
                if randint(0, 100) < 80:
                    orc_fighter_component = Fighter(10, 0, 3)
                    orc_ai_component = BasicMonster()
                    monster = Entity(x, y, 'o', libtcod.desaturated_green, "Orc", blocks=True, render_order=RenderOrder.ACTOR, fighter=orc_fighter_component, ai=orc_ai_component)
                else:
                    troll_fighter_component = Fighter(16, 1, 4)
                    troll_ai_component = BasicMonster()
                    monster = Entity(x, y, 'T', libtcod.darker_green, "Troll", blocks=True, render_order=RenderOrder.ACTOR, fighter=troll_fighter_component, ai=troll_ai_component)

                entities.append(monster)
