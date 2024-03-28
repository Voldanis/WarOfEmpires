import random

from classes.server import Server
from bots.boss import Boss
from bots.bot import Bot


def identify_players():
    map_graph = dict()
    for i in server.map_graph.keys():
        if i[0] == 'r':
            map_graph[i] = {'length': server.map_graph[i].length, 'start_village': server.map_graph[i].start_village, 'finish_village': server.map_graph[i].finish_village}
        else:
            map_graph[i] = server.map_graph[i].roads
    if random.randint(0, 1) == 0:
        player1 = Boss(map_graph, 1)
        player2 = Bot(map_graph, 2)
    else:
        player1 = Bot(map_graph, 1)
        player2 = Boss(map_graph, 2)
    return player1, player2


random.seed(a=835995859)
server = Server()
p1, p2 = identify_players()
server.run(p1, p2)
