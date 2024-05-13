from classes.reports.town_data import TownData
from classes.reports.unit_data import UnitData


class Server:
    def __init__(self):
        self.width = 4
        self.height = 3
        self.delay = 0
        self.map_graph = dict()
        self.generate_map()
        self.units = dict()
        self.codes = {'report_ok': 0, 'upgrade_ok': 1, 'equip_ok': 2, 'move_ok': 3, 'capture_ok': 4, 'increase_ok': 5,
                      'wrong_command': 100, 'wrong_town': 101, 'no_money': 102, 'no_space': 103, 'invaders': 104,
                      'wrong_unit': 105, 'unit_moved': 106, 'wrong_direction': 107, 'traveler': 108, 'in_homeland': 109,
                      'not_in_homeland': 110, 'bad_money': 111, 'wrong_characteristic': 112, 'unit_already_exist': 113}
        self.win_score = 600000
        self.p1 = None
        self.p2 = None
        self.day = 0
        self.score1 = 0
        self.score2 = 0
        self.identify_players()
        manager = multiprocessing.Manager()
        self.requests = manager.dict()
        self.requests['requests'] = []

    def generate_map(self):
        self.map_graph = dict()
        for i in range(self.height):  # города
            for j in range(self.width):
                roads = []
                if i > 0:
                    roads.append('r' + str(self.width - 1 + (2 * self.width - 1) * (i - 1) + j))
                if i < self.height - 1:
                    roads.append('r' + str(self.width - 1 + (2 * self.width - 1) * i + j))
                if j > 0:
                    roads.append('r' + str((2 * self.width - 1) * i + j - 1))
                if j < self.width - 1:
                    roads.append('r' + str((2 * self.width - 1) * i + j))
                self.map_graph['t' + str(i * 4 + j)] = Town('t' + str(i * 4 + j), roads)
        self.map_graph['t3'].empire = 2
        self.map_graph['t8'].empire = 1
        # дороги: что связывает
        for i in range(self.height):  # подогнать формулы под размеры
            for j in range(self.width - 1):
                self.map_graph['r' + str(i * 7 + j)] = Road('t' + str(self.width * i + j),
                                                            't' + str(self.width * i + j + 1))
            if i < self.height - 1:
                for j in range(self.width):
                    self.map_graph['r' + str(i * 7 + 3 + j)] = Road('t' + str(self.width * i + j),
                                                                    't' + str(self.width * (i + 1) + j))
        # дороги: параметры
        for i in range(9):  # подогнать формулы под размеры
            length = random.randint(1, 5)
            self.map_graph['r' + str(i)].init_length(length)
            self.map_graph['r' + str(16 - i)].init_length(length)

    def identify_players(self):
        map_graph = dict()
        for i in self.map_graph.keys():
            if i[0] == 'r':
                map_graph[i] = {'length': self.map_graph[i].length,
                                'start_town': self.map_graph[i].start_town,
                                'finish_town': self.map_graph[i].finish_town}
            else:
                map_graph[i] = self.map_graph[i].roads
        if random.randint(0, 1) == 0:
            self.p1 = Player(Boss(map_graph), 1, {'t8'})
            self.p2 = Player(Bot(map_graph), 2, {'t3'})
        else:
            self.p1 = Player(Bot(map_graph), 1, {'t8'})
            self.p2 = Player(Boss(map_graph), 2, {'t3'})

    def load_image(self, name, colorkey=None):
        fullname = os.path.join('classes/images', name)
        # если файл не существует, то выходим
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        image = pygame.image.load(fullname)
        return image

    def bot_processing(self):
        print('--------------------------')
        print('day', self.day)
        self.process_player(self.p1, self.p2)
        self.process_player(self.p2, self.p1)
        self.day += 1
        self.score1 = 0
        for t in self.p1.towns:
            self.score1 += self.map_graph[t].coins
            self.score1 += self.map_graph[t].level * 10000
        self.score2 = 0
        for t in self.p2.towns:
            self.score2 += self.map_graph[t].coins
            self.score2 += self.map_graph[t].level * 10000

    def run(self):
        pygame.init()
        castels = [[120, 24, '#EFE3AF'], [400, 24, '#EFE3AF'], [680, 24, '#EFE3AF'], [960, 24, '#3F47CC'],
                    [120, 304, '#EFE3AF'], [400, 304, '#EFE3AF'], [680, 304, '#EFE3AF'], [960, 304, '#EFE3AF'],
                    [120, 584, '#ED1B24'], [400, 584, '#EFE3AF'], [680, 584, '#EFE3AF'], [960, 584, '#EFE3AF']]
        ways_coords_gor = [[220, 54, 'r0'], [500, 54, 'r1'], [780, 54, 'r2'],
                           [220, 334, 'r7'], [500, 334, 'r8'], [780, 334, 'r9'],
                           [220, 614, 'r14'], [500, 614, 'r15'], [780, 614, 'r16']]
        ways_coords_ver = [[150, 124, 'r3'], [430, 124, 'r4'], [710, 124, 'r5'], [990, 124, 'r6'],
                           [150, 404, 'r10'], [430, 404, 'r11'], [710, 404, 'r12'], [990, 404, 'r13']]
        num_roads = {'r0': [ways_coords_gor[0], 't0', 't1', True], 'r1': [ways_coords_gor[1], 't1', 't2', True],
                     'r2': [ways_coords_gor[2], 't2', 't3', True], 'r3': [ways_coords_ver[0], 't0', 't4', False],
                     'r4': [ways_coords_ver[1], 't1', 't5', False], 'r5': [ways_coords_ver[2], 't2', 't6', False],
                     'r6': [ways_coords_ver[3], 't3', 't7', False], 'r7': [ways_coords_gor[3], 't4', 't5', True],
                     'r8': [ways_coords_gor[4], 't5', 't6', True], 'r9': [ways_coords_gor[5], 't6', 't7', True],
                     'r10': [ways_coords_ver[4], 't4', 't8', False], 'r11': [ways_coords_ver[5], 't5', 't9', False],
                     'r12': [ways_coords_ver[6], 't6', 't10', False], 'r13': [ways_coords_ver[7], 't7', 't8', False],
                     'r14': [ways_coords_gor[6], 't8', 't9', True], 'r15': [ways_coords_gor[7], 't9', 't10', True],
                     'r16': [ways_coords_gor[8], 't10', 't11', True]}
        circles_segments = {}
        sprites_levels = {7: 'lvl7 (1).png', 6: 'lvl6 (1).png', 5: 'lvl5 (1).png',
                          4: 'lvl4 (1).png', 3: 'lvl3 (1).png', 2: 'lvl2 (1).png',
                          1: 'lvl1 (1).png', 0: 'lvl0 (1).png'}
        for i in num_roads.keys():
            circles = []
            if num_roads[i][3]:
                segment = 180 // self.map_graph[i].length
                y = num_roads[i][0][1] + 20
                for j in range(self.map_graph[i].length):
                    circles.append((num_roads[i][0][0] + (j + 1) * segment - segment // 2, y))
            else:
                segment = 180 // self.map_graph[i].length
                x = num_roads[i][0][0] + 20
                for j in range(self.map_graph[i].length):
                    circles.append((x, num_roads[i][0][1] + (j + 1) * segment - segment // 2))
            circles_segments[str(num_roads[i][0])] = circles
        screen = pygame.display.set_mode((1180, 708))
        running = True
        flag = True
        clock = 0
        slowing_down = 0.5
        xy = ((-18, -6), (-21, -18), (-9, -30), (3, -18), (-1, -6))
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if 557 < event.pos[0] < 623 and 473 < event.pos[1] < 507:
                        clock += 1
                        slowing_down /= 2
                    font = pygame.font.Font(None, 50)
                    text = font.render(f"{slowing_down}x", True, (255, 255, 255))
                    text_x = screen.get_width() // 2 - text.get_width() // 2
                    text_y = 490 - text.get_height() // 2
                    pygame.draw.rect(screen, '#B5E51D', (text_x, text_y, text.get_width(), text.get_height()))
                    screen.blit(text, (text_x, text_y))
                    pygame.display.flip()
            if self.score1 < self.win_score and self.score2 < self.win_score and self.day < 100:
                screen.fill('#B5E51D')
                self.bot_processing()
                all_sprites = pygame.sprite.Group()
                image = None
                player = None
                for i in num_roads.keys():
                    for j in range(len(self.map_graph[i].segments)):
                        if self.map_graph[i].segments[j]:
                            if self.units[self.map_graph[i].segments[j][0]].empire == 2:
                                player = 'p2'
                            else:
                                player = 'p1'
                        num_unist_on_segment = 5
                        if len(self.map_graph[i].segments[j]) < 5:
                            num_unist_on_segment = len(self.map_graph[i].segments[j])
                        for v in range(num_unist_on_segment):
                            sprite = pygame.sprite.Sprite()
                            for key_img in sprites_levels.keys():
                                if self.units[self.map_graph[i].segments[j][v]].defense >= key_img:
                                    image = sprites_levels[key_img]
                                    break
                            sprite.image = self.load_image(player + '/' + image)
                            sprite.rect = sprite.image.get_rect()
                            sprite.rect.x = circles_segments[str(num_roads[i][0])][j][0] + xy[v][0]
                            sprite.rect.y = circles_segments[str(num_roads[i][0])][j][1] + xy[v][1]
                            all_sprites.add(sprite)
                font = pygame.font.Font(None, 50)
                text = font.render(f"{slowing_down}x", True, (255, 255, 255))
                text_x = screen.get_width() // 2 - text.get_width() // 2
                text_y = 490 - text.get_height() // 2
                screen.blit(text, (text_x, text_y))
                for i in range(len(castels)):
                    if self.map_graph[f't{i}'].empire == 1:
                        castels[i][2] = '#ED1B24'
                    elif self.map_graph[f't{i}'].empire == 2:
                        castels[i][2] = '#3F47CC'
                    else:
                        castels[i][2] = '#EFE3AF'
                    pygame.draw.rect(screen, castels[i][2],
                                     (castels[i][0], castels[i][1], 100, 100))
                    font = pygame.font.Font(None, 32)
                    text = font.render(f"{len(self.map_graph[f't{i}'].units)}", True, '#EFE3AF')
                    text_x = castels[i][0] + text.get_width() // 2
                    text_y = castels[i][1] + text.get_height() // 2
                    screen.blit(text, (text_x, text_y))
                    if i < len(ways_coords_gor):
                        pygame.draw.rect(screen, '#FFC90D', (ways_coords_gor[i][0], ways_coords_gor[i][1], 180, 40))
                        for n, v in enumerate(circles_segments[str(ways_coords_gor[i])]):
                            x, y = v[0], v[1]
                            pygame.draw.circle(screen, (255, 255, 255), (x, y), 20, width=13)
                            if len(self.map_graph[ways_coords_gor[i][2]].segments[n]) > 5:
                                text = font.render("+", True, '#FFFFFF')
                                text1 = font.render(f"{len(self.map_graph[ways_coords_gor[i][2]].segments[n]) - 5}", True, '#FFFFFF')
                                text_x = x - text.get_width() // 2
                                text_y = y + 10 + text.get_height() // 2
                                text_x1 = x - text1.get_width() // 2
                                text_y1 = y + 10 + text1.get_height() // 2 + text.get_height()
                                screen.blit(text, (text_x, text_y))
                                screen.blit(text1, (text_x1, text_y1))
                    if i < len(ways_coords_ver):
                        pygame.draw.rect(screen, '#FFC90D', (ways_coords_ver[i][0], ways_coords_ver[i][1], 40, 180))
                        for n, v in enumerate(circles_segments[str(ways_coords_ver[i])]):
                            x, y = v[0], v[1]
                            pygame.draw.circle(screen, (255, 255, 255), (x, y), 20, width=13)
                            if len(self.map_graph[ways_coords_ver[i][2]].segments[n]) > 5:
                                text = font.render(f"+ {len(self.map_graph[ways_coords_ver[i][2]].segments[n]) - 5}", True, '#FFFFFF')
                                text_x = x + 10 + text.get_width() // 2
                                text_y = y - text.get_height() // 2
                                screen.blit(text, (text_x, text_y))
            else:
                if flag == True:
                    if self.score1 > self.score2:
                        print(self.p1.bot.name, 'wins!')
                    elif self.score1 < self.score2:
                        print(self.p2.bot.name, 'wins!')
                    else:
                        print('draw!')
                    print(self.p1.bot.name, 'score:', self.score1)
                    print(self.p2.bot.name, 'score:', self.score2)
                    flag = False
            all_sprites.draw(screen)
            time.sleep(clock)
            pygame.display.flip()

        pygame.quit()

    def process_player(self, client, enemy):
        self.process_beginning_move(client)
        self.requests['requests'] = []
        self.requests['bot'] = None
        p = multiprocessing.Process(target=self.get_client_requests, args=(client, enemy, self.requests))
        p.start()
        p.join(0.16)  # 0.16 -> 0.1 задержка
        if p.is_alive():
            p.terminate()
            print(client.bot.name + ' is too slow')

        if not (self.requests['bot'] is None):
            client.bot = self.requests['bot']
        if type(self.requests['requests']) == list:
            for req in self.requests['requests']:
                print(req)
                print(self.process_request(client, enemy, req))
                time.sleep(self.delay)
        else:
            print(client.bot.name, 'error: wrong output')

    def process_beginning_move(self, client):
        for town in self.map_graph.keys():
            if town[0] == 't':
                if town in client.towns:
                    self.map_graph[town].coins += 1 + self.map_graph[town].level
                    for unit in self.map_graph[town].units:
                        if self.units[unit].finish_town is None:
                            if self.units[unit].is_moved:
                                self.units[unit].is_moved = False
                            elif self.units[unit].hp < self.units[unit].max_hp:
                                self.units[unit].hp += 2
                                if self.units[unit].hp > self.units[unit].max_hp:
                                    self.units[unit].hp = self.units[unit].max_hp
                else:
                    for unit in self.map_graph[town].units:
                        if self.units[unit].finish_town is None and self.units[unit].empire == client.empire:
                            if self.units[unit].is_moved:
                                self.units[unit].is_moved = False
        fixed_queue = client.units_queue.copy()
        for unit in fixed_queue:
            self.move(unit)
        print('--------------------------')
        time.sleep(self.delay)

    def get_client_requests(self, client, enemy, return_val):
        try:
            cv, ev, cu, eu = self.report(client, enemy)
            return_val['requests'] = client.bot.move(cv, ev, cu, eu)
            return_val['bot'] = client.bot
        except Exception as what:
            print(client.bot.name, 'error:', what)


    def process_request(self, client, enemy, request):
        if type(request) == tuple and len(request) > 1:
            if request[0] == 'upgrade':
                if request[1] in client.towns:
                    if len(self.map_graph[request[1]].units) < 1 or self.units[
                            self.map_graph[request[1]].units[0]].empire == self.map_graph[request[1]].empire:
                        if self.map_graph[request[1]].coins >= round((self.map_graph[request[1]].level + 1)
                                                                     * ((5 + self.map_graph[request[1]].level) / 3)):
                            self.map_graph[request[1]].upgrade()
                            return self.codes['upgrade_ok']
                        else:
                            return self.codes['no_money']
                    else:
                        return self.codes['invaders']
                else:
                    return self.codes['wrong_town']
            elif request[0] == 'equip':
                if request[1] in client.towns:
                    if len(self.map_graph[request[1]].units) < 1 or self.units[
                            self.map_graph[request[1]].units[0]].empire == self.map_graph[request[1]].empire:
                        if self.map_graph[request[1]].coins >= 2:
                            if len(self.map_graph[request[1]].units) <= self.map_graph[request[1]].level:
                                if len(request) == 2:
                                    unit = self.map_graph[request[1]].equip()
                                    self.units[unit.name] = unit
                                    client.units.add(unit.name)
                                    return self.codes['equip_ok']
                                elif len(request) == 3 and type(request[2]) == str:
                                    if request[2] not in Town.used_names:
                                        unit = self.map_graph[request[1]].equip(request[2])
                                        self.units[unit.name] = unit
                                        client.units.add(unit.name)
                                        return self.codes['equip_ok']
                                    else:
                                        return self.codes['unit_already_exist']
                                else:
                                    return self.codes['wrong_command']
                            else:
                                return self.codes['no_space']
                        else:
                            return self.codes['no_money']
                    else:
                        return self.codes['invaders']
                else:
                    return self.codes['wrong_town']
            elif request[0] == 'move' and len(request) == 3:
                if request[1] in client.units:
                    if not self.units[request[1]].is_moved:
                        if request[2] in self.map_graph[self.units[request[1]].location].roads:
                            if self.map_graph[request[2]].finish_town != self.units[request[1]].location:
                                self.units[request[1]].finish_town = self.map_graph[request[2]].finish_town
                            else:
                                self.units[request[1]].finish_town = self.map_graph[request[2]].start_town
                            self.move(request[1])
                            self.units[request[1]].is_moved = True
                            client.units_queue.append(request[1])
                            return self.codes['move_ok']
                        else:
                            return self.codes['wrong_direction']
                    else:
                        return self.codes['unit_moved']
                else:
                    return self.codes['wrong_unit']
            elif request[0] == 'capture':
                if request[1] in client.units:
                    if not self.units[request[1]].is_moved:
                        if self.units[request[1]].location[0] == 't':
                            if self.units[request[1]].location not in client.towns:
                                # отбираем
                                if self.units[request[1]].location in enemy.towns:
                                    enemy.towns.discard(self.units[request[1]].location)
                                # добавляем
                                self.map_graph[self.units[request[1]].location].empire = self.units[request[1]].empire
                                client.towns.add(self.units[request[1]].location)
                                self.units[request[1]].is_moved = True
                                return self.codes['capture_ok']
                            else:
                                return self.codes['in_homeland']
                        else:
                            return self.codes['traveler']
                    else:
                        return self.codes['unit_moved']
                else:
                    return self.codes['wrong_unit']
            elif request[0] == 'increase' and len(request) == 4:
                if request[1] in client.units:
                    if self.units[request[1]].location[0] == 't':
                        if self.units[request[1]].location in client.towns:
                            if type(request[3]) == int and request[3] > 0:
                                if request[3] <= self.map_graph[self.units[request[1]].location].coins:
                                    if request[2] == 'atk':
                                        self.units[request[1]].atk += request[3]
                                        self.map_graph[self.units[request[1]].location].coins -= request[3]
                                    elif request[2] == 'def':
                                        self.units[request[1]].defense += request[3]
                                        self.map_graph[self.units[request[1]].location].coins -= request[3]
                                    elif request[2] == 'max_hp':
                                        self.units[request[1]].max_hp += request[3] * 4
                                        self.map_graph[self.units[request[1]].location].coins -= request[3]
                                    elif request[2] == 'heal':
                                        self.units[request[1]].hp += request[3] * 4
                                        if self.units[request[1]].hp > self.units[request[1]].max_hp:
                                            self.units[request[1]].hp = self.units[request[1]].max_hp
                                        self.map_graph[self.units[request[1]].location].coins -= request[3]
                                    else:
                                        return self.codes['wrong_characteristic']
                                    return self.codes['increase_ok']
                                else:
                                    return self.codes['no_money']
                            else:
                                return self.codes['bad_money']
                        else:
                            return self.codes['not_in_homeland']
                    else:
                        return self.codes['traveler']
                else:
                    return self.codes['wrong_unit']
            else:
                return self.codes['wrong_command']
        else:
            return self.codes['wrong_command']

    def report(self, client, enemy):
        client_towns_data = [TownData(self.map_graph[i], 'client') for i in client.towns]
        enemy_towns_data = [TownData(self.map_graph[i], 'enemy') for i in enemy.towns]
        client_units_data = [UnitData(self.units[i], self.find_unit_segment(i), 'client') for i in client.units]
        enemy_units_data = [UnitData(self.units[i], self.find_unit_segment(i), 'enemy') for i in enemy.units]
        return client_towns_data, enemy_towns_data, client_units_data, enemy_units_data

    def find_unit_segment(self, unit):
        if self.units[unit].location[0] == 'r':
            for j in range(self.map_graph[self.units[unit].location].length):
                if unit in self.map_graph[self.units[unit].location].segments[j]:
                    return j

    def move(self, unit):
        if self.units[unit].location[0] == 't':
            correct_road, direction = self.find_hike_data(unit)
            if len(self.map_graph[correct_road].segments[direction]) > 0 and self.units[
                    self.map_graph[correct_road].segments[direction][0]].empire != self.units[unit].empire:
                self.battle(unit, self.map_graph[correct_road].segments[direction][0])
            else:
                self.map_graph[self.units[unit].location].units.remove(unit)
                self.map_graph[correct_road].segments[direction].append(unit)
                self.units[unit].location = correct_road
        else:
            direction, pos = self.find_move_data(unit)
            if pos + direction < 0 or pos + direction >= self.map_graph[self.units[unit].location].length:
                if len(self.map_graph[self.units[unit].finish_town].units) > 0 and self.units[
                        self.map_graph[self.units[unit].finish_town].units[0]].empire != self.units[unit].empire:
                    self.battle(unit, self.map_graph[self.units[unit].finish_town].units[0])
                elif len(self.map_graph[self.units[unit].finish_town].units) <= self.map_graph[
                        self.units[unit].finish_town].level:
                    self.map_graph[self.units[unit].location].segments[pos].remove(unit)
                    self.map_graph[self.units[unit].finish_town].units.append(unit)
                    self.units[unit].location = self.units[unit].finish_town
                    self.units[unit].finish_town = None
                    if unit in self.p1.units_queue:
                        self.p1.units_queue.remove(unit)
                    else:
                        self.p2.units_queue.remove(unit)
            else:
                if len(self.map_graph[self.units[unit].location].segments[pos + direction]) > 0 and \
                        self.units[self.map_graph[self.units[unit].location].segments[pos + direction][0]].empire != \
                        self.units[unit].empire:
                    return self.battle(unit, self.map_graph[self.units[unit].location].segments[pos + direction][
                        0]), direction
                else:
                    self.map_graph[self.units[unit].location].segments[pos].remove(unit)
                    self.map_graph[self.units[unit].location].segments[pos + direction].append(unit)
        return None, 0

    def find_hike_data(self, unit):
        for road in self.map_graph[self.units[unit].location].roads:
            if self.map_graph[road].finish_town == self.units[unit].finish_town:
                return road, 0
            if self.map_graph[road].start_town == self.units[unit].finish_town:
                return road, -1

    def find_move_data(self, unit):
        if self.map_graph[self.units[unit].location].finish_town == self.units[unit].finish_town:
            direction = 1
        else:
            direction = -1
        for i in range(self.map_graph[self.units[unit].location].length):
            if unit in self.map_graph[self.units[unit].location].segments[i]:
                return direction, i

    def battle(self, attacker, target):
        dmg = self.units[attacker].atk - self.units[target].defense
        if dmg < 1:
            dmg = 1
        if self.units[target].hp - dmg <= 0:
            return self.annihilation(target)
        else:
            self.units[target].hp -= dmg
        return None

    def annihilation(self, target):
        if self.units[target].location[0] == 't':
            self.map_graph[self.units[target].location].units.remove(target)
        else:
            i = 0
            while target not in self.map_graph[self.units[target].location].segments[i]:
                i += 1
            self.map_graph[self.units[target].location].segments[i].remove(target)
        if self.units[target].empire == 1:
            self.p1.units.remove(target)
            if target in self.p1.units_queue:
                self.p1.units_queue.remove(target)
        else:
            self.p2.units.remove(target)
            if target in self.p2.units_queue:
                self.p2.units_queue.remove(target)
        Town.used_names.remove(target)
        Town.names.append(target)
        del self.units[target]
        return target


if __name__ == "__main__":
    import os
    import sys
    import time
    import random
    import multiprocessing
    import pygame
    from classes.bots.boss import Boss
    from classes.bots.bot import Bot
    from classes.standart.town import Town
    from classes.standart.road import Road
    from classes.standart.player import Player

    random.seed(a=835995859)
    server = Server()
    server.run()
