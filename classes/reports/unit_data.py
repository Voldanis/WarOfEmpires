from classes.standart import unit
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

    def init2(self, hp, defence, atk, location):
        self.name = 'aaa'
        self.location = location
        self.segment = None
        self.finish_town = None
        self.hp = hp
        self.atk = atk
        self.defense = defence


def new(hp, defence, atk, location):
    u=unit.Unit("a",'a', location)
    unit.atk=atk
    unit.defense=defence
    unit.hp=hp
    return UnitData(u,None,'aa')