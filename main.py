import pygame
import sys
import os
import random

FPS = 70


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * (pos_y + 2))


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x=19, pos_y=43):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.move_left = False
        self.move_right = False
        self.speed = 8

    def get_event(self, event):
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.move_left = True
            if keys[pygame.K_RIGHT]:
                self.move_right = True
        if event.type == pygame.KEYUP:
            keys = pygame.key.get_pressed()
            if not keys[pygame.K_LEFT]:
                self.move_left = False
            if not keys[pygame.K_RIGHT]:
                self.move_right = False

    def change_image(self, new_image, x, y):
        self.image = new_image
        self.rect = self.image.get_rect().move(x, y)

    def start_pos(self):
        self.rect.x = tile_width * 19
        self.rect.y = tile_height * 43

    def update(self):
        if self.move_left:
            self.rect.x -= self.speed
        if self.move_right:
            self.rect.x += self.speed
        if self.rect.x <= 0:
            self.rect.x = 0
        if self.rect.x >= WIDTH - self.rect.size[0]:
            self.rect.x = WIDTH - self.rect.size[0]


class Ball(pygame.sprite.Sprite):
    def __init__(self, pos_x=19 * 32 + 32, pos_y=42 * 16 + 2):
        super().__init__(ball_group, all_sprites)
        self.image = ball_image
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.move_y = random.choice([1, -1])
        self.move_x = random.choice([1, -1])
        self.speed = 4

    def update(self):
        global points
        if self.rect.x < 0:
            self.rect.x = 0
            self.move_x *= -1
        elif self.rect.x > WIDTH - self.rect.width:
            self.rect.x = WIDTH - self.rect.width
            self.move_x *= -1
        if self.rect.y <= 2 * tile_height:
            self.rect.y = 2 * tile_height + 1
            self.move_y *= -1
        if self.rect.y >= HEIGHT:
            self.die()
            return
        if self.rect.colliderect(player.rect):
            intersection = self.rect.clip(player.rect)
            if intersection.y == player.rect.y:
                self.move_y *= -1
                self.rect.y = tile_height * 42 + 2
            if intersection.x <= (player.rect.x + player.rect.width // 10):
                self.move_x = -1
            elif intersection.x >= (player.rect.x + player.rect.width // 10 * 9):
                self.move_x = 1
            self.rect.x += 2

        int_w = 0
        int_h = 0
        collided_sprites = [s for s in tiles_group if self.rect.colliderect(s)]
        for sprite in collided_sprites:
            intersection1 = self.rect.clip(sprite.rect)
            if sprite.image != tile_images['wall']:
                if random.randrange(1, 5) == 1:
                    x, y = sprite.rect.x, sprite.rect.y
                    Bonus(x, y)
                sprite.kill()
                points += 100
            int_w += intersection1.width
            int_h += intersection1.height
        if int_w and int_h:
            if int_w > int_h:
                self.move_y *= -1
            elif int_w < int_h:
                self.move_x *= -1
            else:
                self.move_y *= -1
                self.move_x *= -1
        self.rect.x += self.move_x * self.speed
        self.rect.y += self.move_y * self.speed

    def die(self):
        self.kill()
        change_ball_counter(0)


class Bonus(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(bonus_group, all_sprites)
        self.k = random.randrange(1, 4)
        if self.k == 1:
            self.image = bonus_images['plat_up']
        elif self.k == 2:
            self.image = bonus_images['plat_down']
        else:
            self.image = bonus_images['ball_bonus']
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.speed = 2

    def update(self):
        if self.rect.colliderect(player.rect):
            if self.k == 1:
                if plat_images.index(player.image) != 4:
                    player.change_image(plat_images[plat_images.index(player.image) + 1], player.rect.x, player.rect.y)
            elif self.k == 2:
                if plat_images.index(player.image) != 0:
                    player.change_image(plat_images[plat_images.index(player.image) - 1], player.rect.x, player.rect.y)
            else:
                ar = [x for x in ball_group]
                for b in ar:
                    x, y = b.rect.x, b.rect.y
                    Ball(x - 5, y), Ball(x + 5, y)
                change_ball_counter(1)
            self.kill()
            return
        if self.rect.y > HEIGHT:
            self.kill()
            return
        self.rect.y += self.speed


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    image = image.convert_alpha()

    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)

    return image


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()


def generate_level(level):
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                continue
            elif level[y][x] == 'w':
                Tile('wall', x, y)
            elif level[y][x] == 'b':
                Tile('blue', x, y)
            elif level[y][x] == 'g':
                Tile('green', x, y)
            elif level[y][x] == 'm':
                Tile('marine', x, y)
            elif level[y][x] == 'p':
                Tile('purple', x, y)
            elif level[y][x] == 'r':
                Tile('red', x, y)
            elif level[y][x] == 'y':
                Tile('yellow', x, y)
            elif level[y][x] == 'o':
                Tile('orange', x, y)
    new_player = Player()
    Ball()
    return new_player


def change_ball_counter(k):
    global ball_counter, life_counter
    if k:
        ball_counter *= 3
    else:
        ball_counter -= 1
    if not ball_counter:
        change_life_counter()


def change_life_counter():
    global life_counter, ball_counter
    life_counter -= 1
    if not life_counter:
        end_game()
        new_game()
    else:
        ball_counter = 1
        Ball()
        begin_level()


def begin_level():
    global player
    player.start_pos()
    for b in bonus_group:
        b.kill()
    screen.blit(fon, (0, 0))
    draw_stats()
    tiles_group.draw(screen)
    player_group.draw(screen)
    ball_group.draw(screen)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()


def end_game():
    for sprite in all_sprites:
        sprite.kill()
    fon = pygame.transform.scale(load_image('game_over.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return

        pygame.display.flip()


def draw_stats():
    for i in range(life_counter):
        screen.blit(heart_image, (10 + i * 40, 0))
    font = pygame.font.Font(None, 40)
    text_surface = font.render('POINTS: ' + str(points), True, '#DC143C')
    screen.blit(text_surface, (140, 0))


def new_game():
    global lvl_n, points, ball_counter, life_counter, player, fon
    lvl_n = 0
    points = 0

    start_screen()

    fon = pygame.transform.scale(load_image('game_fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))

    ball_counter = 1
    life_counter = 3

    player = generate_level(load_level(levels[lvl_n]))
    begin_level()


if __name__ == '__main__':
    pygame.init()
    size = WIDTH, HEIGHT = 1280, 720
    tile_width, tile_height = 32, 16
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("ARKANOID")

    tile_images = {
        'wall': load_image('wall.png'),
        'red': load_image('red.png'),
        'blue': load_image('blue.png'),
        'green': load_image('green.png'),
        'marine': load_image('marine.png'),
        'orange': load_image('orange.png'),
        'purple': load_image('purple.png'),
        'yellow': load_image('yellow.png'),
    }

    plat_images = [load_image('lit_platform.png'),
                   load_image('small_plat.png'),
                   load_image('stand_plat.png'),
                   load_image('big_plat.png'),
                   load_image('gig_platform.png')]
    heart_image = load_image('heart.png').convert_alpha()
    player_image = plat_images[2]
    ball_image = load_image('ball.png')

    bonus_images = {'plat_up': load_image('bigger_bonus.png'),
                    'plat_down': load_image('lower_bonus.png'),
                    'ball_bonus': load_image('ball_bonus.png')}

    levels = ['lvl1.txt', 'lvl2.txt', 'lvl3.txt', 'lvl4.txt']

    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    ball_group = pygame.sprite.Group()
    bonus_group = pygame.sprite.Group()

    clock = pygame.time.Clock()

    lvl_n, points, ball_counter, life_counter, player, fon = None, None, None, None, None, None
    new_game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()
            if event.type == pygame.KEYDOWN:
                player.get_event(event)
            if event.type == pygame.KEYUP:
                player.get_event(event)
        if not ([x for x in tiles_group if x.image != tile_images['wall']]):
            lvl_n += 1
            for b in all_sprites:
                b.kill()
            ball_counter = 1
            player = generate_level(load_level(levels[lvl_n]))
            begin_level()

        screen.blit(fon, (0, 0))
        all_sprites.update()
        draw_stats()
        tiles_group.draw(screen)
        player_group.draw(screen)
        bonus_group.draw(screen)
        ball_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
