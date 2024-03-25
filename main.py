import random
import time

from boss import Boss
from bot import Bot

class State:
    def __init__(self, width, height):
        self.map_graph = generate_map(width, height)
        '''self.p1_villages = {'v8'}
        self.p2_villages = {'v3'}'''

    def output(self, player):
        p_villages = []
        enemy_villages = []
        if player == 1:
            p = 'p1'
            enemy = 'p2'
        else:
            p = 'p2'
            enemy = 'p1'
        for i in self.map_graph.keys():
            if i[0] == 'v':
                if self.map_graph[i].empire == p:
                    p_villages.append([i, self.map_graph[i].level, self.map_graph[i].coins])
                elif self.map_graph[i].empire == enemy:
                    enemy_villages.append([i, self.map_graph[i].level])
        return p_villages, enemy_villages


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
player1 = Boss()
player2 = Bot()
if random.randint(0, 1) == 1:
    player1, player2 = player2, player1


while True:
    for i in range(12):
        if state.map_graph['v' + str(i)].empire:
            state.map_graph['v' + str(i)].coins += 1 + state.map_graph['v' + str(i)].level
    print(state.output(2))
    time.sleep(1)

    p1_ans = None
    while p1_ans != 'end':
        p1_ans = player1.move()
        print(p1_ans)
        time.sleep(1)
    p2_ans = None
    while p2_ans != 'end':
        p2_ans = player2.move()
        print(p2_ans)
        time.sleep(1)



