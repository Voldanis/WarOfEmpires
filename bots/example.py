class Example:
    def __init__(self, roads, number):
        self.roads = roads
        self.number = number

    def move(self, response: dict):
        return 'end'

'''
команды:
'report' - получить отчет о состоянии поля
'end' - конец вашего хода
'upgrade', 'v{number]'  - улучшить деревню. number - номер деревни
'equip', {village} - экипировать воина. village - имя деревни
коды состояний:
    0 - report ok
    1 - upgrade ok
    2 - equip ok
    101 - неизвестная команда 
    102 - выбрана несуществующая деревня
    103 - выбрана не принадлежащая игроку деревня
    104 - недостаточно средств
    105 - недостаточно места в городе
'''

