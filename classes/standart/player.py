class Player:
    def __init__(self, bot, empire, towns):
        self.bot = bot
        self.empire = empire
        self.towns = towns
        self.units = set()
        self.units_queue = []
        self.score = 0

    def count_points(self, map_graph: dict):
        self.score = 0
        for t in self.towns:
            self.score += map_graph[t].coins
            self.score += map_graph[t].level * 10000


