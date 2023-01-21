from level_1 import *
from level_2 import *
from level_3 import *


# стартовое окно
def start_screen():
    global current_level
    intro_text = ["                                                         МЕНЮ",
                  "Правила игры:",
                  "Управление стрелками вправо и влево. Пробел или стрелка вверх - прыжок.",
                  "Цель игры - пройти все уровни, собрав как можно больше монет.",
                  "Шипы наносят урон, сердца восстанавливают здоровье."
                  "", "", "", "", "", "", "", "", "", "", "", "",
                  "                                         Нажмите, чтобы продолжить"]

    fon = pygame.transform.scale(load_image('menu_picture.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 10
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    # ожидание запуска
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # отрисовка меню уровней
                screen.fill('light blue')
                level_1_rect = pygame.Rect(75, 100, 150, 150)
                level_2_rect = pygame.Rect(325, 100, 150, 150)
                level_3_rect = pygame.Rect(575, 100, 150, 150)
                statistic_rect = pygame.Rect(75, 300, 650, 150)
                pygame.draw.rect(screen, 'red', level_1_rect, 10)
                pygame.draw.rect(screen, 'red', level_2_rect, 10)
                pygame.draw.rect(screen, 'red', level_3_rect, 10)
                pygame.draw.rect(screen, 'red', statistic_rect, 10)
                font = pygame.font.Font(None, 100)
                number_1 = font.render('1', True, pygame.Color('red'))
                number_2 = font.render('2', True, pygame.Color('red'))
                number_3 = font.render('3', True, pygame.Color('red'))
                statistic_text = font.render('Статистика', True, pygame.Color('red'))
                screen.blit(number_1, (level_1_rect.centerx - 18, level_1_rect.centery - 28))
                screen.blit(number_2, (level_2_rect.centerx - 18, level_2_rect.centery - 28))
                screen.blit(number_3, (level_3_rect.centerx - 18, level_3_rect.centery - 28))
                screen.blit(statistic_text, (statistic_rect.centerx - 190, statistic_rect.centery - 35))
                pygame.display.flip()
                if level_1_rect.collidepoint(event.pos):
                    current_level = 'level_1'
                    return
                elif level_2_rect.collidepoint(event.pos):
                    current_level = 'level_2'
                    return
                elif level_3_rect.collidepoint(event.pos):
                    current_level = 'level_3'
                    return
                elif statistic_rect.collidepoint(event.pos):
                    statistic()
                    start_screen()
                    return
        pygame.display.flip()
        clock.tick(FPS)


def finish_screen():
    global is_started, player, current_level
    # ожидание запуска
    while True:
        # отрисовка меню уровней
        screen.fill('light blue')
        restart_rect = pygame.Rect(75, 150, 150, 150)
        result_rect = pygame.Rect(325, 150, 150, 150)
        menu_rect = pygame.Rect(575, 150, 150, 150)
        exit_image = pygame.transform.scale(load_image('exit.png'), (menu_rect.width, menu_rect.height))
        screen.blit(exit_image, (menu_rect.x, menu_rect.y))
        restart_image = pygame.transform.scale(load_image('restart.png'), (restart_rect.width, restart_rect.height))
        screen.blit(restart_image, (restart_rect.x, restart_rect.y))
        font = pygame.font.Font(None, 60)
        if can_be_finished(current_level):
            text = font.render('Победа', True, pygame.Color('red'))
            screen.blit(text, (result_rect.centerx - 75, result_rect.centery - 30))
            with open('statistic.csv', newline="", encoding='utf8') as csvfile:
                reader = list(csv.reader(csvfile, delimiter=';', quotechar='"'))
                headers = reader[0]
                lines = [[0] * 3 for _ in range(3)]
                if current_level == 'level_1':
                    lines[0][0] = counter_of_coins[0]
                    lines[0][1] = healed[0]
                    lines[0][2] = damage_taken[0]
                elif current_level == 'level_2':
                    lines[1][0] = counter_of_coins[1]
                    lines[1][1] = healed[1]
                    lines[1][2] = damage_taken[1]
                elif current_level == 'level_3':
                    lines[2][0] = counter_of_coins[2]
                    lines[2][1] = healed[2]
                    lines[2][2] = damage_taken[2]
                with open('statistic.csv', 'w', newline="", encoding='utf8') as csvfile:
                    writer = csv.writer(
                        csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    writer.writerow(headers)
                    for line in lines:
                        writer.writerow(line)
        else:
            text = font.render('Поражение', True, pygame.Color('red'))
            screen.blit(text, (result_rect.centerx - 110, result_rect.centery - 30))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_rect.collidepoint(event.pos):
                    if current_level in ['level_1', 'level_2', 'level_3']:
                        return current_level  # начинаем игру
                elif menu_rect.collidepoint(event.pos):
                    current_level = None
                    return start_screen
        pygame.display.flip()
        clock.tick(FPS)


# смерть от шипов
def death():
    clean()
    result = finish_screen()
    return result


# перенаправление из меню уровней на сами уровни
def start_level():
    global is_started, player, x_start, y_start, current_level
    if current_level == 'level_1':
        is_started = True
        player, x_start, y_start = level_1()
    elif current_level == 'level_2':
        is_started = True
        player, x_start, y_start = level_2()
    elif current_level == 'level_3':
        is_started = True
        player, x_start, y_start = level_3()


with open('statistic.csv', 'w', newline="", encoding='utf8') as csvfile:
    writer = csv.writer(
        csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['Монеты', 'Здоровье', 'Урон'])
    for line in range(3):
        writer.writerow([0, 0, 0])
player = None
x_start = None
y_start = None
start_screen()
is_started = False
left = False
right = False
up = False
down = True
camera = Camera()
counter_for_animation = 0
health1_rect = pygame.Rect(10, 10, 110, 30)
end_rect = pygame.Rect(130, 10, 50, 30)
font = pygame.font.Font(None, 20)
exit_image = pygame.transform.scale(load_image('exit.png'), (end_rect.width, end_rect.height))

# основной цикл
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()  # выход
        if not is_started:
            start_level()
            screen.fill('black')  # стартовое окно
        elif is_started:
            # кнопки нажаты, движение есть
            if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                left = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                right = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                up = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                up = True

            # кнопки не нажаты, движения нет
            if event.type == pygame.KEYUP and event.key == pygame.K_LEFT:
                left = False
            if event.type == pygame.KEYUP and event.key == pygame.K_RIGHT:
                right = False
            if event.type == pygame.KEYUP and event.key == pygame.K_UP:
                up = False
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                up = False
    if is_started:
        # если персонаж движется, то все отрисовывается
        if any([left, right, up, down]):
            player_group.update(left, right, up, down)
            tiles_group.update()
        screen.fill('black')

        # изменяем ракурс камеры
        camera.update(player)
        player.start_x += camera.dx
        player.start_y += camera.dy

        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            camera.apply(sprite)
        # если персонаж умирает, то он отправляется в начальное положение, а все данные камеры обнуляются
        if player.start_x == x_start and player.start_y == y_start:
            camera = Camera()
        counter_for_animation += 1
        if counter_for_animation == 4:
            animated_tiles_group.update()
            counter_for_animation = 0

        all_sprites.draw(screen)
        player_group.draw(screen)
        screen.blit(exit_image, (end_rect.x, end_rect.y))

        # уровень пройден успешно, смерть или выход в меню
        if can_be_finished(current_level) or not player.is_alive() or (
                event.type == pygame.MOUSEBUTTONDOWN and end_rect.collidepoint(event.pos)):
            result = death()
            if type(current_level) == str:
                start_level()
            else:
                result()
                start_level()

        pygame.draw.rect(screen, 'gray', health1_rect)
        health_to_show = player.HP
        if health_to_show > 100:
            health_to_show = 100
        health2_rect = pygame.Rect(15, 15, health_to_show, 20)
        pygame.draw.rect(screen, 'red', health2_rect)
        text = font.render(str(player.HP), True, pygame.Color('white'))
        screen.blit(text, (18, 18))
    clock.tick(FPS)
    pygame.display.flip()
