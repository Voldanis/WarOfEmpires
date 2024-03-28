import random

from bots.example import Example


class Bot(Example):
    def move(self, response: dict):
        if response['status_kode'] == 0 or response['status_kode'] == 2:
            self.response = response
            return 'equip', random.choice(list(self.response['p_villages'].keys()))
        if response['status_kode'] == 103 or response['status_kode'] == 104 or response['status_kode'] == 3:
            unit = random.choice(list(self.response['p_units'].keys()))
            if self.response['p_units'][unit]['location'][0] == 'r':
                return  'move', unit, 'aboba'
            return 'move', unit, random.choice(self.roads[self.response['p_units'][unit]['location']])
        return 'end'
