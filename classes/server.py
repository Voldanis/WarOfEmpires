import time
import random

from bots.bot import Bot
from classes.village import Village
from classes.road import Road


class Server:
    def __init__(self):
        self.width = 4
        self.height = 3
        self.map_graph = dict()
        self.generate_map()
        self.units = dict()
        self.delay = 0.1
        self.win_score = 90
        self.p1_villages = {'v8'}
        self.p1_units = set()
        self.p1_score = 1
        self.p2_villages = {'v3'}
        self.p2_units = set()
        self.p2_score = 1
        # коды
        self.code_report_ok = 0  # report ok
        self.code_upgrade_ok = 1  # upgrade ok
        self.code_equip_ok = 2  # equip ok
        self.code_move_ok = 3  # move ok
        self.codeer_wrong_command = 101  # неизвестная команда
        self.codeer_wrong_village = 102 # выбрана не принадлежащая игроку деревня
        self.codeer_no_money = 103  # недостаточно средств
        self.codeer_no_space = 104  # недостаточно места в городе
        self.codeer_wrong_unit = 105  # выбран не принадлежащий игроку юнит
        self.codeer_traveler = 106  # выбран уже посланный юнит
        self.codeer_unit_moved = 107 # юнит уже сделал ход/ только появился
        self.codeer_wrong_direction = 108  # из города, в котором находится юнит, нельзя пойти в данном направлении

    def generate_map(self):
        self.map_graph = dict()
        for i in range(self.height):  # деревни
            for j in range(self.width):
                roads = []
                if i > 0:
                    roads.append( 'r' + str(self.width - 1 + (2 * self.width - 1) * (i - 1) + j))
                if i < self.height - 1:
                    roads.append('r' + str(self.width - 1 + (2 * self.width - 1) * i + j))
                if j > 0:
                    roads.append('r' + str((2 * self.width - 1) * i + j - 1))
                if j < self.width - 1:
                    roads.append('r' + str((2 * self.width - 1) * i + j))
                self.map_graph['v' + str(i * 4 + j)] = Village('v' + str(i * 4 + j), roads)
        self.map_graph['v3'].empire = 2  # 'p2'
        self.map_graph['v8'].empire = 1  # 'p1'

        # дороги: что связывает
        for i in range(self.height):  # подогнать формулы под размеры
            for j in range(self.width - 1):
                self.map_graph['r' + str(i * 7 + j)] = Road('v' + str(self.width * i + j), 'v' + str(self.width * i + j + 1))
            if i < self.height - 1:
                for j in range(self.width):
                    self.map_graph['r' + str(i * 7 + 3 + j)] = Road('v' + str(self.width * i + j), 'v' + str(self.width * (i + 1) + j))
        # дороги: параметры
        for i in range(9):  # подогнать формулы под размеры
            length = random.randint(1, 5)
            self.map_graph['r' + str(i)].init_length(length)
            self.map_graph['r' + str(16 - i)].init_length(length)

    def run(self, p1, p2):

        while self.p1_score < self.win_score and self.p2_score < self.win_score:
            self.process_day_change()
            self.process_player(p1)
            self.process_player(p2)
        if self.p1_score == self.p2_score:
            print('draw!')
        if self.p1_score >= self.win_score:
            if type(p1) == Bot:
                print('player wins!')
                print('boss score:' + str(self.p2_score))
            else:
                print('boss wins!')
                print('player score:' + str(self.p2_score))
        else:
            if type(p2) == Bot:
                print('player wins!')
                print('boss score:' + str(self.p1_score))
            else:
                print('boss wins!')
                print('player score:' + str(self.p1_score))

    def process_day_change(self):
        for i in range(17):
            hard_segments = self.copy_2d_list(self.map_graph['r' + str(i)].segments)
            for segment in hard_segments:
                for unit in segment:
                    self.move(unit)
        for i in range(12):
            if self.map_graph['v' + str(i)].empire:
                self.map_graph['v' + str(i)].coins += 1 + self.map_graph['v' + str(i)].level
            for unit in self.map_graph['v' + str(i)].units: # сделать, чтоб когда приходили, не менялась is_moved
                if self.units[unit].finish_village is None:
                    if self.units[unit].is_moved:
                        self.units[unit].is_moved = False
                    elif self.units[unit].hp < self.units[unit].max_hp and self.units[unit].empire == self.map_graph['v' + str(i)].empire:
                        self.units[unit].hp += 2
                        if self.units[unit].hp > self.units[unit].max_hp:
                            self.units[unit].hp = self.units[unit].max_hp
                elif self.units[unit].finish_village == self.units[unit].location:
                    self.units[unit].finish_village = None
                else:
                    self.move(unit)
        print(self.process_request(2, 'report'))
        time.sleep(self.delay)

    def process_player(self, player):
        request = 'report'
        while request != 'end':
            response = self.process_request(player.number, request)
            request = player.move(response)
            print(request)
            time.sleep(self.delay)

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
            return self.report(self.code_report_ok, p_villages, enemy_villages, p_units, enemy_units)
        elif type(request) == tuple and request[0] == 'upgrade':
            if request[1] in p_villages:
                if self.map_graph[request[1]].coins >= self.map_graph[request[1]].level * 3 + 3:
                    self.map_graph[request[1]].upgrade()
                    if player_num == 1:
                        self.p1_score += 1
                    else:
                        self.p2_score += 1
                    return self.report(self.code_upgrade_ok, p_villages, enemy_villages, p_units, enemy_units)
                else:
                    return {'status_kode': self.codeer_no_money}
            else:
                return {'status_kode': self.codeer_wrong_village}
        elif type(request) == tuple and request[0] == 'equip':
            if request[1] in p_villages:
                if self.map_graph[request[1]].coins >= 2:
                    if len(self.map_graph[request[1]].units) < self.map_graph[request[1]].level + 1:
                        unit = self.map_graph[request[1]].equip()
                        self.units[unit.name] = unit
                        p_units.add(unit.name)
                        return self.report(self.code_equip_ok, p_villages, enemy_villages, p_units, enemy_units)
                    else:
                        return {'status_kode': self.codeer_no_space}
                else:
                    return {'status_kode': self.codeer_no_money}
            else:
                return {'status_kode': self.codeer_wrong_village}
        elif type(request) == tuple and request[0] == 'move':
            if request[1] in p_units:
                if self.units[request[1]].finish_village is None:
                    if not self.units[request[1]].is_moved:
                        if request[2] in self.map_graph[self.units[request[1]].location].roads:
                            if self.map_graph[request[2]].finish_village != self.units[request[1]].location:
                                self.units[request[1]].finish_village = self.map_graph[request[2]].finish_village
                            else:
                                self.units[request[1]].finish_village = self.map_graph[request[2]].start_village
                            self.move(request[1])
                            self.units[request[1]].is_moved = True
                            return self.report(self.code_move_ok, p_villages, enemy_villages, p_units, enemy_units)
                        else:
                            return {'status_kode': self.codeer_wrong_direction}
                    else:
                        return {'status_kode': self.codeer_unit_moved}
                else:
                    return {'status_kode': self.codeer_traveler}
            else:
                return {'status_kode': self.codeer_wrong_unit}
        else:
            return {'status_kode': self.codeer_wrong_command}

    def report(self, status_code, p_villages, enemy_villages, p_units, enemy_units):
        p_villages_data = dict()
        enemy_villages_data = dict()
        p_units_data = dict()
        enemy_units_data = dict()
        for i in p_villages:
            p_villages_data[i] = {'level': self.map_graph[i].level, 'coins': self.map_graph[i].coins}
        for i in enemy_villages:
            enemy_villages_data[i] = {'level': self.map_graph[i].level}
        for i in p_units:
            p_units_data[i] = {'location': self.units[i].location, 'max_hp': self.units[i].max_hp,  'hp': self.units[i].hp, 'atk': self.units[i].atk, 'defense': self.units[i].defense, 'is_moved': self.units[i].is_moved}
        for i in enemy_units:
            enemy_units_data[i] = {'location': self.units[i].location, 'hp': self.units[i].hp, 'atk': self.units[i].atk, 'defense': self.units[i].defense}
        return {'status_kode': status_code, 'p_villages': p_villages_data, 'enemy_villages': enemy_villages_data, 'p_units': p_units_data, 'enemy_units': enemy_units_data}

    def move(self, unit):
        if self.units[unit].location[0] == 'v':
            correct_road = None
            direction = None
            for road in self.map_graph[self.units[unit].location].roads:
                if self.map_graph[road].finish_village == self.units[unit].finish_village:
                    correct_road = road
                    direction = 0
                    break
                if self.map_graph[road].start_village == self.units[unit].finish_village:
                    correct_road = road
                    direction = -1
                    break
            self.map_graph[self.units[unit].location].units.remove(unit)
            self.map_graph[correct_road].segments[direction].append(unit)
            self.units[unit].location = correct_road
        else:
            if self.map_graph[self.units[unit].location].finish_village == self.units[unit].finish_village:
                direction = 1
            else:
                direction = -1
            pos = None
            for i in range(self.map_graph[self.units[unit].location].length):
                if unit in self.map_graph[self.units[unit].location].segments[i]:
                    pos = i
                    break
            if pos + direction < 0:
                if len(self.map_graph[self.units[unit].finish_village].units) <= self.map_graph[self.units[unit].finish_village].level:
                    self.map_graph[self.units[unit].location].segments[0].remove(unit)
                    self.map_graph[self.units[unit].finish_village].units.append(unit)
                    self.units[unit].location = self.units[unit].finish_village
            elif pos + direction >= self.map_graph[self.units[unit].location].length:
                if len(self.map_graph[self.units[unit].finish_village].units) <= self.map_graph[self.units[unit].finish_village].level:
                    self.map_graph[self.units[unit].location].segments[-1].remove(unit)
                    self.map_graph[self.units[unit].finish_village].units.append(unit)
                    self.units[unit].location = self.units[unit].finish_village
            else:
                self.map_graph[self.units[unit].location].segments[pos].remove(unit)
                self.map_graph[self.units[unit].location].segments[pos + direction].append(unit)
                # self.make_step(unit, direction)
                '''if len(self.map_graph[correct_road].segments[direction]) > 0 and self.units[self.map_graph[correct_road].segments[direction][0]].empire != self.units[unit].empire:
                    self.battle(unit, self.map_graph[correct_road].segments[direction][0])
                else:
                    self.make_step()'''

            '''def battle(self):
                pass
            def make_step(self, init, direction):
                index'''

    def copy_2d_list(self, d2list):
        new_list = []
        for mini_list in d2list:
            new_list.append(mini_list.copy())
        return new_list





