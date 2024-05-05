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
        self.alarm = False
        self.isDefTown = []

    def genMap(self):
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

    def gameFunction(self, inp):
        townsNearbady = []
        self.defAllTown()
        logging.warning('def complit')
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
        townsNearbady = self.toDel(townsNearbady, self.isEnemyTown(inp))
        townsNearbady = self.toDel(townsNearbady, self.myTowns())

        for town in inp['player_towns']:
            townsR = self.intersection(self.townNearby(town), townsNearbady)
            townsR = self.sortTowns(townsR, town)

            for t in townsR:
                u = self.ifUnitIsWin(inp, town)
                if u != 'a':
                    self.otprInTown(u, t)
                    self.unitMove.append(u)
                else:
                    self.createUnit(town)
            townsNearbady = self.toDel(townsNearbady, townsR)

        logging.warning('stadiaRcomplete')
        for t in inp['player_towns']:
            self.upTown(t)

        if self.alarm:
            self.supportAndAtakTownPost()

        self.atakOllTown()
        return self.rez

    def spam(self):
        a = ''
        client_towns = self.player_towns
        for i in client_towns:
            a += i.name
            a += " "
            a += str(i.level)
            a += ' '
        print(a)

        reqs = []
        client_towns_names = []
        for town in client_towns:
            reqs.append(('upgrade', town.name))
            for i in range((town.level + 1) // 2):
                reqs.append(('equip', town.name))
            client_towns_names.append(town.name)
        for unit in self.player_units:
            if unit.location[0] == 't':
                if unit.location not in client_towns_names:
                    reqs.append(('capture', unit.name))
                else:
                    reqs.append(('move', unit.name, self.lol(client_towns, unit.location)))
        return reqs

    def lol(self, player_town, unit_loc):
        roads = self.map_graph[unit_loc]

        for road in roads:
            t = self.map_graph[road]['finish_town']
            if self.map_graph[road]['finish_town'] == unit_loc:
                t = self.map_graph[road]['start_town']
            flag = True
            for pl_t in player_town:
                if t == pl_t.name:
                    flag = False
                    break
            if flag:
                return road

        return roads[random.randint(0, len(roads) - 1)]

    def move(self, client_towns: list, enemy_towns: list, client_units: list, enemy_units: list):
        self.player_towns = client_towns
        self.enemy_towns = enemy_towns
        self.player_units = client_units
        self.enemy_units = enemy_units
        inp = self.genMap()
        self.inp = inp
        self.rez = []

        a = ''
        for i in client_towns:
            a += i.name
            a += " level: "
            a += str(i.level)
            a += ', '
        logging.warning(a)
        logging.warning(f'colMuTown: {len(client_towns)}')
        logging.warning(len(enemy_units))

        if self.ozenkaAtak(enemy_units) >= 50:
            self.alarm = True
            return self.spam()
        else:
            self.alarm = False
            return self.gameFunction(inp)

    def defAllTown(self):
        for t in self.player_towns:
            roads = self.map_graph[t.name]
            self.defTown(t, roads)

    def createUsersFromUsers_data(self, unitsInp):
        rez = []
        for i in unitsInp:
            rez.append(User(i.hp, i.defense, i.atk, i.location, i.segment, i.finish_town))
        return rez

    def maxDef(self, units):
        maxAtk = 1
        for unit in units:
            maxAtk = max(maxAtk, unit.atk)
        return maxAtk - 1

    def maxAtk(self, units):
        maxHp = 1
        for unit in units:
            maxHp = max(maxHp, unit.hp)
        return maxHp

    def ozenkaAtak(self, units):
        rez = 0
        for unit in units:
            rez += unit.atk
            rez += unit.hp // 4
            rez += unit.defense
        return rez

    def poiskUnitsOfAtack(self, road):
        rez = []
        for u in self.enemy_units:
            if u.location == road or self.map_graph[road]['start_town'] == u.location or self.map_graph[road][
                'finish_town'] == u.location:
                rez.append(u)
        return rez

    def poiskUnitsFromDef(self, road):
        rez = []
        for u in self.player_units:
            if u.location == road:
                rez.append(u)
        return rez

    def myTowns(self):
        rez = []
        for i in self.inp['player_towns']:
            rez.append(i)
        return rez

    def sortTowns(self, inpTownNear, town):
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

    def ifUnitIsWin(self, inp, town):
        for i in inp['player_units']:
            if inp['player_units'][i]['location'] == town and inp['player_units'][i]['is_moved'] == False:
                if i not in self.unitMove:
                    return i
        return 'a'

    def intersection(self, mas1, mas2):
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

    def isEnemyTown(self, inp):
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

    def simulyBoy(self, myUnits: list, enemyUnits: list,
                  townName, roadName):  # 2 - полная победа 1 - победа при моём 1 ходе,0 - поражение
        rez = 0
        enemyUnit = self.copy(enemyUnits)
        myUnit = self.copy(myUnits)

        road = self.map_graph[roadName]
        myStartPosition = 0
        enemyStartPosition = road['length'] - 1
        myPer = 1
        protPer = -1
        if townName == road['finish_town']:
            myStartPosition = road['length'] - 1
            enemyStartPosition = 0
            myPer = -1
            protPer = 1

        for i in myUnit:
            if i.location[0] == 't':
                i.location = roadName
                i.segment = myStartPosition - myPer
        for i in enemyUnit:
            if i.location[0] == 't':
                i.location = roadName
                i.segment = enemyStartPosition - protPer

        while len(myUnit) > 0 and len(enemyUnit) > 0:
            for unitIsAtack in myUnit:
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
                    unitIsAtack.segment = segment2

            for unitIsAtack in enemyUnit:
                segment2 = unitIsAtack.segment + protPer
                per = True
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
            for i in myUnit:
                rez += i.hp
        else:
            for i in enemyUnit:
                rez -= i.hp
        return rez

    def randomSeach(self, myUnit, enemyUnit, budget, road):
        # находишь оптимальные действия, закидываешь в улучшение
        t = time.time() * 1000
        enemyUnit = self.createUsersFromUsers_data(enemyUnit)
        myUnit = self.createUsersFromUsers_data(myUnit)
        maxDef = self.maxDef(enemyUnit)
        if len(self.unitInTown) == 0:
            self.createUnit(self.town.name)
            self.town.coins -= 2
            return

        a = 'my '
        for i in myUnit:
            a += f'hp: {i.hp}, atk: {i.atk}, loc: {i.location}, '
        logging.warning(a)
        a = 'enemy '
        for i in enemyUnit:
            a += f'hp: {i.hp}, atk: {i.atk}, loc: {i.location}, '
        logging.warning(a)
        a = f'{self.town.name}: coins: {self.town.coins}, budget: {budget} '
        logging.warning(a)

        if self.town.coins - budget >= 7:
            self.helpOtSupport(self.town.name, self.town.coins - budget)

        budget = min(self.town.coins, budget - 1)

        if budget <= 0:
            budget = 2

        unitName = self.unitInTown[0]
        self.unitInTown.pop(0)

        u = None

        for i in self.player_units:
            if i.name == unitName:
                u = i

        if u is None:
            return

        itogApp = []
        s = -100000
        while t + 2 > time.time() * 1000:
            myUnit2 = self.copy(myUnit)
            defence = random.randint(0, maxDef)
            budget -= defence

            maxAtk = self.maxAtk(enemyUnit) - u.atk
            if maxAtk <= 0:
                atk = u.atk
                at = 0
            else:
                at = random.randint(0, maxAtk)
                atk = at + u.atk

            budget -= at

            hp = 4 * budget + u.hp

            myUnit2.append(User(hp, defence, atk, self.town.name))

            a = self.simulyBoy(myUnit2, enemyUnit, self.town.name, road)
            if a > s:
                itogApp = [at, (hp - u.hp) // 4, defence]
                s = a

        self.upUnit(unitName, 'atk', itogApp[0])
        self.upUnit(unitName, 'max_hp', itogApp[1])
        self.upUnit(unitName, 'def', itogApp[2])
        self.otprInRoad(unitName, road)
        self.town.coins -= itogApp[0] + itogApp[1] + itogApp[2]

    def defTown(self, town, roads):
        self.unitInTown = town.units.copy()
        if self.unitInTown is None:
            self.unitInTown = []
        self.town = town
        roadIsAtk = []
        for road in roads:
            enemyUnit = self.poiskUnitsOfAtack(road)
            myUnit = self.poiskUnitsFromDef(road)

            if len(enemyUnit) > 0:
                if self.simulyBoy(myUnit, enemyUnit, self.town.name, road) < 0:
                    self.isDefTown.append(town)
                    budget = self.ozenkaAtak(enemyUnit) - self.ozenkaAtak(myUnit)
                    self.randomSeach(myUnit, enemyUnit, budget, road)


    def atak(self):

        for town in self.saveTown():

            bud = town.level - 2

            for name in town.units:
                if bud >= 3:
                    self.upUnit(name, 'atk', 3)
                    self.upUnit(name, 'max_hp', bud - 3)
                elif bud == 2:
                    self.upUnit(name, 'atk', 1)
                    self.upUnit(name, 'max_hp', 1)
                else:
                    self.upUnit(name, 'atk', bud)
                self.otprInRoad(name, self.getRoadIsAtack(town))

    def saveTown(self):
        rez = []
        for t in self.player_towns:
            roads = self.map_graph[t.name]
            a = True
            for road in roads:
                tn = self.map_graph[road]['start_town']
                if self.map_graph[road]['start_town'] == t.name:
                    tn = self.map_graph[road]['finish_town']
                s = True
                for t in self.player_towns:
                    if tn == t.name:
                        s = False
                        break
                if s:
                    a = False
                    break
            if a:
                rez.append(t)
        return rez

    def getRoadIsAtack(self, town):
        saveTown = self.saveTown()
        for road in self.map_graph[town.name]:
            if self.map_graph[road]['start_town'] == town.name:
                if self.map_graph[road]['finish_town'] not in saveTown:
                    return road
            else:
                if self.map_graph[road]['start_town'] not in saveTown:
                    return road
        return self.map_graph[town.name][0]

    def copy(self, a: list):
        rez = []
        for i in a:
            rez.append(User(i.hp, i.defense, i.atk, i.location, i.segment, i.finish_town))
        return rez

    def townSaveNearbady(self, townName):
        saveTown = self.saveTown()
        rez = 0
        roads = self.map_graph[townName]
        for roadName in roads:
            road = self.map_graph[roadName]
            townN = road['start_town']
            if road['start_town'] == townName:
                townN = road['finish_town']
            flag = True
            for t in saveTown:
                if t.name == townN:
                    flag = False
                    break
            if flag:
                rez += 1
        return rez

    def supportAndAtakTownPost(self):
        alwaysTowns = self.saveTown()
        for town in alwaysTowns:
            colUnit = self.townSaveNearbady(town.name)
            if colUnit == 0 and town.level >= 6:
                colUnit = len(self.map_graph[town.name])
            for _ in range(colUnit - len(town.units)):
                self.createUnit(town.name)
        # подддерживает необходимое количество юнитов

    def townSearch(self, townName):
        saveTown = self.saveTown()
        roads = self.map_graph[townName]
        for roadName in roads:
            road = self.map_graph[roadName]
            townN = road['start_town']
            if road['start_town'] == townName:
                townN = road['finish_town']
            for t in saveTown:
                if t.name == townN:
                    return t
        return None

    def otprInTownNew(self, unitName, unitLoc, napr):
        for roadName in self.map_graph[unitLoc]:
            road = self.map_graph[roadName]
            if (road['start_town'] == unitLoc and road['finish_town'] == napr) or (
                    road['start_town'] == napr and road['finish_town'] == unitLoc):
                self.rez.append(('move', unitName, roadName))
                return

    def helpOtSupport(self, townName, budget):
        townOtpr = self.townSearch(townName)
        if townOtpr is None:
            return

        budget = min(townOtpr.coins, budget)
        if len(townOtpr.units) == 0:
            self.createUnit(townOtpr.name)
            return
        name = townOtpr.units[0]
        townOtpr.units.pop(0)
        if budget >= 3:
            self.upUnit(name, 'atk', 3)
            self.upUnit(name, 'max_hp', budget - 3)
        elif budget == 2:
            self.upUnit(name, 'atk', 1)
            self.upUnit(name, 'max_hp', 1)
        else:
            self.upUnit(name, 'atk', budget)
        self.otprInTownNew(name, townOtpr.name, townName)
        self.createUnit(townOtpr.name)

        # отправляет поддержку на бюджет
    def atakOllTown(self):
        saveTown=self.saveTown()
        atakTown=[]
        for town in self.player_towns:
            flag=True
            for t in saveTown:
                if t.name == town.name:
                    flag=False
                    break
            for t in self.isDefTown:
                if t.name == town.name:
                    flag=False
                    break
            if flag:
                atakTown.append(town)

        for town in atakTown:
            if town.level < 3:
                break
            road = self.poiskRoadIsAtk(town)
            for name in town.units:
                self.otprInRoad(name, road)

            for _ in range(town.coins//2):
                self.createUnit(town.name)


            roadsName = self.map_graph[town.name]
            for roadName in roadsName:
                for t in self.enemy_towns:
                    if t.name == roadName:
                        return roadName
            return None

    def poiskRoadIsAtk(self, town):
        roadsName = self.map_graph[town.name]
        for roadName in roadsName:
            for t in self.enemy_towns:
                if t.name == roadName:
                    return roadName
        return None
# 3 вида кордов, 1 форпосты, сапорты, дамагеры
class User:
    def __init__(self, hp, defence, atk, location, segment=None, finish_town=None):
        self.hp = hp
        self.defense = defence
        self.atk = atk
        self.location = location
        self.segment = segment
        self.finish_town = finish_town


def a():
    u = [User(4, 0, 1, 'r16', 3, 't11')]
    u1 = [User(4, 0, 1, 't11')]
    a = {'r16': {'finish_town': 't10', 'start_town': 't11', 'length': 4}}
    b = Boss(a)
    print(b.simulyBoy(u, u1, 't10', 'r16'))

    print(u[0].hp)
    print(u1[0].hp)


if __name__ == '__main__':
    for _ in range(-2):
        print(1)