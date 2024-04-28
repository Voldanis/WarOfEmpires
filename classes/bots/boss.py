import random
import logging
import time

from classes.bots.example import Example


class Boss(Example):
    def __init__(self, map_graph):
        super().__init__(map_graph)
        self.town = None
        self.flag = 0
        self.not_processed_u = list()
        self.not_processed_t = list()
        self.rez = []
        self.inp = {}
        self.unitMove = []
        self.enemy_units = None
        self.enemy_towns = None
        self.player_units = None
        self.player_towns = None
        self.name = 'LoseBoss'
        self.unitInTown = []

    def genMaps(self):
        rez = {}
        a = {}
        for i in self.player_towns:
            a[i.name] = {'level': i.level}
        rez['player_towns'] = a
        a = {}
        for i in self.enemy_towns:
            a[i.name] = {'level': i.level}
        rez['enemy_towns'] = a
        a = {}
        for i in self.player_units:
            a[i.name] = {'location': i.location, 'is_moved': i.is_moved, 'finish_town': i.finish_town}
        rez['player_units'] = a
        a = {}
        for i in self.enemy_units:
            a[i.name] = {'location': i.location}
        rez['enemy_units'] = a

        return rez

    def move(self, client_towns: list, enemy_towns: list, client_units: list, enemy_units: list):
        self.player_towns = client_towns
        self.enemy_towns = enemy_towns
        self.player_units = client_units
        self.enemy_units = enemy_units
        inp = self.genMaps()
        self.inp = inp
        self.rez = []
        a = ''
        for i in client_towns:
            a += i.name
            a += " "
        logging.warning(a)
        # есть 2 стадии игры: разведка и деф/атак, пока пишу разведку и защиту
        return self.stadiaR(inp)

    def defallTown(self):
        for t in self.player_towns:
            name = t.name
            roads = self.map_graph[name]
            self.defTown(t, roads)

    def defTown(self, town, roads):
        self.unitInTown = town.units
        if self.unitInTown is None:
            self.unitInTown = []
        self.town = town
        for road in roads:
            enemyUnit = self.poiskUnitsOnAtack(road)
            myUnit = self.poiskUnitsOnDef(road)
            if len(enemyUnit) > 0:
                budget = self.ozenkaAtak(enemyUnit) - self.ozenkaAtak(myUnit)
                self.randomSeach(myUnit, enemyUnit, budget, road)

    def createUsersIsUsers_data(self, unitsInp):
        rez = []
        for i in unitsInp:
            rez.append(User(i.hp, i.defense, i.atk, i.location, i.segment, i.finish_town))
        return rez

    def randomSeach(self, myUnit, enemyUnit, budget, road):
        # находишь оптимальные действия, закидываешь в улучшение
        t = time.time() * 1000
        enemyUnit = self.createUsersIsUsers_data(enemyUnit)
        myUnit = self.createUsersIsUsers_data(myUnit)
        maxDef = self.maxDef(enemyUnit)

        s = []
        if len(self.unitInTown) == 0:
            self.createUnit(self.town.name)
            self.town.coins -= 2
            return

        newUnitName = self.unitInTown[0]
        self.unitInTown.pop(0)

        while t + 50 < time.time() * 1000:
            myUnit2 = myUnit.copy()
            defence = random.randint(0, maxDef)
            budget -= defence
            if budget < 0:
                budget = 0
            hp = 4 * random.randint(0, budget) + 4
            budget -= hp
            if budget < 0:
                budget = 0
            atk = random.randint(0, budget)
            myUnit2.append(User(hp, defence, atk, self.town.name))
            a = self.simBoy(myUnit2, enemyUnit, self.town)
            if a == 1:
                self.upUnit(newUnitName, 'atk', atk)
                self.upUnit(newUnitName, 'max_hp', hp)
                self.upUnit(newUnitName, 'def', defence)
                self.otprInRoad(newUnitName, road)
                self.town.coins -= atk + hp + defence
                return

    def maxDef(self, units):
        maxAtk = 1
        for unit in units:
            maxAtk = max(maxAtk, unit.atk)
        return maxAtk - 1

    def ozenkaAtak(self, units):
        rez = 0
        for unit in units:
            rez += 2
            rez += unit.atk - 1
            rez += unit.hp // 4 - 1
            rez += unit.defense
        return rez

    def poiskUnitsOnAtack(self, road):
        rez = []
        for u in self.enemy_units:
            if u.location == road:
                rez.append(u)
        return rez

    def poiskUnitsOnDef(self, road):
        rez = []
        for u in self.player_units:
            if u.location == road:
                rez.append(u)
        return rez

    def stadiaR(self, inp):
        townsNearbady = []
        self.defallTown()
        for u in inp['player_units']:
            loc = inp['player_units'][u]['location']
            a = True
            for t in inp['player_towns']:
                if loc == t:
                    a = False
                    break
            if a and loc.count('t') == 1:
                self.zashvatTown(u)

        for t in inp['player_towns']:
            townsNearbady += self.townNearby(t)
        townsNearbady = self.toDel(townsNearbady, self.unitMoveInTown(inp))
        townsNearbady = self.toDel(townsNearbady, self.shuisFast(inp))
        townsNearbady = self.toDel(townsNearbady, self.muTowns())

        for town in inp['player_towns']:
            townsR = self.peresechenie(self.townNearby(town), townsNearbady)
            townsR = self.sortMasTown(townsR, town)

            for t in townsR:
                u = self.ifUnitintiwn(inp, town)
                if u != 'a':
                    self.otprInTown(u, t)
                    self.unitMove.append(u)
                else:
                    self.createUnit(town)
            townsNearbady = self.toDel(townsNearbady, townsR)

        for t in inp['player_towns']:
            self.upTown(t)
        return self.rez

    def muTowns(self):
        rez = []
        for i in self.inp['player_towns']:
            rez.append(i)
        return rez

    def sortMasTown(self, inpTownNear, town):
        a = {}
        for t1 in inpTownNear:
            r1 = self.map_graph[t1]
            r2 = self.map_graph[town]
            for i in r1:
                for j in r2:
                    if i == j:
                        a[t1] = self.map_graph[i]['length']
                        break
        s = {k: v for k, v in sorted(a.items(), key=lambda item: item[1])}
        rez = []
        for i in s:
            rez.append(i)
        return rez

    def ifUnitintiwn(self, inp, town):
        for i in inp['player_units']:
            if inp['player_units'][i]['location'] == town and inp['player_units'][i]['is_moved'] == False:
                if i not in self.unitMove:
                    return i
        return 'a'

    def peresechenie(self, mas1, mas2):
        rez = []
        for i in mas1:
            for j in mas2:
                if i == j:
                    rez.append(i)
                    break
        return rez

    def toDel(self, masOb, vib):
        rez = []
        for i in masOb:
            a = True
            for j in vib:
                if i == j:
                    a = False
                    break
            if a:
                rez.append(i)
        return rez

    def unitMoveInTown(self, inp):
        rez = []
        for unit in inp['player_units']:
            if inp['player_units'][unit]['location'].count('r') == 1:
                rez.append(inp['player_units'][unit]['finish_town'])
            else:
                loc = inp['player_units'][unit]['location']
                a = True
                for t in inp['player_towns']:
                    if loc == t:
                        a = False
                        break
                if a:
                    rez.append(loc)
        return rez

    def shuisFast(self, inp):
        rez = []
        for i in inp['enemy_towns']:
            rez.append(i)
        return rez

    # Методы связаные с городами
    def upTown(self, townToUp):
        self.rez.append(('upgrade', townToUp))

    def townNearby(self, town):
        dorogi = self.map_graph[town]
        itog = []
        for d in dorogi:
            a = self.map_graph[d]
            if a['start_town'] == town:
                itog.append(a['finish_town'])
            else:
                itog.append(a['start_town'])
        return itog

    # Методы связаные с юнитами
    def upUnit(self, unit, shararacteristic, money):
        self.rez.append(('increase', unit, shararacteristic, money))

    def createUnit(self, town):
        self.rez.append(('equip', town))

    def otprInRoad(self, unit, road):
        self.rez.append(('move', unit, road))

    def otprInTown(self, unit, town):
        r1 = self.map_graph[town]
        r2 = self.map_graph[self.inp['player_units'][unit]['location']]
        road = 'a'
        for i in r1:
            for j in r2:
                if i == j:
                    road = i
                    break

        if road == 'a':
            return 0
        self.rez.append(('move', unit, road))

    def zashvatTown(self, unit):
        self.rez.append(('capture', unit))

    def simBoy(self, myUnit: list, enemyUnit: list,
               townName):  # 2 - полная победа 1 - победа при моём 1 ходе,0 - поражение
        rez = 0
        road = self.map_graph[enemyUnit[0].location]
        r = enemyUnit[0].location
        myStartPosition = 0
        myPer = 1
        protPer = -1
        if townName == road['finish_town']:
            myStartPosition = road['length'] - 1
            myPer = -1
            protPer = 1
        while len(myUnit) > 0 and len(enemyUnit) > 0:
            for unitIsAtack in myUnit:
                segment2 = myStartPosition
                if unitIsAtack.location.count('r') == 1:
                    segment2 = unitIsAtack.segment + myPer
                per = True
                for i in range(len(enemyUnit)):
                    if enemyUnit[i].segment == segment2:
                        per = False
                        enemyUnit[i].hp -= unitIsAtack.atk

                        if enemyUnit[i].hp <= 0:
                            enemyUnit.pop(i)
                        break
                if per:
                    if unitIsAtack.location.count('t') == 1:
                        unitIsAtack.location = r
                    unitIsAtack.segment = segment2

            for unitIsAtack in enemyUnit:
                segment2 = unitIsAtack.segment + protPer
                per = True
                if segment2 == -1 or segment2 == road['length']:
                    for i in range(len(myUnit)):
                        if myUnit[i].location == townName:
                            per = False
                            myUnit[i].hp -= unitIsAtack.atk
                            if myUnit[i].hp <= 0:
                                myUnit.pop(i)
                            break
                    if per:
                        return 0
                else:
                    for i in range(len(myUnit)):
                        if myUnit[i].segment == segment2:
                            per = False
                            myUnit[i].hp -= unitIsAtack.atk

                            if myUnit[i].hp <= 0:
                                myUnit.pop(i)
                            break
                    if per:
                        unitIsAtack.segment = segment2

        if len(myUnit) > 0:
            rez += 1
        return rez


class User:
    def __init__(self, hp, defence, atk, location, segment=None, finish_town=None):
        self.hp = hp
        self.defense = defence
        self.atk = atk
        self.location = location
        self.segment = segment
        self.finish_town = finish_town
