import time
import random

from bots.bot import Bot
from classes.village import Village
from classes.road import Road


class Server:
    def __init__(self, width, height):
        self.map_graph = dict()
        self.generate_map(width, height)
        self.units = dict()
        self.delay = 0.1
        self.p1_villages = {'v8'}
        self.p1_units = set()
        self.p1_score = 1
        self.p2_villages = {'v3'}
        self.p2_units = set()
        self.p2_score = 1

    def run(self, p1, p2):
        while self.p1_score < 90 and self.p2_score < 90:
            self.process_day_change()
            self.process_player(p1)
            self.process_player(p2)
        if self.p1_score >= 90:
            if type(p1) == Bot:
                print('player wins!')
            else:
                print('boss wins!')
        else:
            if type(p2) == Bot:
                print('player wins!')
            else:
                print('boss wins!')

    def process_request(self, player_num, request):
        if player_num == 1:
            p_villages = self.p1_villages
            p_units = self.p1_units
            enemy_villages = self.p2_villages
            enemy_units = self.p2_units
        else:
            p_villages = self.p2_villages
            p_units = self.p2_units
            enemy_villages = self.p1_villages
            enemy_units = self.p1_units


        if request == 'report':
            return self.report(p_villages, enemy_villages, p_units, enemy_units)
        elif type(request) == tuple and request[0] == 'upgrade':
            if request[1] in self.map_graph.keys():
                if request[1] in p_villages:
                    if self.map_graph[request[1]].coins >= self.map_graph[request[1]].level * 3 + 3:
                        self.map_graph[request[1]].upgrade()
                        if player_num == 1:
                            self.p1_score += 1
                        else:
                            self.p2_score += 1
                        return {'status_kode': 1}
                    else:
                        return {'status_kode': 104}
                else:
                    return {'status_kode': 103}
            else:
                return {'status_kode': 102}
        elif type(request) == tuple and request[0] == 'equip':
            if request[1] in self.map_graph.keys():
                if request[1] in p_villages:
                    if self.map_graph[request[1]].coins >= 2:
                        if len(self.map_graph[request[1]].units) < self.map_graph[request[1]].level + 1:
                            unit = self.map_graph[request[1]].equip()
                            self.units[unit.name] = unit  # Проверить, что names одинаково для всех деревень
                            p_units.add(unit.name)
                            return {'status_kode': 2}
                        else:
                            return {'status_kode': 105}
                    else:
                        return {'status_kode': 104}
                else:
                    return {'status_kode': 103}
            else:
                return {'status_kode': 102}
        else:
            return {'status_kode': 101}

    def process_day_change(self):
        for i in range(12):
            if self.map_graph['v' + str(i)].empire:
                self.map_graph['v' + str(i)].coins += 1 + self.map_graph['v' + str(i)].level
        print(self.process_request(2, 'report'))
        time.sleep(self.delay)

    def process_player(self, player):
        request = 'report'
        while request != 'end':
            response = self.process_request(player.number, request)
            request = player.move(response)
            print(request)
            time.sleep(self.delay)

    def report(self, p_villages, enemy_villages, p_units, enemy_units):
        p_villages_data = dict()
        enemy_villages_data = dict()
        p_units_data = dict()
        enemy_units_data = dict()
        for i in p_villages:
            p_villages_data[i] = {'level': self.map_graph[i].level, 'coins': self.map_graph[i].coins}
        for i in enemy_villages:
            enemy_villages_data[i] = {'level': self.map_graph[i].level}
        for i in p_units:
            p_units_data[i] = {'location': self.units[i].location, 'hp': self.units[i].hp, 'atk': self.units[i].atk, 'defense': self.units[i].defense}
        for i in enemy_units:
            enemy_units_data[i] = {'location': self.units[i].location, 'hp': self.units[i].hp, 'atk': self.units[i].atk, 'defense': self.units[i].defense}
        return {'status_kode': 0, 'p_villages': p_villages_data, 'enemy_villages': enemy_villages_data, 'p_units': p_units_data, 'enemy_units': enemy_units_data}

    def generate_map(self, width: int, height: int):
        self.map_graph = dict()
        for i in range(height):  # деревни
            for j in range(width):
                if i > 0:
                    u_road = 'r' + str(width - 1 + (2 * width - 1) * (i - 1) + j)
                else:
                    u_road = None
                if i < height - 1:
                    d_road = 'r' + str(width - 1 + (2 * width - 1) * i + j)
                else:
                    d_road = None
                if j > 0:
                    l_road = 'r' + str((2 * width - 1) * i + j - 1)
                else:
                    l_road = None
                if j < width - 1:
                    r_road = 'r' + str((2 * width - 1) * i + j)
                else:
                    r_road = None
                self.map_graph['v' + str(i * 4 + j)] = Village('v' + str(i * 4 + j), u_road, d_road, l_road, r_road)
        self.map_graph['v3'].empire = 2  # 'p2'
        self.map_graph['v8'].empire = 1  # 'p1'

        # дороги: что связывает
        for i in range(height):  # подогнать формулы под размеры
            for j in range(width - 1):
                connected_villages = {'v' + str(width * i + j), 'v' + str(width * i + j + 1)}
                self.map_graph['r' + str(i * 7 + j)] = Road(connected_villages)
            if i < height - 1:
                for j in range(width):
                    connected_villages = {'v' + str(width * i + j), 'v' + str(width * (i + 1) + j)}
                    self.map_graph['r' + str(i * 7 + 3 + j)] = Road(connected_villages)
        # дороги: параметры
        for i in range(9):  # подогнать формулы под размеры
            length = random.randint(1, 5)
            self.map_graph['r' + str(i)].length = length
            self.map_graph['r' + str(16 - i)].length = length
