class Player:
    def __init__(self, bot, number, villages):
        self.bot = bot
        self.number = number
        self.villages = villages
        self.units = {}
        self.score = 1
