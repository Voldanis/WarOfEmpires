class Unit:
    def __init__(self, name, empire, location):
        self.name = name
        self.empire = empire
        self.location = location
        self.finish_town = None
        self.is_moved = True
        self.max_hp = 4
        self.hp = 4
        self.atk = 1
        self.defense = 0

