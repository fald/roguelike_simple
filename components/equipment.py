from equipment_slots import EquipmentSlots

class Equipment:
    def __init__(self, main_hand=None, off_hand=None, owner=None):
        self.main_hand = main_hand
        self.off_hand = off_hand
        self.owner = owner

    # TODO: Probably just have a gear property thats a list of equipment
    # that is iterated over for all the stats

    @property
    def hp_bonus(self):
        bonus = 0
        if self.main_hand and self.main_hand.equippable:
            bonus += self.main_hand.equippable.hp_bonus
        if self.off_hand and self.off_hand.equippable:
            bonus += self.off_hand.equippable.hp_bonus
        return bonus

    @property
    def power_bonus(self):
        bonus = 0
        if self.main_hand and self.main_hand.equippable:
            bonus += self.main_hand.equippable.power_bonus
        if self.off_hand and self.off_hand.equippable:
            bonus += self.off_hand.equippable.power_bonus
        return bonus

    @property
    def defense_bonus(self):
        bonus = 0
        if self.main_hand and self.main_hand.equippable:
            bonus += self.main_hand.equippable.defense_bonus
        if self.off_hand and self.off_hand.equippable:
            bonus += self.off_hand.equippable.defense_bonus
        return bonus

    def toggle_equip(self, equippable_entity):
        # TODO: This is gross, please make it nicer for future game
        results = []
        slot = equippable_entity.equippable.slot

        if slot == EquipmentSlots.MAIN_HAND:
            if self.main_hand == equippable_entity:
                self.main_hand = None
                results.append({"unequipped": equippable_entity})
            else:
                if self.main_hand:
                    results.append({"unequipped": self.main_hand})
                self.main_hand = equippable_entity
                results.append({"equipped": equippable_entity})
        elif slot == EquipmentSlots.OFF_HAND:
            if self.off_hand == equippable_entity:
                self.off_hand = None
                results.append({"unequipped": equippable_entity})
            else:
                if self.off_hand:
                    results.append({"unequipped": self.off_hand})
                self.off_hand = equippable_entity
                results.append({"equipped": equippable_entity})

        return results
