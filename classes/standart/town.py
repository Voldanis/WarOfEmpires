import random

from classes.standart.unit import Unit


class Town:
    with open(f"classes\\standart\\unit_names.txt", 'r') as f:
        names = f.read()
        names = names.split()
    used_names = []

    def __init__(self, name, roads):
        self.name = name
        self.roads = roads
        self.level = 1
        self.coins = 0
        self.empire = None
        self.units = []

    def upgrade(self):
        self.coins -= round((self.level + 1) * ((5 + self.level) / 3))
        self.level += 1

    def equip(self, name=None):
        self.coins -= 2
        if name is None:
            if len(self.names) <= 0:
                name = str(random.randint(0, 10 ** 9))
                while name in self.used_names:
                    name = str(random.randint(0, 10 ** 9))
            else:
                name = self.names.pop(random.randint(0, len(self.names) - 1))
        elif name in self.names:
            self.names.remove(name)
        self.used_names.append(name)
        self.units.append(name)
        return Unit(name, self.empire, self.name)




