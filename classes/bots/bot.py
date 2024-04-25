import random

from classes.bots.example import Example


class Bot(Example):
    def __init__(self, map_graph):
        super().__init__(map_graph)
        self.name = 'Nomad'

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


