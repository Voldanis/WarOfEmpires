import random

from classes.standart.unit import Unit


class Town:
    names = ['Pof', 'XD', 'Odii', 'Fred', 'Mi', 'Uga', 'Era', 'Fun', 'Zvi', 'Ten', 'Prank', 'Omnom', 'Michel', 'Grif',
             'Ziwix', 'Tet', 'Summer', 'Q', 'Stu', 'Igyana', 'Tomorrow', 'Sigma', 'Kuzya', 'Soika', 'Edgar', 'Quick',
             'Hu', 'Miss', 'Astrid', 'Hill', 'Efgri', 'Spring', 'Fiona', 'Om', 'Sayanara', 'Elgrad', 'Cobra', 'Enk',
             'Sey', 'Glowing', 'Bep', 'Cat', 'Lyi', 'Madam', 'Jap', 'Vic', 'Sas', 'Ly', 'Gisp', 'Jic', 'Alah', 'Hloya',
             'Rabr', 'Thunderstorm', 'Dead', 'Runner', 'Macadamia', 'Edri', 'Jik', 'Oval', 'Arb', 'Update', 'Ex', 'Soa',
             'Sky', 'Dervish', 'Fagr', 'Yong', 'Yad', 'Jessika', 'Wise', 'Kia', 'Lemon', 'Kuz', 'Mijivan', 'Owl', 'Lu',
             'Jam', 'Doad', 'Zag', 'Nutti', 'Mickey', 'Gem', 'Odri', 'Ju', 'Eleven', 'Vasya', 'Zeus', 'Kai', 'Dodo',
             'Svag', 'Zombie', 'Hait', 'Ne', 'Wasix', 'Ziy', 'Efrieda', 'Karp', 'Olga', 'Zags', 'Sonya', 'Сhloe',
             'Seer', 'Enkza', 'Qn', 'X', 'Minion', 'Magical', 'Fafid', 'Dj', 'Faid', 'Tu', 'Hoy', 'Casey', 'Exza',
             'Bit', 'Thor', 'Staring', 'Geed', 'Ew', 'Enxap', 'Pap', 'Jif', 'Nlo', 'Ven', 'Graf', 'Okjewu', 'Iole',
             'Thunder', 'Fej', 'Minivan', 'Isona', 'Zap', 'Gerry', 'Sasla', 'Qm', 'Ritchie', 'Svagrik', 'Dog', 'Hyk',
             'Mep', 'Greed', 'Magikarp', 'Efgrid', 'Ded', 'Cj', 'Loop', 'Yxxx', 'Jesus', 'Qia', 'Noy', 'Twez', 'Saya',
             'Brat', 'Hugh', 'Marika', 'Feid', 'Ivix', 'Bob', 'Kjaben', 'Tank', 'Soe', 'Qtx', 'Crystal', 'Winged',
             'Hey', 'Hron', 'Tor', 'Padavan', 'Freeman', 'Qsvi', 'Perry', 'Rich', 'Zasno', 'Say', 'Wez', 'Zes', 'Aski',
             'Wasya', 'Mic', 'Acid', 'Tina', 'Exzo', 'Pif', 'Flux', 'Storm', 'Lea', 'Alkali', 'Poi', 'Efra', 'Holly',
             'Karncy', 'Genry', 'Fafi', 'Brother', 'Fraid', 'Olha', 'Soya', 'Clerk', 'Qila', 'Ufo', 'Mr', 'Qina', 'Ben']
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




