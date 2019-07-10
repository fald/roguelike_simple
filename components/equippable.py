class Equippable:
    def __init__(self, slot, power_bonus=0, defense_bonus=0, hp_bonus=0, owner=None):
        self.slot = slot
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.hp_bonus = hp_bonus
        self.owner = owner
