from game_messages import Message

# Component for entities that allows them to fight.
# Holds the information directly related to combat, so we avoid
# giving non-fighting entities things like HP

# This will be a composition, which is an alternative to inheritance! Hey, new thing!

# Inheritance is for "is a" relationships, composition is for "has a"
# Example, parent and child would inherit person, but child would be a composition of parent.

class Fighter:
    def __init__(self, hp, defense, power, owner=None):
        self.max_hp = hp
        self.current_hp = self.max_hp
        self.defense = defense
        self.power = power
        self.owner = owner

    def attack(self, target):
        results = []
        damage = self.power - target.fighter.defense
        if damage > 0:
            results.append({'message': Message("{0} attacks {1} for {2} points of damage!".format(self.owner.name.capitalize(), target.name.capitalize(), str(damage)))})
            results.extend(target.fighter.take_damage(damage))
        else:
            results.append({'message': Message("{0} tries to hurt {1}, but his bitch-ass noddle arms aren't up to the challenge!".format(self.owner.name.capitalize(), target.name.capitalize()))})
        if target.fighter.current_hp <= 0:
            pass
        return results

    def take_damage(self, amount):
        results = []
        self.current_hp -= amount
        if self.current_hp <= 0:
            results.append({'dead': self.owner})
        return results
