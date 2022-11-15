import pygame
pygame.font.init()
import os
import random

WIDTH, HEIGHT = 750, 950
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Return of The Sith")

# This is Player
SULKHAN = pygame.image.load(os.path.join("src", "lika.png"))

# Enemy
LIKA = pygame.image.load(os.path.join("src", "sulkhan.png"))

# Ammos
LOBIO = pygame.image.load(os.path.join("src", "khinkali.png"))
KHINKALI = pygame.image.load(os.path.join("src", "bean.png"))

# Background
BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("src", "background1.png")), (WIDTH, HEIGHT))


class Ammo:
    def __init__(self, coordinate_x, coordinate_y, ammo_img):
        self.coordinate_x = coordinate_x
        self.coordinate_y = coordinate_y
        self.ammo_img = ammo_img
        self.mask = pygame.mask.from_surface(self.ammo_img)

    def draw(self, window):
        window.blit(self.ammo_img, (self.coordinate_x, self.coordinate_y))

    def move(self, vel):
        self.coordinate_y += vel

    def off_screen(self, height):
        return not(self.coordinate_y <= height and self.coordinate_y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Warrior:
    COOLDOWN = 30

    def __init__(self, coordinate_x, coordinate_y, health=100):
        self.coordinate_x = coordinate_x
        self.coordinate_y = coordinate_y
        self.health = health
        self.warrior_img = None
        self.ammo_img = None
        self.ammos = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.warrior_img, (self.coordinate_x, self.coordinate_y))
        for ammo in self.ammos:
            ammo.draw(window)

    def move_ammos(self, velocity, obj):
        self.cooldown()
        for ammo in self.ammos:
            ammo.move(velocity)
            if ammo.off_screen(HEIGHT):
                self.ammos.remove(ammo)
            elif ammo.collision(obj):
                obj.health -= 10
                self.ammos.remove(ammo)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            ammo = Ammo(self.coordinate_x + 18, self.coordinate_y, self.ammo_img)
            self.ammos.append(ammo)
            self.cool_down_counter = 1

    def get_width(self):
        return self.warrior_img.get_width()

    def get_height(self):
        return self.warrior_img.get_height()


class Sulkhan(Warrior):
    def __init__(self, coordinate_x, coordinate_y, health=100):
        super().__init__(coordinate_x, coordinate_y, health)
        self.warrior_img = SULKHAN
        self.ammo_img = LOBIO
        self.mask = pygame.mask.from_surface(self.warrior_img)
        self.max_health = health

    def move_ammos(self, velocity, objs):
        self.cooldown()
        for ammo in self.ammos:
            ammo.move(velocity)
            if ammo.off_screen(HEIGHT):
                self.ammos.remove(ammo)
            else:
                for obj in objs:
                    if ammo.collision(obj):
                        objs.remove(obj)
                        if ammo in self.ammos:
                            self.ammos.remove(ammo)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.coordinate_x, self.coordinate_y + self.warrior_img.get_height() +10, self.warrior_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.coordinate_x, self.coordinate_y + self.warrior_img.get_height() + 10, self.warrior_img.get_width() * (self.health/self.max_health), 10))


class Lika(Warrior):
    def __init__(self, coordinate_x, coordinate_y, health=100):
        super().__init__(coordinate_x, coordinate_y, health)
        self.warrior_img = LIKA
        self.ammo_img = KHINKALI
        self.mask = pygame.mask.from_surface(self.warrior_img)

    def move(self, velocity):
        self.coordinate_y += velocity

    def shoot(self):
        if self.cool_down_counter == 0:
            ammo = Ammo(self.coordinate_x + 25, self.coordinate_y + 90, self.ammo_img)
            ammo = ammo
            self.ammos.append(ammo)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.coordinate_x - obj1.coordinate_x
    offset_y = obj2.coordinate_y - obj1.coordinate_y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():
    run = True
    FPS = 60
    level = 0
    lives = 3
    main_font = pygame.font.SysFont("Inter", 50)
    lost_font = pygame.font.SysFont("Inter", 80)

    enemies = []
    wave_length = 5
    lika_velocity_speed = 0.8

    sulkhan_velocity_speed = 8
    ammo_velocity_speed = 5

    sulkhan = Sulkhan(WIDTH/2-(SULKHAN.get_width()/2), 780)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    # This function draws game window
    def draw_window():
        WINDOW.blit(BACKGROUND, (0, 0))

        level_count = main_font.render(f"Level: {level}", 1, (247, 213, 27))
        lives_count = main_font.render(f"Lives: {lives}", 1, (247, 213, 27))

        WINDOW.blit(lives_count, (5, 5))
        WINDOW.blit(level_count, (WIDTH - level_count.get_width() - 5, 5))

        for lika in enemies:
            lika.draw(WINDOW)

        sulkhan.draw(WINDOW)

        if lost:
            lost_value = lost_font.render("Lobio Wins!!", 1, (247, 213, 27))
            WINDOW.blit(lost_value, (HEIGHT/2 - lost_value.get_width()/2-100, 330))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        draw_window()

        if lives <= 0 or sulkhan.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Lika(random.randrange(50, WIDTH - 100), random.randrange(-1000, -100))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and sulkhan.coordinate_x - sulkhan_velocity_speed > 0:  # left
            sulkhan.coordinate_x -= sulkhan_velocity_speed
        if keys[pygame.K_d] and sulkhan.coordinate_x + sulkhan_velocity_speed + sulkhan.get_width() < WIDTH:  # right
            sulkhan.coordinate_x += sulkhan_velocity_speed
        if keys[pygame.K_w] and sulkhan.coordinate_y - sulkhan_velocity_speed > 0:  # up
            sulkhan.coordinate_y -= sulkhan_velocity_speed
        if keys[pygame.K_s] and sulkhan.coordinate_y + sulkhan_velocity_speed + sulkhan.get_height() + 15 < HEIGHT:  # down
            sulkhan.coordinate_y += sulkhan_velocity_speed
        if keys[pygame.K_SPACE]:
            sulkhan.shoot()

        for lika in enemies[:]:
            lika.move(lika_velocity_speed)
            lika.move_ammos(ammo_velocity_speed, sulkhan)

            if random.randrange(0, 3 * 60) == 1:
                lika.shoot()

            if collide(lika, sulkhan):
                sulkhan.health -= 10
                enemies.remove(lika)

            elif lika.coordinate_y + lika.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(lika)

        sulkhan.move_ammos(-ammo_velocity_speed, enemies)


def main_menu():
    title_font = pygame.font.SysFont("Inter", 80)
    run = True
    while run:
        WINDOW.blit(BACKGROUND, (0, 0))
        title_value = title_font.render("Press the Mouse To Start...", 1, (247, 213, 27))
        WINDOW.blit(title_value, (WIDTH/2 - title_value.get_width()/2, 330))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()
