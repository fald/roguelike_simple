class Level:
    def __init__(self, curr_level=1, curr_xp=0, level_up_base=200, level_up_factor=150):
        self.curr_level = curr_level
        self.curr_xp = curr_xp
        self.level_up_base = level_up_base
        self.level_up_factor = level_up_factor

    @property
    def experience_to_next_level(self):
        return self.level_up_base + self.curr_level * self.level_up_factor

    def add_xp(self, amount):
        self.curr_xp += amount
        if self.curr_xp > self.experience_to_next_level:
            self.curr_xp -= self.experience_to_next_level
            self.curr_level += 1
            return True
        else:
            return False

        