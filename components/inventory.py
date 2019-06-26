import tcod as libtcod
from game_messages import Message

class Inventory:
    def __init__(self, capacity, owner=None):
        self.capacity = capacity
        self.items = []
        self.owner = owner

    def add_item(self, item):
        results = []

        if len(self.items) < self.capacity:
            self.items.append(item)
            result = {
                'item_added': item,
                'message': Message("You have added {0} to your inventory.".format(item.name), libtcod.blue)
            }
        else:
            result = {
                'item_added': None,
                'message': Message("You cannot carry any more, your inventory is full.", libtcod.yellow)
            }
        results.append(result)

        return results