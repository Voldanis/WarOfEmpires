import random


class Village:
    def __init__(self, u_road, d_road, l_road, r_road):
        self.u_road = u_road
        self.d_road = d_road
        self.l_road = l_road
        self.r_road = r_road

    def __str__(self):
        return self.r_road, self.d_road, self.l_road, self.r_road


class Road:
    def __init__(self, connected_villages: set):
        self.connected_villages = connected_villages
        self.length = 0

    def __str__(self):
        return self.connected_villages, self.length


random.seed(a=835995859)
map = dict()
width = 4
height = 3

for i in range(height):
    for j in range(width):
        if i > 0:
            u_road = 'r' +  str(width - 1 + (2 * width - 1) * (i - 1) + j)
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
        map['v' + str(i * 4 + j)] = Village(u_road, d_road, l_road, r_road)

for i in range(height): # подогнать формулы под размеры
    for j in range(width - 1):
        connected_villages = {'v' + str(width * i + j), 'v' + str(width * i + j + 1)}
        map['r' + str(i * 7 + j)] = Road(connected_villages)
    if i < height - 1:
        for j in range(width):
            connected_villages = {'v' + str(width * i + j), 'v' + str(width * (i + 1) +j)}
            map['r' + str(i * 7 + 3 + j)] = Road(connected_villages)
for i in range(9): # подогнать формулы под размеры
    length = random.randint(1, 5)
    map['r' + str(i)].length = length
    map['r' + str(16 - i)].length = length
