import os
import sys
import pygame
import random
import csv

pygame.init()

# константы
TILE_SIZE = 50
GRAVITY = 1
VELOCITY_X = 5
VELOCITY_Y = -15
FPS = 50
SIZE = WIDTH, HEIGHT = 800, 550
KEYS_TO_MOVE = [pygame.K_UP, pygame.K_SPACE, pygame.K_LEFT, pygame.K_RIGHT]
BACKGROUND = pygame.Surface(SIZE)

# статистика, которая заносится в csv файл
passed_levels = [0, 0, 0]
counter_of_coins = [0, 0, 0]
healed = [0, 0, 0]
damage_taken = [0, 0, 0]

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
animated_tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
platforms = pygame.sprite.Group()
spikes = pygame.sprite.Group()
coins = pygame.sprite.Group()
hearts = pygame.sprite.Group()

screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()


# конец
def terminate():
    pygame.quit()
    sys.exit()


# очистка
def clean():
    global player, x_start, y_start, is_started, left, right, up, down, camera, counter_for_animation
    player = None
    x_start = None
    y_start = None
    is_started = False

    left = False
    right = False
    up = False
    down = True

    camera = Camera()
    counter_for_animation = 0

    for sprite in all_sprites:
        sprite.kill()

    pygame.display.flip()


def statistic():
    screen.fill('brown')
    with open('statistic.csv', newline="", encoding='utf8') as csvfile:
        reader = list(csv.reader(csvfile, delimiter=';', quotechar='"', ))[1:]
        line_1 = reader[0]
        coins_1 = line_1[0]
        heal_1 = line_1[1]
        damage_1 = line_1[2]
        line_2 = reader[1]
        coins_2 = line_2[0]
        heal_2 = line_2[1]
        damage_2 = line_2[2]
        line_3 = reader[2]
        coins_3 = line_3[0]
        heal_3 = line_3[1]
        damage_3 = line_3[2]
    text_1 = [f'Собрано монет на 1 уровне: {coins_1}',
              f'Вылечено здоровья на 1 уровне: {heal_1}',
              f'Получено урона на 1 уровне: {damage_1}']
    text_2 = [f'Собрано монет на 2 уровне: {coins_2}',
              f'Вылечено здоровья на 2 уровне: {heal_2}',
              f'Получено урона на 2 уровне: {damage_2}']
    text_3 = [f'Собрано монет на 3 уровне: {coins_3}',
              f'Вылечено здоровья на 3 уровне: {heal_3}',
              f'Получено урона на 3 уровне: {damage_3}']
    text = text_1 + text_2 + text_3
    font = pygame.font.Font(None, 30)
    text_coord = 10
    counter_of_lines = 0
    for line in text:
        counter_of_lines += 1
        string_rendered = font.render(line, True, pygame.Color('white'))
        text_rect = string_rendered.get_rect()
        text_coord += 10
        if counter_of_lines in [4, 7]:
            text_coord += 20
        text_rect.top = text_coord
        text_rect.x = 10
        text_coord += text_rect.height
        screen.blit(string_rendered, text_rect)
    menu_rect = pygame.Rect(200, 375, 400, 100)
    exit_image = pygame.transform.scale(load_image('exit.png'), (menu_rect.width, menu_rect.height))
    screen.blit(exit_image, (menu_rect.x, menu_rect.y))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if menu_rect.collidepoint(event.pos):
                    return


def can_be_finished(current_level):
    if current_level == 'level_1':
        if counter_of_coins[0] == 4:
            passed_levels[0] = True
            return True
        return False
    elif current_level == 'level_2':
        if counter_of_coins[1] == 10:
            passed_levels[1] = True
            return True
        return False
    elif current_level == 'level_3':
        if counter_of_coins[2] == 1:
            passed_levels[2] = True
            return True
        return False


# загрузка картинки
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# камера, следящая за игроком
class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


# анимация сердец
class SpriteHeart(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(animated_tiles_group, all_sprites)
        # pygame.Rect(pos_x, pos_y, self.image.get_width(), self.image.get_height())
        self.list_of_hearts = []
        self.cur_frame = random.randint(0, 4)
        for i in range(1, 6):
            self.list_of_hearts.append(
                pygame.transform.scale(load_image('heart_image' + str(i) + '.png'), (TILE_SIZE, TILE_SIZE)))
        self.image = self.list_of_hearts[self.cur_frame]
        self.rect = self.image.get_rect().move(
            pos_x, pos_y)

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.list_of_hearts)
        self.image = self.list_of_hearts[self.cur_frame]


# анимация монет
class SpriteCoin(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(animated_tiles_group, all_sprites)
        # pygame.Rect(pos_x, pos_y, self.image.get_width(), self.image.get_height())
        self.list_of_coins = []
        self.cur_frame = random.randint(0, 5)
        for i in range(1, 7):
            self.list_of_coins.append(
                pygame.transform.scale(load_image('coin_image' + str(i) + '.png'), (TILE_SIZE, TILE_SIZE)))
        self.image = self.list_of_coins[self.cur_frame]
        self.rect = self.image.get_rect().move(
            pos_x, pos_y)

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.list_of_coins)
        self.image = self.list_of_coins[self.cur_frame]
