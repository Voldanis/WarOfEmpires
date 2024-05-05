import random
import math
from classes.bots.example import Example


class Bot(Example):
    def __init__(self, map_graph):
        super().__init__(map_graph)
        self.name = 'China'
        self.best_roads = dict()
        self.my_towns_d = dict()
        self.enemy_towns_d = dict()
        self.my_locations = set()
        self.enemy_locations = set()
        self.t_indexes = dict()
        for i in self.map_graph.keys():
            if i[0] == 't':
                self.t_indexes[i] = 0


    def move(self, client_towns: list, enemy_towns: list, client_units: list, enemy_units: list):
        reqs = []
        self.my_towns_d = dict()
        self.enemy_towns_d = dict()
        self.my_locations = set()
        self.enemy_locations = set()
        for town in client_towns:
            self.my_towns_d[town.name] = town
        for town in enemy_towns:
            self.enemy_towns_d[town.name] = town
        for u in client_units:
            self.my_locations.add(u.location)
        for u in enemy_units:
            self.enemy_locations.add(u.location)
        self.find_best_roads(client_towns, enemy_towns)

        soldiers = dict()
        enemy_towns_opposite = dict()
        for town in client_towns:
            if self.t_indexes[town.name] == 0:
                for i in range((town.level + 1) // 2):
                    reqs.append(('equip', town.name))
                    town.coins -= 2
            self.t_indexes[town.name] += 1
            if self.map_graph[self.best_roads[town.name]]['start_town'] in self.enemy_towns_d.keys():
                max_index = 0
                soldiers[town.name] = []
                enemy_towns_opposite[town.name] = self.map_graph[self.best_roads[town.name]]['start_town']
            elif self.map_graph[self.best_roads[town.name]]['finish_town'] in self.enemy_towns_d.keys():
                max_index = 0
                soldiers[town.name] = []
                enemy_towns_opposite[town.name] = self.map_graph[self.best_roads[town.name]]['finish_town']
            else:
                max_index = 1
            if self.t_indexes[town.name] > max_index:
                self.t_indexes[town.name] = 0
            if town.coins >= round((town.level + 1) * ((5 + town.level) / 3)):
                reqs.append(('upgrade', town.name))
                town.coins -= round((town.level + 1) * ((5 + town.level) / 3))
                self.t_indexes[town.name] = 0

        for unit in client_units:
            if unit.location[0] == 't' and not unit.is_moved:
                if unit.location not in self.my_towns_d.keys():
                    reqs.append(('capture', unit.name))
                elif unit.location in soldiers.keys():
                    soldiers[unit.location].append(unit)
                else:
                    road = self.best_roads[unit.location]
                    reqs.append(('move', unit.name, road))

        '''enemy_squads = dict()
        for i in self.best_roads.values():
            enemy_squads[i] = []
            for _ in self.map_graph[i]['length']:
                enemy_squads[i].append([0, 0])
        for unit in enemy_units:
            if unit.location in enemy_squads.keys():
                enemy_squads[unit.location][unit.segment][0] += unit.atk
                enemy_squads[unit.location][unit.segment][1] += unit.hp'''
        '''soldier = 0
                    len(soldiers[war_town])
                    while self.my_towns_d[war_town].coins > 0:

                        self.best_roads[war_town]'''


        for war_town in soldiers.keys():
            road = self.best_roads[war_town]
            if self.my_towns_d[war_town].level > 4:
                if len(self.my_towns_d[war_town].units) > 0:
                    first_unit = self.my_towns_d[war_town].units[0]
                    reqs.append(('increase', first_unit, 'max_hp', self.my_towns_d[war_town].coins // 2))
                    reqs.append(('increase', first_unit, 'heal', self.my_towns_d[war_town].coins // 2))
                    reqs.append(('move', first_unit, road))
            for sold in soldiers[war_town]:
                reqs.append(('move', sold.name, road))
        return reqs

    def find_best_roads(self, my_ts, e_ts):
        self.best_roads = dict()
        for my_t in my_ts:
            passed = set()
            queue = [my_t.name]
            endpoints = set()
            lens = {my_t.name: 0}
            parent = {}

            while len(queue) > 0:
                processed_city = queue.pop(0)
                for road in self.map_graph[processed_city]:
                    if self.map_graph[road]['finish_town'] == processed_city:
                        next_town = self.map_graph[road]['start_town']
                    else:
                        next_town = self.map_graph[road]['finish_town']
                    if next_town not in lens.keys() or self.map_graph[road]['length'] + lens[processed_city] + 1 < lens[next_town]:
                        lens[next_town] = self.map_graph[road]['length'] + lens[processed_city] + 1
                        parent[next_town] = [processed_city, road]
                    if next_town in self.enemy_towns_d.keys():
                        endpoints.add(next_town)
                        if road in self.enemy_locations and road not in self.my_locations and processed_city == my_t.name:
                            lens[next_town] -= 99
                    elif next_town not in self.my_towns_d.keys() and road not in self.my_locations and next_town not in self.my_locations:
                        endpoints.add(next_town)
                    elif next_town not in passed and next_town not in queue:
                        queue.append(next_town)
                passed.add(processed_city)

            if len(endpoints) == 0:
                self.best_roads[my_t.name] = random.choice(self.map_graph[my_t.name])
            else:
                endtown = ''
                min_len = 999
                for endpoint in endpoints:
                    if lens[endpoint] < min_len:
                        min_len = lens[endpoint]
                        endtown = endpoint
                while parent[endtown][0] != my_t.name:
                    endtown = parent[endtown][0]
                self.best_roads[my_t.name] = parent[endtown][1]