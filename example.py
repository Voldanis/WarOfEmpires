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
'upgrade', 'v{number]'  - улучшить деревню, number - номер деревни
коды состояний:
    0 - неизвестная команда
    report:
    1 - ок. Содержит отчет об изменениях состояния
    upgrade:
    10 - ок
    11 - выбрана несуществующая деревня
    12 - выбрана не принадлежащая игроку деревня
    13 - недостаточно средств
    
'''

