import random

from classes.bots.example import Example


class Bot(Example):
    def __init__(self, map_graph):
        super().__init__(map_graph)

    def move(self, client_towns: list, enemy_towns: list, client_units: list, enemy_units: list):
        reqs = []
        client_towns_names = []
        for town in client_towns:
            reqs.append(('equip', town.name))
            client_towns_names.append(town.name)
        for unit in client_units:
            if unit.location[0] == 't':
                if unit.location not in client_towns_names:
                    reqs.append(('capture', unit.name))
                else:
                    road = random.choice(list(self.map_graph[unit.location]))
                    reqs.append(('move', unit.name, road))
        return reqs

'''if response['status_code'] == 103 or response['status_code'] == 102 or response['status_code'] == 104:
            self.flag = 1
        if self.flag == 0:
            self.response = response
            self.not_processed_u = list(self.response['player_units'].keys())
            self.not_processed_t = list(self.response['player_towns'].keys())
            return 'equip', random.choice(list(self.response['player_towns'].keys()))
        if self.flag == 1:
            if len(self.not_processed_u) > 0:
                unit = self.not_processed_u.pop(-1)
                if self.response['player_units'][unit]['location'][0] == 't':
                    if self.response['player_units'][unit]['location'] not in self.response['player_towns'].keys():
                        return 'capture', unit
                    else:
                        return 'move', unit, random.choice(self.map_graph[self.response['player_units'][unit]['location']])
                else:
                    return 'move', unit, 'aboba'
            self.flag = 2
        if self.flag == 2:
            if len(self.not_processed_t) > 0:
                town = self.not_processed_t.pop(-1)
                return 'upgrade', town
            self.flag = 0
        return 'end'
'''

