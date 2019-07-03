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

    def remove_item(self, item):
        self.items.remove(item)

    def drop(self, item):
        results = []

        item.x = self.owner.x
        item.y = self.owner.y
        self.remove_item(item)
        results.append({'item_dropped': item, 'message': Message('You dropped the {0}'.format(item.name), libtcod.yellow)})

        return results

    def use(self, item_entity, **kwargs):
        results = []

        item_component = item_entity.item

        if item_component.use_function is None:
            results.append({'message': Message("The {0} cannot be used.".format(item_entity.name), libtcod.yellow)})
        else:
            # kwargs = {**item_component.function_kwargs, **kwargs}
            # item_use_results = item_component.use_function(self.owner, **kwargs)

            # for item_use_result in item_use_results:
            #     if item_use_result.get('consumed'):
            #         self.remove_item(item_entity)
            
            # results.extend(item_use_results)
            if item_component.targeting and not (kwargs.get('target_x') or kwargs.get('target_y')):
                results.append({'targeting': item_entity})
            else:
                kwargs = {**item_component.function_kwargs, **kwargs}
                item_use_results = item_component.use_function(self.owner, **kwargs)

                for item_use_result in item_use_results:
                    if item_use_result.get('consumed'):
                        self.remove_item(item_entity)

                results.extend(item_use_results)

        return results
