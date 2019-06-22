
# Component for entities that allows them to fight.
# Holds the information directly related to combat, so we avoid
# giving non-fighting entities things like HP

# This will be a composition, which is an alternative to inheritance! Hey, new thing!

# Inheritance is for "is a" relationships, composition is for "has a"
# Example, parent and child would inherit person, but child would be a composition of parent.

class Fighter:
    def __init__(self, hp, defense, power):
        self.max_hp = hp
        self.current_hp = self.max_hp
        self.defense = defense
        self.power = power
