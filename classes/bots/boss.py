from classes.bots.example import Example


class Boss(Example):
    def __init__(self, map_graph):
        super().__init__(map_graph)
        self.name = 'Boss'



'''if response['status_code'] == 103 or response['status_code'] == 102 or response['status_code'] == 104:
            self.flag = 1
        if self.flag == 0:
            self.response = response
            self.not_processed = set(self.response['player_units'].keys())
            return 'equip', random.choice(list(self.response['player_towns'].keys()))
        if self.flag == 1:
            for unit in self.not_processed:
                self.not_processed.remove(unit)
                if self.response['player_units'][unit]['location'][0] == 't':
                    if self.response['player_units'][unit]['location'] not in self.response['player_towns'].keys():
                        return 'capture', unit
                    else:
                        return 'move', unit, random.choice(self.map_graph[self.response['player_units'][unit]['location']])
                else:
                    return 'move', unit, 'aboba'
            self.flag = 0
        return 'end'
'''
