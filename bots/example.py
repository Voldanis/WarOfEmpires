class Example:
    def __init__(self, roads, number):
        self.roads = roads
        self.number = number
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
коды состояний: in server
    
'''

