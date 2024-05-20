from classes.standart.player import Player
from classes.reports.town_data import TownData
from classes.reports.unit_data import UnitData
from classes.standart.status_codes import StatusCodes

class Server:
    def __init__(self):
        self.width = 4
        self.height = 3
        self.map_graph = dict()
        self.generate_map()
        self.units = dict()
        self.win_score = 600000
        self.p1 = None
        self.p2 = None
        self.identify_players()
        self.day = 0
        self.delay = 0
        manager = multiprocessing.Manager()
        self.requests = manager.dict()
        self.requests['requests'] = []
        self.castels = [[120, 5, 'towns/lvl1_town.png'], [400, 5, 'towns/lvl1_town.png'],
                        [680, 5, 'towns/lvl1_town.png'], [945, 5, 'p2/p2_castel.png'],
                        [120, 285, 'towns/lvl1_town.png'], [400, 285, 'towns/lvl1_town.png'],
                        [680, 285, 'towns/lvl1_town.png'], [960, 285, 'towns/lvl1_town.png'],
                        [105, 580, 'p1/p1_castel.png'], [400, 564, 'towns/lvl1_town.png'],
                        [680, 564, 'towns/lvl1_town.png'], [960, 564, 'towns/lvl1_town.png']]
        self.ways_coords_gor = [[195, 54, 'r0'], [475, 54, 'r1'], [755, 54, 'r2'],
                                [195, 334, 'r7'], [475, 334, 'r8'], [755, 334, 'r9'],
                                [195, 614, 'r14'], [475, 614, 'r15'], [755, 614, 'r16']]
        self.ways_coords_ver = [[150, 124, 'r3'], [430, 124, 'r4'], [710, 124, 'r5'], [990, 124, 'r6'],
                                [150, 404, 'r10'], [430, 404, 'r11'], [710, 404, 'r12'], [990, 404, 'r13']]
        self.num_roads = {'r0': [self.ways_coords_gor[0], 't0', 't1', True],
                          'r1': [self.ways_coords_gor[1], 't1', 't2', True],
                          'r2': [self.ways_coords_gor[2], 't2', 't3', True],
                          'r3': [self.ways_coords_ver[0], 't0', 't4', False],
                          'r4': [self.ways_coords_ver[1], 't1', 't5', False],
                          'r5': [self.ways_coords_ver[2], 't2', 't6', False],
                          'r6': [self.ways_coords_ver[3], 't3', 't7', False],
                          'r7': [self.ways_coords_gor[3], 't4', 't5', True],
                          'r8': [self.ways_coords_gor[4], 't5', 't6', True],
                          'r9': [self.ways_coords_gor[5], 't6', 't7', True],
                          'r10': [self.ways_coords_ver[4], 't4', 't8', False],
                          'r11': [self.ways_coords_ver[5], 't5', 't9', False],
                          'r12': [self.ways_coords_ver[6], 't6', 't10', False],
                          'r13': [self.ways_coords_ver[7], 't7', 't8', False],
                          'r14': [self.ways_coords_gor[6], 't8', 't9', True],
                          'r15': [self.ways_coords_gor[7], 't9', 't10', True],
                          'r16': [self.ways_coords_gor[8], 't10', 't11', True]}
        self.circles_segments = {}
        self.sprites_levels = {0: 'lvl0 (1).png', 2: 'lvl1 (1).png', 4: 'lvl2 (1).png',
                               6: 'lvl3 (1).png', 8: 'lvl4 (1).png', 10: 'lvl5 (1).png'}
                               # 12: '', 14: ''}
        self.town_levels = {1: 'towns/lvl1_town.png', 3: 'towns/lvl2_town.png',
                            5: 'towns/lvl3_town.png', 7: 'towns/lvl5_town.png',
                            9: 'towns/lvl6_town.png'}
        self.clock = 0.2
        self.speed_now = 2
        self.speeds = {1: ("2x", 446), 2: ("1x", 490), 3: ("0.5x", 534)}
        self.xy = ((-18, -6), (-21, -18), (-9, -30), (3, -18), (-1, -6))

    def generate_map(self):
        self.map_graph = dict()
        # создание городов
        for i in range(self.height):
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
        # создание дорог
        for i in range(self.height):
            for j in range(self.width - 1):
                self.map_graph['r' + str(i * (self.width * 2 - 1) + j)] = Road('t' + str(self.width * i + j),
                                                                               't' + str(self.width * i + j + 1))
            if i < self.height - 1:
                for j in range(self.width):
                    self.map_graph['r' + str(i * (self.width * 2 - 1) + self.width - 1 + j)] = \
                        Road('t' + str(self.width * i + j), 't' + str(self.width * (i + 1) + j))
        # настройка длины дорог
        roads_count = self.height * (self.width - 1) + (self.height - 1) * self.width
        for i in range(math.ceil(roads_count / 2)):
            length = random.randint(1, 5)
            self.map_graph['r' + str(i)].init_length(length)
            self.map_graph['r' + str(roads_count - 1 - i)].init_length(length)

    def identify_players(self):
        self.p1 = None
        self.p2 = None
        map_objects = dict()
        for i in self.map_graph.keys():
            if i[0] == 'r':
                map_objects[i] = MPRoadData(self.map_graph[i])
            else:
                map_objects[i] = self.map_graph[i].roads
        if random.randint(0, 1) == 0:
            self.p1 = Player(Boss(map_objects), 1, {'t8'})
            self.p2 = Player(Bot(map_objects), 2, {'t3'})
        else:
            self.p1 = Player(Bot(map_objects), 1, {'t8'})
            self.p2 = Player(Boss(map_objects), 2, {'t3'})

    def load_image(self, name):
        fullname = os.path.join('classes/images', name)
        image = pygame.image.load(fullname)
        return image

    def run(self):
        self.units = dict()
        pygame.init()
        for i in self.num_roads.keys():
            circles = []
            if self.num_roads[i][3]:
                segment = 180 // self.map_graph[i].length
                y = self.num_roads[i][0][1] + 20
                for j in range(self.map_graph[i].length):
                    circles.append((self.num_roads[i][0][0] + (j + 1) * segment - segment // 2, y))
            else:
                segment = 180 // self.map_graph[i].length
                x = self.num_roads[i][0][0] + 20
                for j in range(self.map_graph[i].length):
                    circles.append((x, self.num_roads[i][0][1] + (j + 1) * segment - segment // 2))
            self.circles_segments[str(self.num_roads[i][0])] = circles
        screen = pygame.display.set_mode((1180, 708))
        running = True
        flag = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if 557 < event.pos[0] < 623 and 429 < event.pos[1] < 463:
                        self.clock = 0.0
                        self.speed_now = 1
                    elif 557 < event.pos[0] < 623 and 473 < event.pos[1] < 507:
                        self.clock = 0.2
                        self.speed_now = 2
                    elif 557 < event.pos[0] < 623 and 517 < event.pos[1] < 551:
                        self.clock = 0.4
                        self.speed_now = 3
                    font = pygame.font.Font(None, 50)
                    for i in self.speeds.keys():
                        if i == self.speed_now:
                            text = font.render(self.speeds[i][0], True, (255, 0, 0))
                        else:
                            text = font.render(self.speeds[i][0], True, '#EFE3AF')
                        text_x = screen.get_width() // 2 - text.get_width() // 2
                        text_y = self.speeds[i][1] - text.get_height() // 2
                        screen.blit(text, (text_x, text_y))

                    pygame.display.flip()
            if self.p1.score < self.win_score and self.p2.score < self.win_score and self.day < 100:
                screen.fill('#B5E51D')
                self.bot_processing(screen)
            else:
                if flag == True:
                    if self.p1.score > self.p2.score:
                        print(self.p1.bot.name, 'wins!')
                    elif self.p1.score < self.p2.score:
                        print(self.p2.bot.name, 'wins!')
                    else:
                        print('draw!')
                    print(self.p1.bot.name, 'score:', self.p1.score)
                    print(self.p2.bot.name, 'score:', self.p2.score)
                    flag = False
        pygame.quit()

    def bot_processing(self, screen):
        print('day', self.day)
        self.process_player(self.p1, self.p2, screen)
        self.process_player(self.p2, self.p1, screen)
        self.day += 1
        self.p1.count_points(self.map_graph)
        self.p2.count_points(self.map_graph)

    def process_player(self, client: Player, enemy: Player, screen):
        print('--------------------------')
        self.process_beginning_move(client)
        self.requests['requests'] = []
        self.requests['bot'] = None
        p = multiprocessing.Process(target=self.get_client_requests, args=(client, enemy, self.requests))
        p.start()
        p.join()  # 0.16 -> 0.1 задержка
        if p.is_alive():
            p.terminate()
            print(client.bot.name + ' is too slow')
        if not (self.requests['bot'] is None):
            client.bot = self.requests['bot']
        if type(self.requests['requests']) == list:
            for req in self.requests['requests']:
                print(req)
                print(self.process_request(client, enemy, req))
        else:
            print(client.bot.name, 'error: wrong output')
        self.draw(screen)
        print('--------------------------')

    def make_sprite(self, path, indexes, all_sprites):
        sprite = pygame.sprite.Sprite()
        sprite.image = self.load_image(path)
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = indexes[0]
        sprite.rect.y = indexes[1]
        all_sprites.add(sprite)

    def draw(self, screen):
        screen.fill('#B5E51D')
        all_sprites = pygame.sprite.Group()
        self.make_sprite('pole.png', (0, 0), all_sprites)
        image = None
        player = None

        font = pygame.font.Font(None, 50)
        for i in range(len(self.castels)):
            if self.map_graph[f't{i}'].empire == 1:
                if self.castels[i][2] not in ['p1/p1_castel.png', 'p2/p2_castel.png']:
                    for j in self.town_levels.keys():
                        if self.map_graph[f't{i}'].level >= j:
                            self.castels[i][2] = self.town_levels[j]
            elif self.map_graph[f't{i}'].empire == 2:
                if self.castels[i][2] not in ['p1/p1_castel.png', 'p2/p2_castel.png']:
                    for j in self.town_levels.keys():
                        if self.map_graph[f't{i}'].level >= j:
                            self.castels[i][2] = self.town_levels[j]
            else:
                self.castels[i][2] = 'towns/lvl1_town.png'
            if i < len(self.ways_coords_gor):
                if i % 3 == 0:
                    self.make_sprite('road_gor.png', (self.ways_coords_gor[i][0] - 15, self.ways_coords_gor[i][1]),
                                     all_sprites)
                for n, v in enumerate(self.circles_segments[str(self.ways_coords_gor[i])]):
                    x, y = v[0], v[1]
                    self.make_sprite('segment2.png', (x, y - 20), all_sprites)
                    if len(self.map_graph[self.ways_coords_gor[i][2]].segments[n]) > 5:
                        text = font.render("+", True, '#EFE3AF')
                        text1 = font.render(f"{len(self.map_graph[self.ways_coords_gor[i][2]].segments[n]) - 5}",
                                            True, '#EFE3AF')
                        text_x = x - text.get_width() // 2
                        text_y = y + 10 + text.get_height() // 2
                        text_x1 = x - text1.get_width() // 2
                        text_y1 = y + 10 + text1.get_height() // 2 + text.get_height()
                        screen.blit(text, (text_x, text_y))
                        screen.blit(text1, (text_x1, text_y1))
            if i < len(self.ways_coords_ver):
                if i < 4:
                    self.make_sprite('road_ver.png', (self.ways_coords_ver[i][0], self.ways_coords_ver[i][1] - 20), all_sprites)
                for n, v in enumerate(self.circles_segments[str(self.ways_coords_ver[i])]):
                    x, y = v[0], v[1]
                    self.make_sprite('segment2.png', (x - 20, y - 20), all_sprites)
                    if len(self.map_graph[self.ways_coords_ver[i][2]].segments[n]) > 5:
                        text = font.render(f"+ {len(self.map_graph[self.ways_coords_ver[i][2]].segments[n]) - 5}",
                                           True, '#EFE3AF')
                        text_x = x + 10 + text.get_width() // 2
                        text_y = y - text.get_height() // 2
                        screen.blit(text, (text_x, text_y))
            self.make_sprite(self.castels[i][2], (self.castels[i][0], self.castels[i][1]), all_sprites)
        for i in self.num_roads.keys():
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
                    for key_img in self.sprites_levels.keys():
                        if self.units[self.map_graph[i].segments[j][v]].defense >= key_img:
                            image = self.sprites_levels[key_img]
                            break
                    x = self.circles_segments[str(self.num_roads[i][0])][j][0] + self.xy[v][0]
                    y = self.circles_segments[str(self.num_roads[i][0])][j][1] + self.xy[v][1]
                    if self.num_roads[i][0] in self.ways_coords_gor:
                        self.make_sprite(player + '/' + image, (x + 20, y), all_sprites)
                    else:
                        self.make_sprite(player + '/' + image, (x, y), all_sprites)
        all_sprites.draw(screen)
        for i in range(len(self.castels)):
            color = (239, 227, 175)
            if self.map_graph[f't{i}'].empire == 1:
                color = (66, 170, 255)
            elif self.map_graph[f't{i}'].empire == 2:
                color = (255, 51, 51)
            font1 = pygame.font.Font(None, 32)
            text = font1.render(f"{len(self.map_graph[f't{i}'].units)}", True, color)
            text1 = font1.render(f"{self.map_graph[f't{i}'].level}", True, color)
            text_x = self.castels[i][0] + text.get_width() // 2
            text_y = self.castels[i][1] + text.get_height() // 2
            text1_x = self.castels[i][0] + 70 + text1.get_width() // 2
            text1_y = self.castels[i][1] + text1.get_height() // 2
            if self.castels[i][2] == 'p2/p2_castel.png':
                text_x += 20
                text_y += 10
                text1_x += 45
                text1_y += 10
            screen.blit(text, (text_x, text_y))
            screen.blit(text1, (text1_x, text1_y))
        for i in self.speeds.keys():
            if i == self.speed_now:
                text = font.render(self.speeds[i][0], True, (255, 0, 0))
            else:
                text = font.render(self.speeds[i][0], True, '#EFE3AF')
            text_x = screen.get_width() // 2 - text.get_width() // 2
            text_y = self.speeds[i][1] - text.get_height() // 2
            screen.blit(text, (text_x, text_y))
        time.sleep(self.clock)
        pygame.display.flip()

    def process_beginning_move(self, client: Player):
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
        # self.draw(screen)
        time.sleep(self.delay)

    def get_client_requests(self, client: Player, enemy: Player, return_val):
        try:
            cv, ev, cu, eu = self.report(client, enemy)
            return_val['requests'] = client.bot.move(cv, ev, cu, eu)
            return_val['bot'] = client.bot
        except Exception as what:
            print(client.bot.name, 'error:', what)

    def process_request(self, client: Player, enemy: Player, request):
        if type(request) == tuple and len(request) > 1:
            if request[0] == 'upgrade':
                if request[1] in client.towns:
                    if len(self.map_graph[request[1]].units) < 1 or self.units[
                            self.map_graph[request[1]].units[0]].empire == self.map_graph[request[1]].empire:
                        if self.map_graph[request[1]].coins >= round((self.map_graph[request[1]].level + 1)
                                                                     * ((5 + self.map_graph[request[1]].level) / 3)):
                            self.map_graph[request[1]].upgrade()
                            return StatusCodes.upgrade_ok
                        else:
                            return StatusCodes.no_money
                    else:
                        return StatusCodes.invaders
                else:
                    return StatusCodes.wrong_town
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
                                    return StatusCodes.equip_ok
                                elif len(request) == 3 and type(request[2]) == str:
                                    if request[2] not in Town.used_names:
                                        unit = self.map_graph[request[1]].equip(request[2])
                                        self.units[unit.name] = unit

                                        client.units.add(unit.name)
                                        return StatusCodes.equip_ok
                                    else:
                                        return StatusCodes.unit_already_exist
                                else:
                                    return StatusCodes.wrong_command
                            else:
                                return StatusCodes.no_space
                        else:
                            return StatusCodes.no_money
                    else:
                        return StatusCodes.invaders
                else:
                    return StatusCodes.wrong_town
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
                            return StatusCodes.move_ok
                        else:
                            return StatusCodes.wrong_direction
                    else:
                        return StatusCodes.unit_moved
                else:
                    return StatusCodes.wrong_unit
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
                                return StatusCodes.capture_ok
                            else:
                                return StatusCodes.in_homeland
                        else:
                            return StatusCodes.traveler
                    else:
                        return StatusCodes.unit_moved
                else:
                    return StatusCodes.wrong_unit
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
                                        return StatusCodes.wrong_characteristic
                                    return StatusCodes.increase_ok
                                else:
                                    return StatusCodes.no_money
                            else:
                                return StatusCodes.bad_money
                        else:
                            return StatusCodes.in_abroad
                    else:
                        return StatusCodes.traveler
                else:
                    return StatusCodes.wrong_unit
            else:
                return StatusCodes.wrong_command
        else:
            return StatusCodes.wrong_command

    def report(self, client: Player, enemy: Player):
        client_towns_data = dict()
        for town in client.towns:
            client_towns_data[town] = TownData(self.map_graph[town], 'client')
        enemy_towns_data = dict()
        for town in enemy.towns:
            enemy_towns_data[town] = TownData(self.map_graph[town], 'enemy')
        client_units_data = dict()
        for unit in client.units:
            client_units_data[unit] = UnitData(self.units[unit], self.find_unit_segment(unit), 'client')
        enemy_units_data = dict()
        for unit in enemy.units:
            enemy_units_data[unit] = UnitData(self.units[unit], self.find_unit_segment(unit), 'enemy')
        return client_towns_data, enemy_towns_data, client_units_data, enemy_units_data

    def find_unit_segment(self, unit: str):
        if self.units[unit].location[0] == 'r':
            for j in range(self.map_graph[self.units[unit].location].length):
                if unit in self.map_graph[self.units[unit].location].segments[j]:
                    return j

    def move(self, unit: str):
        if self.units[unit].location[0] == 't':
            correct_road, direction = self.find_start_move_data(unit)
            self.exit_of_town(correct_road, direction, unit)
        else:
            direction, pos = self.find_where_step(unit)
            if pos + direction < 0 or pos + direction >= self.map_graph[self.units[unit].location].length:
                self.enter_town(pos, unit)
            else:
                self.step(direction, pos, unit)

    def find_start_move_data(self, unit: str):
        for road in self.map_graph[self.units[unit].location].roads:
            if self.map_graph[road].finish_town == self.units[unit].finish_town:
                return road, 0
            if self.map_graph[road].start_town == self.units[unit].finish_town:
                return road, -1

    def find_where_step(self, unit: str):
        if self.map_graph[self.units[unit].location].finish_town == self.units[unit].finish_town:
            direction = 1
        else:
            direction = -1
        for i in range(self.map_graph[self.units[unit].location].length):
            if unit in self.map_graph[self.units[unit].location].segments[i]:
                return direction, i

    def exit_of_town(self, correct_road: str, direction: int, unit: str):
        if len(self.map_graph[correct_road].segments[direction]) > 0 and self.units[
                self.map_graph[correct_road].segments[direction][0]].empire != self.units[unit].empire:
            self.battle(unit, self.map_graph[correct_road].segments[direction][0])
        else:
            self.map_graph[self.units[unit].location].units.remove(unit)
            self.map_graph[correct_road].segments[direction].append(unit)
            self.units[unit].location = correct_road

    def enter_town(self, pos: int, unit: str):
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

    def step(self, direction: int, pos: int, unit: str):
        if len(self.map_graph[self.units[unit].location].segments[pos + direction]) > 0 and \
                self.units[self.map_graph[self.units[unit].location].segments[pos + direction][0]].empire != \
                self.units[unit].empire:
            self.battle(unit, self.map_graph[self.units[unit].location].segments[pos + direction][0]), direction
        else:
            self.map_graph[self.units[unit].location].segments[pos].remove(unit)
            self.map_graph[self.units[unit].location].segments[pos + direction].append(unit)

    def battle(self, attacker: str, target: str):
        dmg = self.units[attacker].atk - self.units[target].defense
        if dmg < 1:
            dmg = 1
        if self.units[target].hp - dmg <= 0:
            self.annihilation(target)
        else:
            self.units[target].hp -= dmg

    def annihilation(self, target: str):
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


if __name__ == "__main__":
    import os
    import time
    import random
    import multiprocessing
    import pygame
    import math
    from classes.bots.boss import Boss
    from classes.bots.bot import Bot
    from classes.standart.town import Town
    from classes.standart.road import Road
    from classes.reports.mp_road_data import MPRoadData

    # random.seed(a=835995859)
    server = Server()
    server.run()
