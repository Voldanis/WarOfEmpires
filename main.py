import random

from classes.server import Server
from bots.boss import Boss
from bots.bot import Bot


def identify_players():
    roads = dict()
    for i in server.map_graph.keys():
        if i[0] == 'r':
            roads[i] = server.map_graph[i].length
    if random.randint(0, 1) == 0:
        player1 = Boss(roads, 1)
        player2 = Bot(roads, 2)
    else:
        player1 = Bot(roads, 1)
        player2 = Boss(roads, 2)
    return player1, player2


random.seed(a=835995859)
width = 4
height = 3
server = Server(width, height)
p1, p2 = identify_players()
server.run(p1, p2)
