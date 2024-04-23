import random
import logging


from classes.bots.example import Example



class Bot(Example):
    def __init__(self, map_graph):
        super().__init__(map_graph)
        self.flag = 0
        self.not_processed_u = list()
        self.not_processed_t = list()
        self.rez=[]
        self.inp={}
        self.unitMove=[]
        self.enemy_units = None
        self.enemy_towns = None
        self.player_units = None
        self.player_towns = None
        self.name = 'Bot'
        logging.warning(map_graph)

    def genMaps(self):
        logging.warning("aaaaa")
        rez={}
        a={}
        for i in self.player_towns:
            a[i.name]={'level': i.level}
        rez['player_towns']=a
        a={}
        for i in self.enemy_units:
            a[i.name]={'level': i.level}
        rez['enemy_towns']=a
        a={}
        logging.warning("ssssss")
        for i in self.player_units:
            a[i.name] = {'location':i.location, 'is_moved': i.is_moved, 'finish_town': i.finish_town}
        rez['player_units'] = a
        for i in self.enemy_units:
            a[i.name] = {'location':i.location}
        rez['enemy_units'] = a

        return rez

    def move(self, client_towns: list, enemy_towns: list, client_units: list, enemy_units: list):
        self.player_towns = client_towns
        self.enemy_towns = enemy_towns
        self.player_units = client_units
        self.enemy_units = enemy_units
        inp=self.genMaps()
        self.inp=inp
        self.rez = []

        # есть 2 стадии игры: разведка и деф/атак, пока пишу разведку и защиту
        return self.stadiaR(inp)

    def stadiaR(self, inp):
        townsNearbady = []
        logging.warning(inp['player_towns'])
        for u in inp['player_units']:
            loc = inp['player_units'][u]['location']
            a = True
            for t in inp['player_towns']:
                if (loc == t):
                    a = False
                    break

            if (a and loc.count('t') == 1):
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

    # общие методы
