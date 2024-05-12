import random
import logging

from classes.bots.example import Example


class Boss(Example):

    def __init__(self, map_graph):
        super().__init__(map_graph)
        self.map_graph = map_graph
        self.name = 'SpamBoss'
        self.enemy_units = None
        self.enemy_towns = None
        self.player_units = None
        self.player_towns = None
        self.saveTowmsName = []
        self.upTownUnit = []
        self.turn = 0

    def move(self, client_towns: list, enemy_towns: list, client_units: list, enemy_units: list):
        self.player_towns = client_towns
        self.player_units = client_units
        self.enemy_towns = enemy_towns
        self.enemy_units = enemy_units
        self.saveTowmsName = []
        self.turn += 1

        logging.warning('my ' + str(len(client_units)))
        logging.warning('enemy ' + str(len(enemy_units)))
        upUnit = ''
        for i in client_towns:
            upUnit += i.name
            upUnit += " level: "
            upUnit += str(i.level)
            upUnit += ', '
        logging.warning(upUnit)
        upUnit = ''
        for i in enemy_towns:
            upUnit += i.name
            upUnit += " level: "
            upUnit += str(i.level)
            upUnit += ', '
        logging.warning(upUnit)

        rez = []
        al = []

        for u in client_units:
            if u.location[0] == 't':
                flag = True
                for t in client_towns:
                    if u.location == t.name:
                        flag = False
                        road = self.optimalRoad(t)
                        al.append(('move', u.name, road))
                        u.location = road
                        break
                if flag:
                    rez.append(('capture', u.name))

        self.zapSaveTown()

        oz = self.ozenkaUnits(enemy_units) - self.ozenkaUnits(client_units)

        for t in client_towns:
            colUnit = self.colMyUnitInTown(t)
            logging.warning(colUnit)
            db = 1
            if t.name in self.saveTowmsName:
                if oz >= 5:
                    db = 1
                else:
                    db = 0

            if colUnit >= t.level + 1:
                if oz > 0:
                    rez += self.upUnitsInTown(t, t.level + db)
            else:
                a = t.level + 1 - colUnit
                if a < (t.level + db) // 2:
                    rez += self.upUnitsInTown(t, a-(t.level + db) // 2 * 2)
                for _ in range(min((t.level + db) // 2, t.level + 1 - colUnit)):
                    rez.append(('equip', t.name))

        rez += al
        for t in client_towns:
            rez.append(('upgrade', t.name))
        return rez

    def optimalRoad(self, town):
        roadsName = self.map_graph[town.name]
        roadsInMyTown = []
        roadsInEnemyTowns = []
        roadsInNeitTowns = []

        for roadName in roadsName:
            road = self.map_graph[roadName]
            t2Name = road['finish_town']
            if t2Name == town.name:
                t2Name = road['start_town']
            if self.isMyTown(t2Name):
                roadsInMyTown.append(roadName)
            elif self.isEnemyTown(t2Name):
                roadsInEnemyTowns.append(roadName)
            else:
                roadsInNeitTowns.append(roadName)

        for roadName in roadsInNeitTowns:
            flag = True
            for unit in self.player_units:
                if unit.location == roadName:
                    flag = False
                    break
            if flag:
                return roadName

        a = {}
        for roadName in roadsInEnemyTowns:
            a[roadName] = self.myUnitInroad(roadName) - self.myEnemyInroad(roadName)
        s = {k: v for k, v in sorted(a.items(), key=lambda item: item[1])}
        for i in s:
            return i

        for roadName in roadsInMyTown:
            road = self.map_graph[roadName]
            t2 = road['finish_town']
            if t2 == roadName:
                t2 = road['start_town']
            if t2 in self.getDefTowns():
                return roadName
        if len(roadsInMyTown) <= 0:
            return roadsName[0]

        return roadsInMyTown[random.randint(0, len(roadsInMyTown) - 1)]

    def isMyTown(self, townName):
        for t in self.player_towns:
            if t.name == townName:
                return True
        return False

    def isEnemyTown(self, townName):
        for t in self.enemy_towns:
            if t.name == townName:
                return True
        return False

    def myUnitInroad(self, roadName):
        rez = 0
        for unit in self.player_units:
            if unit.location == roadName:
                rez += unit.hp // 2 - 1
                rez += unit.atk
                rez += unit.defense
        return rez

    def myEnemyInroad(self, roadName):
        rez = 0
        for unit in self.enemy_units:
            if unit.location == roadName:
                rez += unit.hp // 2 - 1
                rez += unit.atk
                rez += unit.defense
        return rez

    def getDefTowns(self):
        rez = []
        for t in self.player_towns:
            if self.getDefTowm(t):
                rez.append(t.name)
        return rez

    def getDefTowm(self, town):
        roadsName = self.map_graph[town.name]

        for roadName in roadsName:
            road = self.map_graph[roadName]
            t2 = road['finish_town']
            if t2 == roadName:
                t2 = road['start_town']
            if self.isEnemyTown(t2):
                return True
        return False

    def ozenkaUnits(self, units):
        rez = 0
        for unit in units:
            rez += unit.hp // 2 - 1
            rez += unit.atk
            rez += unit.defense
        return rez

    def zapSaveTown(self):
        df = self.getDefTowns()
        for town in self.player_towns:
            if town.name not in df:
                flag = True
                roadsName = self.map_graph[town.name]
                for roadName in roadsName:
                    road = self.map_graph[roadName]
                    t2Name = road['finish_town']
                    if t2Name == town.name:
                        t2Name = road['start_town']
                    if not self.isMyTown(t2Name) and self.myUnitInroad(roadName) == 0:
                        flag = False
                        break

                if flag:
                    self.saveTowmsName.append(town.name)

    def colMyUnitInTown(self, town):
        rez = 0
        for roadName in self.map_graph[town.name]:
            segment = 0
            road = self.map_graph[roadName]
            if road['finish_town'] == town.name:
                segment = road['length'] - 1
            for unit in self.player_units:
                if unit.location == roadName and unit.segment == segment and unit.finish_town == town.name:
                    rez += 1
        return rez

    def upUnitsInTown(self, town, budget):
        rez = []
        units = self.getUnitsIsUnitsName(town.units)
        while budget > 0:
            flag = True
            for unit in units:
                if budget > 0:
                    if unit.atk < 4:
                        budget -= 1
                        flag = False
                        rez.append(('increase', unit.name, 'atk', 1))
            if flag:
                break
        return rez

    def getUnitsIsUnitsName(self, unitsNames):
        rez = []
        for unit in self.player_units:
            if unit.name in unitsNames:
                rez.append(unit)
        return rez


if __name__ == '__main__':
    pass
