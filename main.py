import time
import random

from bots.boss import Boss
from bots.bot import Bot
from classes.village import Village
from classes.road import Road
from classes.player import Player


class Server:
    def __init__(self):
        self.width = 4
        self.height = 3
        self.delay = 0
        self.map_graph = dict()
        self.generate_map()
        self.units = dict()
        self.codes = {'report_ok': 0, 'upgrade_ok': 1, 'equip_ok': 2, 'move_ok': 3, 'capture_ok': 4, 'increase_ok': 5,
                      'wrong_command': 100, 'wrong_village': 101, 'no_money': 102, 'no_space': 103, 'invaders': 104,
                      'wrong_unit': 105, 'unit_moved': 106, 'wrong_direction': 107, 'traveler': 108, 'in_homeland': 109,
                      'not_in_homeland': 110, 'bad_money': 111, 'wrong_characteristic': 112}
        self.win_score = 600000
        self.p1 = None
        self.p2 = None
        self.identify_players()

    def generate_map(self):
        self.map_graph = dict()
        for i in range(self.height):  # деревни
            for j in range(self.width):
                roads = []
                if i > 0:
                    roads.append('r' + str(self.width - 1 + (2 * self.width - 1) * (i - 1) + j))
                if i < self.height - 1:
                    roads.append('r' + str(self.width - 1 + (2 * self.width - 1) * i + j))
                if j > 0:
                    roads.append('r' + str((2 * self.width - 1) * i + j - 1))
                if j < self.width - 1:
                    roads.append('r' + str((2 * self.width - 1) * i + j))
                self.map_graph['v' + str(i * 4 + j)] = Village('v' + str(i * 4 + j), roads)
        self.map_graph['v3'].empire = 2
        self.map_graph['v8'].empire = 1
        # дороги: что связывает
        for i in range(self.height):  # подогнать формулы под размеры
            for j in range(self.width - 1):
                self.map_graph['r' + str(i * 7 + j)] = Road('v' + str(self.width * i + j),
                                                            'v' + str(self.width * i + j + 1))
            if i < self.height - 1:
                for j in range(self.width):
                    self.map_graph['r' + str(i * 7 + 3 + j)] = Road('v' + str(self.width * i + j),
                                                                    'v' + str(self.width * (i + 1) + j))
        # дороги: параметры
        for i in range(9):  # подогнать формулы под размеры
            length = random.randint(1, 5)
            self.map_graph['r' + str(i)].init_length(length)
            self.map_graph['r' + str(16 - i)].init_length(length)

    def identify_players(self):
        map_graph = dict()
        for i in self.map_graph.keys():
            if i[0] == 'r':
                map_graph[i] = {'length': self.map_graph[i].length,
                                'start_village': self.map_graph[i].start_village,
                                'finish_village': self.map_graph[i].finish_village}
            else:
                map_graph[i] = self.map_graph[i].roads
        if random.randint(0, 1) == 0:
            self.p1 = Player(Boss(map_graph), 1, {'v8'})
            self.p2 = Player(Bot(map_graph), 2, {'v3'})
        else:
            self.p1 = Player(Bot(map_graph), 1, {'v8'})
            self.p2 = Player(Boss(map_graph), 2, {'v3'})

    def run(self):
        day = 0
        score1 = 0
        score2 = 0
        while score1 < self.win_score and score2 < self.win_score and day < 100:
            self.process_day_change()
            self.process_player(self.p1, self.p2)
            self.process_player(self.p2, self.p1)
            day += 1
            score1 = 0
            for v in self.p1.villages:
                score1 += self.map_graph[v].coins
                score1 += self.map_graph[v].level * 10000
            score2 = 0
            for v in self.p2.villages:
                score2 += self.map_graph[v].coins
                score2 += self.map_graph[v].level * 10000

        if score1 > score2:
            print(self.p1.bot.name, 'wins!')
            print('p1 score:', score1, 'p2 score:', score2)
        elif score1 < score2:
            print(self.p2.bot.name, 'wins!')
            print('p1 score:', score1, 'p2 score:', score2)
        else:
            print('draw!')
            print('p1 score:', score1, 'p2 score:', score2)

    def process_day_change(self):
        for i in range(17):
            hard_segments = self.map_graph['r' + str(i)].copy_segments()
            for j in range(self.map_graph['r' + str(i)].length):
                for unit in hard_segments[j]:
                    victim, direction = self.move(unit)
                    if victim and victim in hard_segments[j + direction]:
                        hard_segments[j + direction].remove(victim)
        for i in range(12):
            if self.map_graph['v' + str(i)].empire:
                self.map_graph['v' + str(i)].coins += 1 + self.map_graph['v' + str(i)].level
            for unit in self.map_graph['v' + str(i)].units:
                if self.units[unit].finish_village is None:
                    if self.units[unit].is_moved:
                        self.units[unit].is_moved = False
                    elif self.units[unit].hp < self.units[unit].max_hp and self.units[unit].empire == self.map_graph[
                        'v' + str(i)].empire:
                        self.units[unit].hp += 2
                        if self.units[unit].hp > self.units[unit].max_hp:
                            self.units[unit].hp = self.units[unit].max_hp
                elif self.units[unit].finish_village == self.units[unit].location:
                    self.units[unit].finish_village = None
                else:
                    self.move(unit)
        print(self.process_request(self.p2, self.p1, 'report'))
        time.sleep(self.delay)

    def process_player(self, client, enemy):
        request = 'report'
        while request != 'end':
            response = self.process_request(client, enemy, request)
            request = client.bot.move(response)
            print(request)
            time.sleep(self.delay)

    def process_request(self, client, enemy, request):
        if request == 'report':
            return self.report(self.codes['report_ok'], client, enemy)
        elif type(request) == tuple and len(request) > 1:
            if request[0] == 'upgrade':
                if request[1] in client.villages:
                    if self.map_graph[request[1]].coins >= round((self.map_graph[request[1]].level + 1)
                                                                 * ((5 + self.map_graph[request[1]].level) / 3)):
                        self.map_graph[request[1]].upgrade()
                        return self.report(self.codes['upgrade_ok'], client, enemy)
                    else:
                        return {'status_kode': self.codes['no_money']}
                else:
                    return {'status_kode': self.codes['wrong_village']}
            elif request[0] == 'equip':
                if request[1] in client.villages:
                    if len(self.map_graph[request[1]].units) < 1 or self.units[self.map_graph[request[1]].units[0]].empire == self.map_graph[request[1]].empire:
                        if self.map_graph[request[1]].coins >= 2:
                            if len(self.map_graph[request[1]].units) <= self.map_graph[request[1]].level:
                                unit = self.map_graph[request[1]].equip()
                                self.units[unit.name] = unit
                                client.units.add(unit.name)
                                return self.report(self.codes['equip_ok'], client, enemy)
                            else:
                                return {'status_kode': self.codes['no_space']}
                        else:
                            return {'status_kode': self.codes['no_money']}
                    else:
                        return {'status_kode': self.codes['invaders']}
                else:
                    return {'status_kode': self.codes['wrong_village']}
            elif request[0] == 'move' and len(request) == 3:
                if request[1] in client.units:
                    if not self.units[request[1]].is_moved:
                        if request[2] in self.map_graph[self.units[request[1]].location].roads:
                            if self.map_graph[request[2]].finish_village != self.units[request[1]].location:
                                self.units[request[1]].finish_village = self.map_graph[request[2]].finish_village
                            else:
                                self.units[request[1]].finish_village = self.map_graph[request[2]].start_village
                            self.move(request[1])
                            self.units[request[1]].is_moved = True
                            return self.report(self.codes['move_ok'], client, enemy)
                        else:
                            return {'status_kode': self.codes['wrong_direction']}
                    else:
                        return {'status_kode': self.codes['unit_moved']}
                else:
                    return {'status_kode': self.codes['wrong_unit']}
            elif request[0] == 'capture':
                if request[1] in client.units:
                    if not self.units[request[1]].is_moved:
                        if self.units[request[1]].location[0] == 'v':
                            if self.units[request[1]].location not in client.villages:
                                # отбираем
                                if self.units[request[1]].location in enemy.villages:
                                    enemy.villages.discard(self.units[request[1]].location)
                                # добавляем
                                self.map_graph[self.units[request[1]].location].empire = self.units[request[1]].empire
                                client.villages.add(self.units[request[1]].location)
                                self.units[request[1]].is_moved = True
                                return self.report(self.codes['capture_ok'], client, enemy)
                            else:
                                return {'status_kode': self.codes['in_homeland']}
                        else:
                            return {'status_kode': self.codes['traveler']}
                    else:
                        return {'status_kode': self.codes['unit_moved']}
                else:
                    return {'status_kode': self.codes['wrong_unit']}
            elif request[0] == 'increase' and len(request) == 4 :
                if request[1] in client.units:
                    if self.units[request[1]].location[0] == 'v':
                        if self.units[request[1]].location in client.villages:
                            if type(request[3]) == int and request[3] > 0:
                                if request[3] <= self.map_graph[self.units[request[1]].location].coins:
                                    if request[2] == 'atk':
                                        self.units[request[1]].atk += request[3]
                                        self.map_graph[self.units[request[1]].location].coins -= request[3]
                                    elif request[2] == 'def':
                                        self.units[request[1]].defense += request[3]
                                        self.map_graph[self.units[request[1]].location].coins -= request[3]
                                    elif request[2] == 'max_hp':
                                        self.units[request[1]].max_hp += request[3] * 4
                                        self.map_graph[self.units[request[1]].location].coins -= request[3]
                                    elif request[2] == 'heal':
                                        self.units[request[1]].hp += request[3] * 4
                                        if self.units[request[1]].hp > self.units[request[1]].max_hp:
                                            self.units[request[1]].hp = self.units[request[1]].max_hp
                                        self.map_graph[self.units[request[1]].location].coins -= request[3]
                                    else:
                                        return {'status_kode': self.codes['wrong_characteristic']}
                                    return self.report(self.codes['increase_ok'], client, enemy)
                                else:
                                    return {'status_kode': self.codes['no_money']}
                            else:
                                return {'status_kode': self.codes['bad_money']}
                        else:
                            return {'status_kode': self.codes['not_in_homeland']}
                    else:
                        return {'status_kode': self.codes['traveler']}
                else:
                    return {'status_kode': self.codes['wrong_unit']}
            else:
                return {'status_kode': self.codes['wrong_command']}
        else:
            return {'status_kode': self.codes['wrong_command']}

    def report(self, status_code, client, enemy):
        p_villages_data = dict()
        enemy_villages_data = dict()
        p_units_data = dict()
        enemy_units_data = dict()
        for i in client.villages:
            p_villages_data[i] = {'level': self.map_graph[i].level, 'coins': self.map_graph[i].coins}
        for i in enemy.villages:
            enemy_villages_data[i] = {'level': self.map_graph[i].level}
        for i in client.units:
            p_units_data[i] = {'location': self.units[i].location, 'max_hp': self.units[i].max_hp,
                               'hp': self.units[i].hp, 'atk': self.units[i].atk, 'defense': self.units[i].defense,
                               'is_moved': self.units[i].is_moved}
        for i in enemy.units:
            enemy_units_data[i] = {'location': self.units[i].location, 'hp': self.units[i].hp, 'atk': self.units[i].atk,
                                   'defense': self.units[i].defense}
        return {'status_kode': status_code, 'p_villages': p_villages_data, 'enemy_villages': enemy_villages_data,
                'p_units': p_units_data, 'enemy_units': enemy_units_data}

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
            if len(self.map_graph[correct_road].segments[direction]) > 0 and self.units[
                    self.map_graph[correct_road].segments[direction][0]].empire != self.units[unit].empire:
                self.battle(unit, self.map_graph[correct_road].segments[direction][0])
            else:
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
            if pos + direction < 0 or pos + direction >= self.map_graph[self.units[unit].location].length:
                if len(self.map_graph[self.units[unit].finish_village].units) > 0 and self.units[self.map_graph[self.units[unit].finish_village].units[0]].empire != self.units[unit].empire:
                    self.battle(unit, self.map_graph[self.units[unit].finish_village].units[0])
                elif len(self.map_graph[self.units[unit].finish_village].units) <= self.map_graph[
                        self.units[unit].finish_village].level:
                    self.map_graph[self.units[unit].location].segments[pos].remove(unit)
                    self.map_graph[self.units[unit].finish_village].units.append(unit)
                    self.units[unit].location = self.units[unit].finish_village
            else:
                if len(self.map_graph[self.units[unit].location].segments[pos + direction]) > 0 and \
                        self.units[self.map_graph[self.units[unit].location].segments[pos + direction][0]].empire != self.units[unit].empire:
                    return self.battle(unit, self.map_graph[self.units[unit].location].segments[pos + direction][0]), direction
                else:
                    self.map_graph[self.units[unit].location].segments[pos].remove(unit)
                    self.map_graph[self.units[unit].location].segments[pos + direction].append(unit)
        return None, 0

    def battle(self, attacker, target):
        dmg = self.units[attacker].atk - self.units[target].defense
        if dmg < 1:
            dmg = 1
        if self.units[target].hp - dmg <= 0:
            return self.annihilation(target)
        else:
            self.units[target].hp -= dmg
        return None

    def annihilation(self, target):
        if self.units[target].location[0] == 'v':
            self.map_graph[self.units[target].location].units.remove(target)
        else:
            i = 0
            while target not in self.map_graph[self.units[target].location].segments[i]:
                i += 1
            self.map_graph[self.units[target].location].segments[i].remove(target)
        if self.units[target].empire == 1:
            self.p1.units.remove(target)
        else:
            self.p2.units.remove(target)
        Village.used_names.remove(target)
        Village.names.append(target)
        del self.units[target]
        return target


random.seed(a=835995859)
server = Server()
server.run()


