import random
import time

from boss import Boss
from bot import Bot


class State:
    def __init__(self, width, height):
        self.map_graph = generate_map(width, height)
        self.p1_villages = {'v8'}
        self.p2_villages = {'v3'}

    def process_request(self, player_num, request):
        if player_num == 1:
            p_villages = self.p1_villages
            enemy_villages = self.p2_villages
        else:
            p_villages = self.p2_villages
            enemy_villages = self.p1_villages

        if request == 'report':
            return self.report(p_villages, enemy_villages)
        elif type(request) == tuple and request[0] == 'upgrade':
            if request[1] in self.map_graph.keys():
                if request[1] in p_villages:
                    if self.map_graph[request[1]].coins >= self.map_graph[request[1]].level * 2 + 2:
                        self.upgrade_village(request[1])
                        return {'status_kode': 10}
                    else:
                        return {'status_kode': 13}
                else:
                    return {'status_kode': 12}
            else:
                return {'status_kode': 11}
        else:
            return {'status_kode': 0}

    def process_day_change(self):
        for i in range(12):
            if self.map_graph['v' + str(i)].empire:
                self.map_graph['v' + str(i)].coins += 1 + self.map_graph['v' + str(i)].level
        print(self.process_request(2, 'report'))
        time.sleep(1)

    def process_player(self, player):
        request = 'report'
        while request != 'end':
            response = self.process_request(player.number, request)
            request = player.move(response)
            print(request)
            time.sleep(1)

    def upgrade_village(self, village):
        self.map_graph[village].coins -= (self.map_graph[village].level * 2 + 2)
        self.map_graph[village].level += 1

    def report(self, p_villages, enemy_villages):
        p_villages_data = dict()
        enemy_villages_data = dict()
        for i in p_villages:
            p_villages_data[i] = {'level': self.map_graph[i].level, 'coins': self.map_graph[i].coins}
        for i in enemy_villages:
            enemy_villages_data[i] = {'level': self.map_graph[i].level}
        return {'status_kode': 1, 'p_villages': p_villages_data, 'enemy_villages': enemy_villages_data}


class Village:
    def __init__(self, u_road, d_road, l_road, r_road):
        self.u_road = u_road
        self.d_road = d_road
        self.l_road = l_road
        self.r_road = r_road
        self.level = 1
        self.coins = 0
        self.empire = None
        #self.units = []

    def __str__(self):
        return self.r_road, self.d_road, self.l_road, self.r_road


class Road:
    def __init__(self, connected_villages: set):
        self.connected_villages = connected_villages
        self.length = 0

    def __str__(self):
        return self.connected_villages, self.length


def generate_map(width: int, height: int):
    map_graph = dict()
    for i in range(height): # деревни
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
            map_graph['v' + str(i * 4 + j)] = Village(u_road, d_road, l_road, r_road)
    map_graph['v3'].empire = 'p2'
    map_graph['v8'].empire = 'p1'
    # дороги: что связывает
    for i in range(height):  # подогнать формулы под размеры
        for j in range(width - 1):
            connected_villages = {'v' + str(width * i + j), 'v' + str(width * i + j + 1)}
            map_graph['r' + str(i * 7 + j)] = Road(connected_villages)
        if i < height - 1:
            for j in range(width):
                connected_villages = {'v' + str(width * i + j), 'v' + str(width * (i + 1) + j)}
                map_graph['r' + str(i * 7 + 3 + j)] = Road(connected_villages)
    # дороги: параметры
    for i in range(9):  # подогнать формулы под размеры
        length = random.randint(1, 5)
        map_graph['r' + str(i)].length = length
        map_graph['r' + str(16 - i)].length = length
    return map_graph


random.seed(a=835995859)
width = 4
height = 3
state = State(width, height)

roads = dict()
for i in state.map_graph.keys():
    if i[0] == 'r':
        roads[i] = state.map_graph[i].length
player1 = Boss(roads, 1)
player2 = Bot(roads, 2)
if random.randint(0, 1) == 1:
    player1, player2 = player2, player1
    player1.number = 1
    player2.number = 2


while True:
    state.process_day_change()
    state.process_player(player1)
    state.process_player(player2)






