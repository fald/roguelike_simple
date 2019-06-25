class Inventory:
    def __init__(self, capacity, owner=None):
        self.capacity = capacity
        self.items = []
        self.owner = owner