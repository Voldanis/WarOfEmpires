import random
import logging
import time

from classes.bots.example import Example
from classes.reports import unit_data
from classes.standart import unit

class Boss(Example):
    def __init__(self, map_graph):
        super().__init__(map_graph)
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
        self.name = 'Bot'
        self.unitInTown=[]

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

        # есть 2 стадии игры: разведка и деф/атак, пока пишу разведку и защиту
        return self.stadiaR(inp)

    def defallTown(self):
        for t in self.player_towns:
            name = t.name
            roads = self.map_graph[name]
            self.defTown(t, roads)

    def defTown(self, town, roads):
        self.unitInTown=town.units
        for road in roads:
            enemyUnit=self.poiskUnitsOnAtack(road)
            myUnit=self.poiskUnitsOnDef(road)
            if(len(enemyUnit)>0):
                if(self.simBoy(myUnit, enemyUnit, town.name)==0):
                    budget = self.ozenkaAtak(enemyUnit) - self.ozenkaAtak(myUnit)
                    self.randomSeach(myUnit, enemyUnit, budget, town)

    def randomSeach(self, myUnit, enemyUnit, budget, town):
        #находишь оптимальные действия, закидываешь в улучшение
        t=time.time()*1000
        maxDef=self.maxDef(enemyUnit)
        budget=min(town.coins, budget)
        s=[]
        if(len(self.unitInTown)==0):
            self.createUnit(town)
            return
        newUnitName = self.unitInTown[-1]
        while(time.time()*1000<t+200):
            myUnit2=myUnit.copy()
            defence=random.randint(0,maxDef)
            hp=4*random.randint(0,budget-defence)+4
            atk=random.randint(0, budget-defence-hp)
            myUnit2.append(unit_data.a(hp, defence, atk, town.name))
            a=self.simBoy(myUnit2, enemyUnit, town)
            if(a==2):
                self.upUnit(newUnitName, 'atk', atk)
                self.upUnit(newUnitName, 'max_hp', hp)
                self.upUnit(newUnitName, 'def', defence)
                s=[]
                break
            elif(a==1):
                s=[]
                s.append(atk)
                s.append(hp)
                s.append(defence)
        if(len(s)>0):
            self.upUnit(newUnitName, 'atk', s[0])
            self.upUnit(newUnitName, 'max_hp', s[1])
            self.upUnit(newUnitName, 'def', s[2])


    def createUnit(self, town, unitName):
        self.rez.append(('equip', town, unitName))

    def simBoy(self, playUnits1: list, playUnits2: list,
               townName):  # 2 - полная победа 1 - победа при моём 1 ходе,0 - поражение
        rez = 0
        road = self.map_graph[playUnits2[0].location]
        units1 = playUnits1.copy()
        units2 = playUnits2.copy()
        myStartPosition = 0
        myPer = 1
        protPer=road['lenght']
        if (townName == road['finish_town']):
            myStartPosition = road['lenght']
            myPer = -1
            protPer=0

        while (len(units1) > 0 and len(units2) > 0):
            for unit in units1:
                segment2 = myStartPosition
                if (unit.location.count('r') == 1):
                    segment2 = unit.segment + myPer
                per = True
                for i in range(len(units2)):
                    if units2[i].segment == segment2:
                        per = False
                        units2[i].hp -= unit.atk
                        if (units2[i].hp <= 0):
                            playUnits2.pop(i)
                        break
                if per:
                    unit.segment = segment2

            for unit in units2:
                segment2 = unit.segment + protPer
                per = True
                for i in range(len(units1)):
                    if units1[i].segment == segment2:
                        per = False
                        units1[i].hp -= unit.atk
                        if (units1[i].hp <= 0):
                            playUnits2.pop(i)
                        break
                if per:
                    unit.segment = segment2

        if (len(units1) > 0):
            rez += 1

        while (len(units1) > 0 and len(units2) > 0):
            for unit in units2:
                segment2 = unit.segment + protPer
                per = True
                for i in range(len(units1)):
                    if units1[i].segment == segment2:
                        per = False
                        units1[i].hp -= unit.atk
                        if (units1[i].hp <= 0):
                            playUnits2.pop(i)
                        break
                if per:
                    unit.segment = segment2

            for unit in units1:
                segment2 = myStartPosition
                if (unit.location.count('r') == 1):
                    segment2 = unit.segment + myPer
                per = True
                for i in range(len(units2)):
                    if units2[i].segment == segment2:
                        per = False
                        units2[i].hp -= unit.atk
                        if (units2[i].hp <= 0):
                            playUnits2.pop(i)
                        break
                if per:
                    unit.segment = segment2

        if (len(units1) > 0):
            rez += 1

        return rez

    def maxDef(self, units):
        maxAtk=1
        for unit in units:
            maxAtk=max(maxAtk, unit.atk)
        return maxAtk-1
    def ozenkaAtak(self, units):
        rez=0
        for unit in units:
            rez+=2
            rez+=unit.atk-1
            rez += unit.hp//4 - 1
            rez += unit.defense
        return rez

    def poiskUnitsOnAtack(self, road):
        rez = []
        for u in self.enemy_units:
            if u.location in road:
                rez.append(u)
        return rez
    def poiskUnitsOnDef(self, road):
        rez = []
        for u in self.player_units:
            if u.location in road:
                rez.append(u)
        return rez

    def stadiaR(self, inp):
        townsNearbady = []
        for u in inp['player_units']:
            loc = inp['player_units'][u]['location']
            a = True
            for t in inp['player_towns']:
                if (loc == t):
                    a = False
                    break

            if (a and loc.count('t') == 1):
                self.zashvatTown(u)
        self.defallTown()

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
                if (u != 'a'):
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
                    if (i == j):
                        a[t1] = self.map_graph[i]['length']
                        break
        s = {k: v for k, v in sorted(a.items(), key=lambda item: item[1])}
        rez = []
        for i in s:
            rez.append(i)
        return rez

    def ifUnitintiwn(self, inp, town):
        for i in inp['player_units']:
            if (inp['player_units'][i]['location'] == town and inp['player_units'][i]['is_moved'] == False):
                if i not in self.unitMove:
                    return i
        return 'a'

    def peresechenie(self, mas1, mas2):
        rez = []
        for i in mas1:
            for j in mas2:
                if (i == j):
                    rez.append(i)
                    break
        return rez

    def toDel(self, masOb, vib):
        rez = []
        for i in masOb:
            a = True
            for j in vib:
                if (i == j):
                    a = False
                    break
            if (a):
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
                    if (loc == t):
                        a = False
                        break
                if (a):
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
            if (a['start_town'] == town):
                itog.append(a['finish_town'])
            else:
                itog.append(a['start_town'])
        return itog

    # Методы связаные с юнитами
    def upUnit(self, unit, shararacteristic, money):
        self.rez.append(('increase', unit, shararacteristic, money))

    def createUnit(self, town):
        self.rez.append(('equip', town))

    def otprInTown(self, unit, town):
        r1 = self.map_graph[town]
        r2 = self.map_graph[self.inp['player_units'][unit]['location']]
        road = 'a'
        for i in r1:
            for j in r2:
                if (i == j):
                    road = i
                    break

        if (road == 'a'):
            return 0
        self.rez.append(('move', unit, road))

    def zashvatTown(self, unit):
        self.rez.append(('capture', unit))

#if __name__=='__main__':

