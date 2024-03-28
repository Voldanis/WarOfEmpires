class Player:
    def __init__(self, bot, empire, villages):
        self.bot = bot
        self.empire = empire
        self.villages = villages
        self.units = set()
        self.score = 1
