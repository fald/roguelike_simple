from map_objects.tile import Tile
from map_objects.rectangle import Rect
from random import randint
from entity import Entity
import tcod as libtcod
from components.ai import BasicMonster
from components.fighter import Fighter
from components.item import Item
from components.stairs import Stairs
from components.equipment import Equipment, EquipmentSlots
from components.equippable import Equippable
from render_functions import RenderOrder
from components.item_functions import heal, cast_lightning, cast_fireball, cast_confuse
from game_messages import Message
from random_utils import random_choice_from_dict, from_dungeon_level

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
# TODO: Allow going back up a floor

class GameMap:
    def __init__(self, width, height, dungeon_level=1):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.dungeon_level = dungeon_level

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]

        return tiles

    def make_map(self, max_rooms, min_size, max_size, map_width, map_height, player, entities):
        rooms = []
        # num_rooms = 0
        failures_in_a_row = 0
        max_failures_in_a_row = 20

        # Stairs just going to be in middle of final room for simplicity.
        center_of_last_room_x = None
        center_of_last_room_y = None

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
                center_of_last_room_x = new_x
                center_of_last_room_y = new_y
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

                self.place_entities(new_room, entities)
                rooms.append(new_room)
        
        stairs_component = Stairs(self.dungeon_level + 1)
        down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, '>', libtcod.white,
                            'Stairs', blocks=False, render_order=RenderOrder.STAIRS, stairs=stairs_component)
        entities.append(down_stairs)

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

    def place_entities(self, room, entities):
        # Items
        max_items_per_room = from_dungeon_level([[1, 1], [2, 4]], self.dungeon_level)
        num_items = randint(0, max_items_per_room)
        item_chances = {
            'sword': from_dungeon_level([[5, 4]], self.dungeon_level),
            'shield': from_dungeon_level([[15, 8]], self.dungeon_level),
            'healing_potion': 35,
            'lightning_scroll': from_dungeon_level([[25, 4]], self.dungeon_level),
            'fireball_scroll': from_dungeon_level([[25, 6]], self.dungeon_level),
            'confusion_scroll': from_dungeon_level([[10, 2]], self.dungeon_level)
        }
        for i in range(num_items):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)
            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                item_choice = random_choice_from_dict(item_chances)
                if item_choice == 'healing_potion':
                    # Health pots
                    item_component = Item(use_function=heal, amount=40)
                    item = Entity(x, y, '!', libtcod.violet, 'Potion of Healing', blocks=False, render_order=RenderOrder.ITEM, item=item_component)
                elif item_choice == 'fireball_scroll':
                    # Fireball scrolls
                    item_component = Item(use_function=cast_fireball, damage=30, radius=3, targeting=True, targeting_message=Message('Left click a tile to cast fireball, or right click to cancel.', libtcod.light_cyan))
                    item = Entity(x, y, '#', libtcod.red, "Fireball Scroll", blocks=False, render_order=RenderOrder.ITEM, item=item_component)
                elif item_choice == 'confusion_scroll':
                    # Confuse scrolls
                    item_component = Item(use_function=cast_confuse, targeting=True, targeting_message=Message("Left click on an enemy to confuse it, or right click to cancel", libtcod.light_cyan))
                    item = Entity(x, y, '#', libtcod.light_pink, "Confusion Scroll", blocks=False, render_order=RenderOrder.ITEM, item=item_component)
                elif item_choice == 'lightning_scroll':
                    # Lightning scrolls
                    item_component = Item(use_function=cast_lightning, damage=50, max_range=5)
                    item = Entity(x, y, '#', libtcod.yellow, "Lightning Scroll", blocks=False, render_order=RenderOrder.ITEM, item=item_component)
                elif item_choice == 'sword':
                    # Yadda yadda
                    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=3)
                    item = Entity(x, y, '/', libtcod.sky, 'Sword', equippable=equippable_component)
                elif item_choice == 'shield':
                    equippable_component = Equippable(EquipmentSlots.OFF_HAND, defense_bonus=1)
                    item = Entity(x, y, '[', libtcod.darker_orange, 'Shield', equippable=equippable_component)
                entities.append(item)

        # Mobs
        # Bad way of doing constants. Fix it, or just hard code it? Fix it for new projects, learn from my mistakes, future me.
        max_monsters_per_room = from_dungeon_level([[2, 1], [3, 4], [5, 6]], self.dungeon_level)
        num_monsters = randint(0, max_monsters_per_room)
        monster_chances = {
            'orc': 80,
            'troll': from_dungeon_level([[15, 3], [30, 5], [60, 7]], self.dungeon_level)
        }
        for i in range(num_monsters):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)
            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                # If not overlapping another monster...
                monster_choice = random_choice_from_dict(monster_chances)
                if monster_choice == 'orc':
                    orc_fighter_component = Fighter(20, 0, 4, xp=35, attack_speed=20)
                    orc_ai_component = BasicMonster()
                    monster = Entity(
                        x, y, 'o', libtcod.desaturated_green, "Orc", blocks=True, 
                        render_order=RenderOrder.ACTOR, fighter=orc_fighter_component, 
                        ai=orc_ai_component, speed=8)
                else:
                    troll_fighter_component = Fighter(30, 2, 8, xp=100, attack_speed=20)
                    troll_ai_component = BasicMonster()
                    monster = Entity(
                        x, y, 'T', libtcod.darker_green, "Troll", blocks=True, 
                        render_order=RenderOrder.ACTOR, fighter=troll_fighter_component, 
                        ai=troll_ai_component, speed=8)

                entities.append(monster)

    def next_floor(self, player, message_log, constants):
        self.dungeon_level += 1
        entities = [player]
        self.tiles = self.initialize_tiles()
        self.make_map(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'], constants['map_width'],
                        constants['map_height'], player, entities)
        player.fighter.heal(player.fighter.max_hp // 2)
        message_log.add_message(Message('You take a moment to rest and recover your strength.', libtcod.light_violet))

        return entities
