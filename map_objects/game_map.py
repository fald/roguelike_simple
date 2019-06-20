from map_objects.tile import Tile

class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):
        tiles = [[Tile(False) for y in range(self.height)] for x in range(self.width)]

        tiles[30][22] = Tile(True)
        tiles[31][22] = Tile(True)
        tiles[32][32] = Tile(True)

        return tiles

    def is_blocked(self, x, y):
        # Can be shortened, but will apparently be modifying it soon enough to not be necessary
        if self.tiles[x][y].blocked:
            return True

        return False
