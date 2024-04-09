import time
import random
import multiprocessing

from bots.boss import Boss
from bots.bot import Bot
from classes.town import Town
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
                      'wrong_command': 100, 'wrong_town': 101, 'no_money': 102, 'no_space': 103, 'invaders': 104,
                      'wrong_unit': 105, 'unit_moved': 106, 'wrong_direction': 107, 'traveler': 108, 'in_homeland': 109,
                      'not_in_homeland': 110, 'bad_money': 111, 'wrong_characteristic': 112}
        self.win_score = 600000
        self.p1 = None
        self.p2 = None
        self.identify_players()

    def generate_map(self):
        self.map_graph = dict()
        for i in range(self.height):  # города
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
                self.map_graph['t' + str(i * 4 + j)] = Town('t' + str(i * 4 + j), roads)
        self.map_graph['t3'].empire = 2
        self.map_graph['t8'].empire = 1
        # дороги: что связывает
        for i in range(self.height):  # подогнать формулы под размеры
            for j in range(self.width - 1):
                self.map_graph['r' + str(i * 7 + j)] = Road('t' + str(self.width * i + j),
                                                            't' + str(self.width * i + j + 1))
            if i < self.height - 1:
                for j in range(self.width):
                    self.map_graph['r' + str(i * 7 + 3 + j)] = Road('t' + str(self.width * i + j),
                                                                    't' + str(self.width * (i + 1) + j))
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
                                'start_town': self.map_graph[i].start_town,
                                'finish_town': self.map_graph[i].finish_town}
            else:
                map_graph[i] = self.map_graph[i].roads
        if random.randint(0, 1) == 0:
            self.p1 = Player(Boss(map_graph), 1, {'t8'})
            self.p2 = Player(Bot(map_graph), 2, {'t3'})
        else:
            self.p1 = Player(Bot(map_graph), 1, {'t8'})
            self.p2 = Player(Boss(map_graph), 2, {'t3'})

    def run(self):
        day = 0
        score1 = 0
        score2 = 0
        while score1 < self.win_score and score2 < self.win_score and day < 100:
            print('--------------------------')
            print('day', day)
            self.process_player(self.p1, self.p2)
            self.process_player(self.p2, self.p1)
            day += 1
            score1 = 0
            for t in self.p1.towns:
                score1 += self.map_graph[t].coins
                score1 += self.map_graph[t].level * 10000
            score2 = 0
            for t in self.p2.towns:
                score2 += self.map_graph[t].coins
                score2 += self.map_graph[t].level * 10000

        if score1 > score2:
            print(self.p1.bot.name, 'wins!')
        elif score1 < score2:
            print(self.p2.bot.name, 'wins!')
        else:
            print('draw!')
        print(self.p1.bot.name, 'score:', score1)
        print(self.p2.bot.name, 'score:', score2)

    def process_player(self, client, enemy):
        self.process_beginning_move(client)
        client_requests = []
        try:
            manager = multiprocessing.Manager()
            return_val = manager.dict()
            p = multiprocessing.Process(target=self.get_client_requests, args=(client, enemy, return_val))
            p.start()
            p.join(0.5)
            if p.is_alive():
                p.kill()
                text = client.bot.name + ' are too slow'
                raise TimeoutError(text)
            else:
                client_requests = return_val['requests']
        except TimeoutError as ter:
            print(ter)
        except Exception as what:
            print(what)
        for req in client_requests:
            print(req)
            resp = self.process_request(client, enemy, req)
            print(resp['status_code'])
            time.sleep(self.delay)

    def process_beginning_move(self, client):
        for town in self.map_graph.keys():
            if town[0] == 't':
                if town in client.towns:
                    self.map_graph[town].coins += 1 + self.map_graph[town].level
                    for unit in self.map_graph[town].units:
                        if self.units[unit].finish_town is None:
                            if self.units[unit].is_moved:
                                self.units[unit].is_moved = False
                            elif self.units[unit].hp < self.units[unit].max_hp:
                                self.units[unit].hp += 2
                                if self.units[unit].hp > self.units[unit].max_hp:
                                    self.units[unit].hp = self.units[unit].max_hp
                else:
                    for unit in self.map_graph[town].units:
                        if self.units[unit].finish_town is None and self.units[unit].empire == client.empire:
                            if self.units[unit].is_moved:
                                self.units[unit].is_moved = False

        fixed_queue = client.units_queue.copy()
        for unit in fixed_queue:
            self.move(unit)
        print('--------------------------')
        time.sleep(self.delay)

    def get_client_requests(self, client, enemy, return_val):
        report = self.report(self.codes['report_ok'], client, enemy)
        return_val['requests'] = client.bot.move(report)

    def process_request(self, client, enemy, request):
        if request == 'report':
            return self.report(self.codes['report_ok'], client, enemy)
        elif type(request) == tuple and len(request) > 1:
            if request[0] == 'upgrade':
                if request[1] in client.towns:
                    if self.map_graph[request[1]].coins >= round((self.map_graph[request[1]].level + 1)
                                                                 * ((5 + self.map_graph[request[1]].level) / 3)):
                        self.map_graph[request[1]].upgrade()
                        return {'status_code': self.codes['upgrade_ok']}
                    else:
                        return {'status_code': self.codes['no_money']}
                else:
                    return {'status_code': self.codes['wrong_town']}
            elif request[0] == 'equip':
                if request[1] in client.towns:
                    if len(self.map_graph[request[1]].units) < 1 or self.units[
                            self.map_graph[request[1]].units[0]].empire == self.map_graph[request[1]].empire:
                        if self.map_graph[request[1]].coins >= 2:
                            if len(self.map_graph[request[1]].units) <= self.map_graph[request[1]].level:
                                unit = self.map_graph[request[1]].equip()
                                self.units[unit.name] = unit
                                client.units.add(unit.name)
                                return {'status_code': self.codes['equip_ok']}
                            else:
                                return {'status_code': self.codes['no_space']}
                        else:
                            return {'status_code': self.codes['no_money']}
                    else:
                        return {'status_code': self.codes['invaders']}
                else:
                    return {'status_code': self.codes['wrong_town']}
            elif request[0] == 'move' and len(request) == 3:
                if request[1] in client.units:
                    if not self.units[request[1]].is_moved:
                        if request[2] in self.map_graph[self.units[request[1]].location].roads:
                            if self.map_graph[request[2]].finish_town != self.units[request[1]].location:
                                self.units[request[1]].finish_town = self.map_graph[request[2]].finish_town
                            else:
                                self.units[request[1]].finish_town = self.map_graph[request[2]].start_town
                            self.move(request[1])
                            self.units[request[1]].is_moved = True
                            client.units_queue.append(request[1])
                            return {'status_code': self.codes['move_ok']}
                        else:
                            return {'status_code': self.codes['wrong_direction']}
                    else:
                        return {'status_code': self.codes['unit_moved']}
                else:
                    return {'status_code': self.codes['wrong_unit']}
            elif request[0] == 'capture':
                if request[1] in client.units:
                    if not self.units[request[1]].is_moved:
                        if self.units[request[1]].location[0] == 't':
                            if self.units[request[1]].location not in client.towns:
                                # отбираем
                                if self.units[request[1]].location in enemy.towns:
                                    enemy.towns.discard(self.units[request[1]].location)
                                # добавляем
                                self.map_graph[self.units[request[1]].location].empire = self.units[request[1]].empire
                                client.towns.add(self.units[request[1]].location)
                                self.units[request[1]].is_moved = True
                                return {'status_code': self.codes['capture_ok']}
                            else:
                                return {'status_code': self.codes['in_homeland']}
                        else:
                            return {'status_code': self.codes['traveler']}
                    else:
                        return {'status_code': self.codes['unit_moved']}
                else:
                    return {'status_code': self.codes['wrong_unit']}
            elif request[0] == 'increase' and len(request) == 4:
                if request[1] in client.units:
                    if self.units[request[1]].location[0] == 't':
                        if self.units[request[1]].location in client.towns:
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
                                        return {'status_code': self.codes['wrong_characteristic']}
                                    return {'status_code': self.codes['increase_ok']}
                                else:
                                    return {'status_code': self.codes['no_money']}
                            else:
                                return {'status_code': self.codes['bad_money']}
                        else:
                            return {'status_code': self.codes['not_in_homeland']}
                    else:
                        return {'status_code': self.codes['traveler']}
                else:
                    return {'status_code': self.codes['wrong_unit']}
            else:
                return {'status_code': self.codes['wrong_command']}
        else:
            return {'status_code': self.codes['wrong_command']}

    def report(self, status_code, client, enemy):
        client_towns_data = dict()
        enemy_towns_data = dict()
        client_units_data = dict()
        enemy_units_data = dict()
        for i in client.towns:
            client_towns_data[i] = {'level': self.map_graph[i].level, 'coins': self.map_graph[i].coins}
        for i in enemy.towns:
            enemy_towns_data[i] = {'level': self.map_graph[i].level}
        for i in client.units:
            client_units_data[i] = {'location': self.units[i].location, 'max_hp': self.units[i].max_hp,
                                    'hp': self.units[i].hp, 'atk': self.units[i].atk, 'defense': self.units[i].defense,
                                    'is_moved': self.units[i].is_moved}
            if self.units[i].location[0] == 'r':
                client_units_data[i]['finish_town'] = self.units[i].finish_town
                for segment in range(self.map_graph[self.units[i].location].length):
                    if i in self.map_graph[self.units[i].location].segments[segment]:
                        client_units_data[i]['segment'] = segment
                        break
        for i in enemy.units:
            enemy_units_data[i] = {'location': self.units[i].location, 'hp': self.units[i].hp, 'atk': self.units[i].atk,
                                   'defense': self.units[i].defense}
            if self.units[i].location[0] == 'r':
                enemy_units_data[i]['finish_town'] = self.units[i].finish_town
                for segment in range(self.map_graph[self.units[i].location].length):
                    if i in self.map_graph[self.units[i].location].segments[segment]:
                        enemy_units_data[i]['segment'] = segment
                        break
        return {'status_code': status_code, 'player_towns': client_towns_data, 'enemy_towns': enemy_towns_data,
                'player_units': client_units_data, 'enemy_units': enemy_units_data}

    def move(self, unit):
        if self.units[unit].location[0] == 't':
            correct_road = None
            direction = None
            for road in self.map_graph[self.units[unit].location].roads:
                if self.map_graph[road].finish_town == self.units[unit].finish_town:
                    correct_road = road
                    direction = 0
                    break
                if self.map_graph[road].start_town == self.units[unit].finish_town:
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
            if self.map_graph[self.units[unit].location].finish_town == self.units[unit].finish_town:
                direction = 1
            else:
                direction = -1
            pos = None
            for i in range(self.map_graph[self.units[unit].location].length):
                if unit in self.map_graph[self.units[unit].location].segments[i]:
                    pos = i
                    break
            if pos + direction < 0 or pos + direction >= self.map_graph[self.units[unit].location].length:
                if len(self.map_graph[self.units[unit].finish_town].units) > 0 and self.units[
                        self.map_graph[self.units[unit].finish_town].units[0]].empire != self.units[unit].empire:
                    self.battle(unit, self.map_graph[self.units[unit].finish_town].units[0])
                elif len(self.map_graph[self.units[unit].finish_town].units) <= self.map_graph[
                        self.units[unit].finish_town].level:
                    self.map_graph[self.units[unit].location].segments[pos].remove(unit)
                    self.map_graph[self.units[unit].finish_town].units.append(unit)
                    self.units[unit].location = self.units[unit].finish_town
                    self.units[unit].finish_town = None
                    if unit in self.p1.units_queue:
                        self.p1.units_queue.remove(unit)
                    else:
                        self.p2.units_queue.remove(unit)
            else:
                if len(self.map_graph[self.units[unit].location].segments[pos + direction]) > 0 and \
                        self.units[self.map_graph[self.units[unit].location].segments[pos + direction][0]].empire != \
                        self.units[unit].empire:
                    return self.battle(unit, self.map_graph[self.units[unit].location].segments[pos + direction][
                        0]), direction
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
        if self.units[target].location[0] == 't':
            self.map_graph[self.units[target].location].units.remove(target)
        else:
            i = 0
            while target not in self.map_graph[self.units[target].location].segments[i]:
                i += 1
            self.map_graph[self.units[target].location].segments[i].remove(target)
        if self.units[target].empire == 1:
            self.p1.units.remove(target)
            if target in self.p1.units_queue:
                self.p1.units_queue.remove(target)
        else:
            self.p2.units.remove(target)
            if target in self.p2.units_queue:
                self.p2.units_queue.remove(target)
        Town.used_names.remove(target)
        Town.names.append(target)
        del self.units[target]

        return target


if __name__ == "__main__":
    random.seed(a=835995859)
    server = Server()
    server.run()
