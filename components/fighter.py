from game_messages import Message

# Component for entities that allows them to fight.
# Holds the information directly related to combat, so we avoid
# giving non-fighting entities things like HP

# This will be a composition, which is an alternative to inheritance! Hey, new thing!

# Inheritance is for "is a" relationships, composition is for "has a"
# Example, parent and child would inherit person, but child would be a composition of parent.

class Fighter:
    def __init__(self, hp, defense, power, owner=None, xp=0, attack_speed=0):
        self.base_max_hp = hp
        self.current_hp = hp
        self.base_defense = defense
        self.base_power = power
        self.owner = owner
        self.xp = xp
        self.attack_speed=attack_speed

    @property
    def max_hp(self):
        if self.owner and self.owner.equipment:
                bonus = self.owner.equipment.hp_bonus
        else:
            bonus = 0

        return self.base_max_hp + bonus
    
    @property
    def power(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.power_bonus
        else:
            bonus = 0

        return self.base_power + bonus

    @property
    def defense(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.defense_bonus
        else:
            bonus = 0

        return self.base_defense + bonus

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
        self.owner.wait = self.attack_speed
        return results

    def take_damage(self, amount):
        results = []
        self.current_hp -= amount
        if self.current_hp <= 0:
            results.append({'dead': self.owner, 'xp': self.xp})
        return results

    def heal(self, amount):
        self.current_hp = min(self.current_hp + amount, self.max_hp)