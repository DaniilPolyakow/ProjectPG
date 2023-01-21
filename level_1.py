from functions import *


def level_1():
    # загрузка уровня
    def load_level(filename):
        filename = "data/" + filename
        # читаем уровень, убирая символы перевода строки
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]

        return level_map

    # класс игрока
    class Player(pygame.sprite.Sprite):
        def __init__(self, pos_x, pos_y, HP, start_x, start_y):
            super().__init__(player_group, all_sprites)
            self.hero = pygame.transform.scale(load_image('playerrealstanding.png'), (TILE_SIZE - 20, TILE_SIZE))
            self.list_of_heroes_left = []
            self.cur_frame_left = 0
            for i in range(1, 10):
                self.list_of_heroes_left.append(
                    pygame.transform.scale(load_image('playerrealleft' + str(i) + '.png'), (TILE_SIZE - 20, TILE_SIZE)))
            self.list_of_heroes_right = []
            self.cur_frame_right = 0
            for i in range(1, 10):
                self.list_of_heroes_right.append(
                    pygame.transform.scale(load_image('playerrealright' + str(i) + '.png'),
                                           (TILE_SIZE - 20, TILE_SIZE)))
            self.image = self.hero

            # позиция
            self.pos_x = pos_x
            self.pos_y = pos_y

            # скорость
            self.v_x = 0
            self.v_y = 0

            # анимация движения
            self.last_move = None
            self.counter_for_animation = 0

            self.rect = self.image.get_rect()
            self.rect.x = pos_x
            self.rect.y = pos_y
            # вычисляем маску для эффективного сравнения
            self.mask = pygame.mask.from_surface(self.image)
            self.HP = HP
            self.is_on_ground = True

            # стартовая позиция (для появления после смерти)
            self.start_x = start_x
            self.start_y = start_y

        # обновление в зависимости от направления движения
        def update(self, left, right, up, down):
            if left:
                self.v_x = -VELOCITY_X
                if self.last_move == 'left':
                    self.counter_for_animation += 1
                    if self.counter_for_animation == 4:
                        self.counter_for_animation = 0
                        self.cur_frame_left = (self.cur_frame_left + 1) % len(self.list_of_heroes_left)
                        self.image = self.list_of_heroes_left[self.cur_frame_left]
                        self.cur_frame_right = 0
                self.last_move = 'left'
            elif right:
                self.v_x = VELOCITY_X
                if self.last_move == 'right':
                    self.counter_for_animation += 1
                    if self.counter_for_animation == 4:
                        self.counter_for_animation = 0
                        self.cur_frame_right = (self.cur_frame_right + 1) % len(self.list_of_heroes_right)
                        self.image = self.list_of_heroes_right[self.cur_frame_right]
                        self.cur_frame_left = 0
                self.last_move = 'right'
            else:
                self.v_x = 0
                self.image = self.hero
                self.last_move = None
                self.cur_frame_left = 0
                self.cur_frame_right = 0
            if up:
                # прыжок возможен только с поверхности
                if self.is_on_ground:
                    self.v_y = VELOCITY_Y
                    self.is_on_ground = False
            if down:
                # если не прыгаем, то падаем
                self.v_y += GRAVITY

            # соприкасается с вертикальными стенками
            self.rect.x += self.v_x
            self.is_touching(self.v_x, 0)

            # соприкасается с горизонтальными стенками
            self.rect.y += self.v_y
            self.is_touching(0, self.v_y)

            self.pos_x, self.pos_y = self.rect.x, self.rect.y
            pygame.display.flip()

        def is_alive(self):
            return self.HP > 0

        # получение урона (шипы)
        def get_damage(self, amount):
            self.HP -= amount

        # восстановление здоровья (сердца)
        def regen(self, amount):
            self.HP += amount
            if self.HP > 100:
                self.HP = 100

        def is_touching(self, v_x, v_y):
            for platform in platforms:
                if pygame.sprite.collide_rect(self, platform):
                    # движение вправо
                    if v_x > 0:
                        self.rect.right = platform.rect.left
                    # движение влево
                    if v_x < 0:
                        self.rect.left = platform.rect.right
                    # движение вниз (падение)
                    if v_y > 0:
                        self.rect.bottom = platform.rect.top
                        self.v_y = 0
                        self.is_on_ground = True
                    # движение вверх (прыжок)
                    if v_y < 0:
                        self.rect.top = platform.rect.bottom
                        self.v_y = 0
                        self.is_on_ground = False
            # сбор монет
            for coin in coins:
                if pygame.sprite.collide_mask(self, coin):
                    counter_of_coins[0] += 1
                    coin.kill()
                    pygame.mixer.pre_init(44100, -16, 1, 512)
                    sound = pygame.mixer.Sound("data/coin.mp3")
                    sound.play()
            # касание шипов
            for spike in spikes:
                if pygame.sprite.collide_mask(self, spike):
                    amount = 10
                    self.get_damage(amount)
                    damage_taken[0] += amount
                    self.rect.x = self.start_x
                    self.pos_x = self.start_x
                    self.rect.y = self.start_y
                    self.pos_y = self.start_y
                    pygame.mixer.pre_init(44100, -16, 1, 512)
                    sound = pygame.mixer.Sound("data/spike.mp3")
                    sound.play()
            # сбор сердец
            for heart in hearts:
                if pygame.sprite.collide_mask(self, heart):
                    amount = 15
                    self.regen(amount)
                    healed[0] += amount
                    heart.kill()
                    pygame.mixer.pre_init(44100, -16, 1, 512)
                    sound = pygame.mixer.Sound("data/heart.mp3")
                    sound.play()

    # класс клеток поля
    class Tile(pygame.sprite.Sprite):
        def __init__(self, tile_type, pos_x, pos_y):
            super().__init__(tiles_group, all_sprites)
            self.image = tile_images[tile_type]
            self.rect = self.image.get_rect().move(
                pos_x, pos_y)

    # генерация загруженного уровня
    def generate_level(level):
        new_player, x, y = None, None, None
        for y in range(1, len(level) - 1):
            for x in range(1, len(level[y]) - 1):
                # создание платформы
                if level[y][x] == '_':
                    platform = Tile('platform', (x - 1) * TILE_SIZE, (y - 1) * TILE_SIZE)
                    platforms.add(platform)
                # создание монеты
                elif level[y][x] == '*':
                    coin = SpriteCoin((x - 1) * TILE_SIZE, (y - 1) * TILE_SIZE)
                    coins.add(coin)
                # создание шипов
                elif level[y][x] == '!':
                    spike = Tile('spike', (x - 1) * TILE_SIZE, (y - 1) * TILE_SIZE)
                    spikes.add(spike)
                # создание сердец
                elif level[y][x] == '%':
                    heart = SpriteHeart((x - 1) * TILE_SIZE, (y - 1) * TILE_SIZE)
                    hearts.add(heart)
                # создание героя
                elif level[y][x] == '@':
                    start_x = (x - 1) * TILE_SIZE
                    start_y = (y - 1) * TILE_SIZE
                    new_player = Player((x - 1) * TILE_SIZE, (y - 1) * TILE_SIZE, 100, start_x, start_y)
        # вернем игрока
        return new_player, start_x, start_y

    # виды клеток
    tile_images = {
        'platform': pygame.transform.scale(load_image('platform.png'), (TILE_SIZE, TILE_SIZE)),
        'spike': pygame.transform.scale(load_image('spike.png'), (TILE_SIZE, TILE_SIZE))
    }
    player, x_start, y_start = generate_level(load_level('level_1.txt'))
    return player, x_start, y_start
