import random

from classes.unit import Unit


class Village:
    names = ['greed', 'edgar', 'qina', 'tina', 'tu', 'fred', 'qila', 'twez', 'sas', 'hu', 'jif', 'olga', 'efgri', 'grif', 'geed', 'nutti', 'qn', 'astrid', 'qia', 'fraid', 'fafi', 'qsvi', 'q', 'jap', 'hugh', 'qtx', 'zes', 'dog', 'zeus', 'svagrik', 'efra', 'efgrid', 'graf', 'elgrad', 'okjewu', 'efrida', 'alah', 'faid', 'fafid', 'hron', 'svag', 'fagr', 'ew', 'hill', 'wez', 'zag', 'stu', 'sasla', 'feid', 'olha', 'zags']
    used_names = []

    def __init__(self, name, roads):
        self.name = name
        self.roads = roads
        self.level = 1
        self.coins = 0
        self.empire = None
        self.units = []

    def __str__(self):
        return self.roads

    def upgrade(self):
        self.coins -= round((self.level + 1) * ((5 + self.level) / 3))
        self.level += 1

    def equip(self):
        self.coins -= 2
        if len(self.names) <= 0:
            name = str(random.randint(0, 10 ** 9))
            while name in self.used_names:
                name = str(random.randint(0, 10 ** 9))
        else:
            name = self.names.pop(random.randint(0, len(self.names) - 1))
        self.used_names.append(name)
        self.units.append(name)
        return Unit(name, self.empire, self.name)




