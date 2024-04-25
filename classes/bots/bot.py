class Bot(Example):
    def __init__(self, map_graph):
        super().__init__(map_graph)
        self.flag = 0
        self.name = 'Bot'

    def move(self, client_towns: list, enemy_towns: list, client_units: list, enemy_units: list):
        return []