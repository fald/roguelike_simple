class Entity:
    """
    Base entity; generic object to represent players, enemies, items and more!
    """

    def __init__(self, x, y, char, color, name, blocks=False, fighter=None, ai=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.fighter = fighter
        self.ai = ai

        # Setting the owner of the components to self for future use when
        # we may want to access the entity from the component.
        if self.fighter:
            self.fighter.owner = self
        if self.ai:
            self.ai.owner = self

    def move(self, dx, dy):
        self.x += dx
        self.y += dy


# This function relates to entities in general, but not to a specific entity, so
# it is not a method within the class
# TODO: Would it be easier to work it like walking into walls?
def get_blocking_entities_at_location(entities, destination_x, destination_y):
    for entity in entities:
        if entity.blocks and entity.x == destination_x and entity.y == destination_y:
            return entity

    return None
