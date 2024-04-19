class TownData:
    def __init__(self, town, player):
        self.name = town.name
        self.level = town.level
        self.units = town.units.copy()
        if player == 'client':
            self.coins = town.coins
