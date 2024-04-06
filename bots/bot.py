import random

from bots.example import Example


class Bot(Example):
    def __init__(self, map_graph):
        super().__init__(map_graph)
        self.flag = 0
        self.not_processed_u = list()
        self.not_processed_v = list()

    def move(self, response: dict):
        if response['status_kode'] == 103 or response['status_kode'] == 102:
            self.flag = 1
        if self.flag == 0:
            self.response = response
            self.not_processed_u = list(self.response['p_units'].keys())
            self.not_processed_v = list(self.response['p_villages'].keys())
            return 'equip', random.choice(list(self.response['p_villages'].keys()))
        if self.flag == 1:
            if len(self.not_processed_u) > 0:
                unit = self.not_processed_u.pop(-1)
                if self.response['p_units'][unit]['location'][0] == 'v':
                    if self.response['p_units'][unit]['location'] not in self.response['p_villages'].keys():
                        return 'capture', unit
                    else:
                        return 'move', unit, random.choice(self.map_graph[self.response['p_units'][unit]['location']])
                else:
                    return 'move', unit, 'aboba'
            self.flag = 2
        if self.flag == 2:
            if len(self.not_processed_v) > 0:
                vil = self.not_processed_v.pop(-1)
                return 'upgrade', vil
            self.flag = 0
        return 'end'

