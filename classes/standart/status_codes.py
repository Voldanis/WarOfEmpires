from enum import Enum


class StatusCodes(Enum):
    report_ok = 0
    upgrade_ok = 1
    equip_ok = 2
    move_ok = 3
    capture_ok = 4
    increase_ok = 5
    wrong_command = 100  # неизвестная команда
    wrong_town = 101  # выбрана не принадлежащий игроку город
    no_money = 102  # недостаточно средств
    no_space = 103  # недостаточно места в городе
    invaders = 104  # в городе захватчики
    unit_already_exist = 105  # юнит с таким именем уже существует
    wrong_unit = 106  # выбран не принадлежащий игроку юнит
    unit_moved = 107  # юнит уже сделал ход/ только появился
    wrong_direction = 108  # из города, в котором находится юнит, нельзя пойти в данном направлении
    traveler = 109  # юнит находится не в городе
    in_homeland = 110   # юнит находится в дружественном городе
    in_abroad = 111  # юнит находится во вражеском городе
    bad_money = 112  # Указано неправильное денежное значение
    wrong_characteristic = 113  # выбрана неправильная характеристика
