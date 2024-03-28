class Example:
    def __init__(self, map_graph):
        self.map_graph = map_graph
        self.response = None

    def move(self, response: dict):
        if response['status_kode'] == 0:
            self.response = response
        return 'end'

'''
команды:
    'report' - получить отчет о состоянии поля
    'end' - конец вашего хода
    'upgrade', {village}  - улучшить деревню. village - имя деревни
    'equip', {village} - экипировать воина. village - имя деревни
    'move', {unit}, {road} - отправить юнита по одному из направлений. unit - имя юнита. road - имя дороги
коды состояний:
    0  # report ok
    1  # upgrade ok
    2  # equip ok
    3  # move ok
    100  # неизвестная команда
    101 # выбрана не принадлежащая игроку деревня
    102  # недостаточно средств
    103  # недостаточно места в городе
    104  # выбран не принадлежащий игроку юнит
    105 # юнит уже сделал ход/ только появился
    106  # из города, в котором находится юнит, нельзя пойти в данном направлении
'''

