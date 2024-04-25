class UnitData:
    def __init__(self, unit, segment, player):
        self.name = unit.name
        self.location = unit.location
        self.segment = segment
        self.finish_town = unit.finish_town
        self.hp = unit.hp
        self.atk = unit.atk
        self.defense = unit.defense
        if player == 'client':
            self.max_hp = unit.max_hp
            self.is_moved = unit.is_moved

    def __init__(self, hp, defence, atk, location):
        self.name = 'aaa'
        self.location = location
        self.segment = None
        self.finish_town = None
        self.hp = hp
        self.atk = atk
        self.defense = defence
