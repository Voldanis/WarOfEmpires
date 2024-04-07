class Player:
    def __init__(self, bot, empire, towns):
        self.bot = bot
        self.empire = empire
        self.towns = towns
        self.units = set()
        self.units_queue = []


