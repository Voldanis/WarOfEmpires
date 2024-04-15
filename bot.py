import random


from bots.example import Example



class Bot(Example):
    def __init__(self, map_graph):
        super().__init__(map_graph)
        self.flag = 0
        self.not_processed_u = list()
        self.not_processed_t = list()

    def move(self, response: dict):
        reqs = []
        for town in response['player_towns'].keys():
            reqs.append(('equip', town))
        for unit in response['player_units'].keys():
            if response['player_units'][unit]['location'][0] == 't':
                if response['player_units'][unit]['location'] not in response['player_towns'].keys():
                    reqs.append(('capture', unit))
                else:
                    road = random.choice(list(self.map_graph[response['player_units'][unit]['location']]))
                    reqs.append(('move', unit, road))
        return reqs