import pygame as p
import random, time
print(__file__)
p.init()
screen = p.display.set_mode((1550, 800))
p.display.set_caption('FireKill')
icon = p.image.load(__file__.replace('FireKill.py','icon.jpeg')).convert_alpha()
p.display.set_icon(icon)
# Создаём 1 спрайт 1 скина игрока
player1_sk1 = p.image.load(__file__.replace('FireKill.py','player1_sk1.png')).convert_alpha()
player1_sk1 = p.transform.scale(player1_sk1, (100, 180))

# Создаём 2 спрайт 1 скина игрока
player2_sk1 = p.image.load(__file__.replace('FireKill.py','player2_sk1.png')).convert_alpha()
player2_sk1 = p.transform.scale(player2_sk1, (130, 180))

# Создаём 1 спрайт 2 скина игрока
player1_sk2 = p.image.load(__file__.replace('FireKill.py','player1_sk2.png')).convert_alpha()
player1_sk2 = p.transform.scale(player1_sk2, (110, 200))

# Создаём 2 спрайт 2 скина игрока
player2_sk2 = p.image.load(__file__.replace('FireKill.py','player2_sk2.png')).convert_alpha()
player2_sk2 = p.transform.scale(player2_sk2, (110, 200))

# Создаём врага
enemy_img = p.image.load(__file__.replace('FireKill.py','enemy.png')).convert_alpha()
enemy_img = p.transform.scale(enemy_img, (200, 220))

# Создаём сердца для шкалы здоровья
h1 = p.image.load(__file__.replace('FireKill.py','heart_1.png')).convert_alpha()
h1 = p.transform.scale(h1, (150, 100))

h2 = p.image.load(__file__.replace('FireKill.py','heart_2.png')).convert_alpha()
h2 = p.transform.scale(h2, (150, 100))

h3 = p.image.load(__file__.replace('FireKill.py','heart_3.png')).convert_alpha()
h3 = p.transform.scale(h3, (150, 100))

# Создаём монету
coin_img = p.image.load(__file__.replace('FireKill.py','coin.png')).convert_alpha()
coin_img = p.transform.scale(coin_img, (100, 60))

# Создаём магазин
shop_icon = p.image.load(__file__.replace('FireKill.py','shop.png')).convert_alpha()
shop_icon = p.transform.scale(shop_icon, (150, 100))

# Создаём фон магазина
shop_bg = p.image.load(__file__.replace('FireKill.py','back_ground.jpg')).convert_alpha()
shop_bg = p.transform.scale(shop_bg, (1550, 800))

# Создаём фон
bg = p.image.load(__file__.replace('FireKill.py','back_ground.jpg')).convert_alpha()
bg = p.transform.scale(bg, (1550, 800))

# Создаём экран окончания 
go = p.image.load(__file__.replace('FireKill.py','game_over.png')).convert_alpha()
go = p.transform.scale(go, (1550, 800))

# Создаём fireball для 1 скина
fireball1 = p.image.load(__file__.replace('FireKill.py','fireball1.png')).convert_alpha()
fireball1 = p.transform.scale(fireball1, (100, 100))

# Создаём fireball для 2 скина
fireball2 = p.image.load(__file__.replace('FireKill.py','fireball2.png')).convert_alpha()
fireball2 = p.transform.scale(fireball2, (100, 100))

# Шрифты
font = p.font.SysFont('Arial', 30)
big_font = p.font.SysFont('Arial', 60)

clock = p.time.Clock()

# Границы для монет
COIN_MIN_X = 0
COIN_MAX_X = 1000
COIN_MIN_Y = 10
COIN_MAX_Y = 550

# Класс для файрболов
class Fireball:
    def __init__(self, x, y, skin_set):
        self.x = x
        self.y = y
        self.speed = 15
        self.active = True
        self.width = 100
        self.height = 100
        self.skin_set = skin_set  # Добавляем информацию о скина
    
    def update(self):
        self.x += self.speed
        if self.x > 1550:
            self.active = False
    
    def draw(self):
        # Рисуем соответствующий файрбол в зависимости от скина
        if self.skin_set == 1:
            screen.blit(fireball1, (self.x, self.y))
        else:
            screen.blit(fireball2, (self.x, self.y))
    
    def get_rect(self):
        return p.Rect(self.x, self.y, self.width, self.height)

# Класс для монет
class Coin:
    def __init__(self, x, y):
        self.x = max(COIN_MIN_X, min(x, COIN_MAX_X))
        self.y = max(COIN_MIN_Y, min(y, COIN_MAX_Y))
        self.speed = 3
        self.active = True
        self.width = 50
        self.height = 50
        self.value = 5
    
    def update(self):
        self.y += self.speed
        if self.y > 800:
            self.active = False
    
    def draw(self):
        screen.blit(coin_img, (self.x, self.y))
    
    def get_rect(self):
        return p.Rect(self.x, self.y, self.width, self.height)

# Класс для врагов
class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        self.active = True
        self.width = 200
        self.height = 220
        self.has_dropped_coin = False
    
    def update(self):
        self.x -= self.speed
        if self.x < -200:
            self.active = False
    
    def draw(self):
        screen.blit(enemy_img, (self.x, self.y))
    
    def get_rect(self):
        return p.Rect(self.x, self.y, self.width, self.height)
    
    def hit(self):
        self.active = False
        return True
    
    def drop_coin(self, coins):
        if not self.has_dropped_coin:
            if (COIN_MIN_X <= self.x + 75 <= COIN_MAX_X and 
                COIN_MIN_Y <= self.y + 100 <= COIN_MAX_Y):
                coins.append(Coin(self.x + 75, self.y + 100))
            else:
                coin_x = max(COIN_MIN_X, min(self.x + 75, COIN_MAX_X))
                coin_y = max(COIN_MIN_Y, min(self.y + 100, COIN_MAX_Y))
                coins.append(Coin(coin_x, coin_y))
            self.has_dropped_coin = True

# Класс для кнопок магазина
class Button:
    def __init__(self, x, y, width, height, text, price, action):
        self.rect = p.Rect(x, y, width, height)
        self.text = text
        self.price = price
        self.action = action
        self.color = (100, 100, 200)
        self.hover_color = (150, 150, 250)
        self.is_hovered = False
    
    def draw(self):
        color = self.hover_color if self.is_hovered else self.color
        p.draw.rect(screen, color, self.rect)
        p.draw.rect(screen, (0, 0, 0), self.rect, 2)
        if self.price:
            text_surface = font.render(f"{self.text} - {self.price} монет", True, (255, 255, 255))
        else:
            text_surface = font.render(f"{self.text}", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
    
    def check_click(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click

running = True
game_over = False
shop_open = False
x = 0
y = 200
fireballs = []
enemies = []
coins = []
speed = 15
fire_cooldown_max = 60
fire_cooldown = 0
can_fire = True
current_skin = player1_sk1
shooting_animation_time = 0
score = 0
coins_collected = 0
enemy_spawn_timer = 0
lives = 3
invulnerability_timer = 0
extra_lives = 0
current_skin_set = 1  # 1 = первый скин, 2 = второй скин
skin2_unlocked = True  # Второй скин изначально заблокирован
begin_time = time.time()
final_time = 0  # Добавляем переменную для хранения времени окончания игры
coin_multiplier = 1  # Множитель монет (1 = обычное количество, 2 = двойное)
coin_multiplier_unlocked = False  # Куплен ли множитель монет навсегда

# Списки скинов
sk1 = [player1_sk1, player2_sk1]  # Обычный скин
sk2 = [player1_sk2, player2_sk2]  # Второй скин

# Текущий активный набор скинов
skins = sk1

# Создаем кнопки магазина
shop_buttons = [
    Button(470, 200, 600, 60, "Увеличить скорость стрельбы", 50, "faster_fire"),
    Button(470, 300, 600, 60, "Дополнительная жизнь", 100, "extra_life"),
    Button(470, 400, 600, 60, "Увеличить скорость игрока", 75, "faster_move"),
    Button(470, 500, 600, 60, "Купить скин для игрока", 200, "buy_skin2"),
    Button(470, 600, 600, 60, "x2 монеты навсегда", 300, "coin_multiplier"),
    Button(470, 700, 600, 60, "Закрыть магазин", 0, "close_shop")
]

# Переменная для сообщения о недостатке монет
not_enough_coins_message = ""
not_enough_coins_timer = 0

while running:
    mouse_clicked = False
    mouse_pos = p.mouse.get_pos()
    
    for event in p.event.get():
        if event.type == p.QUIT:
            running = False

        if event.type == p.MOUSEBUTTONDOWN:
            mouse_clicked = True
            

        if game_over and event.type == p.KEYDOWN:
            if event.key == p.K_r:
                game_over = False
                x = 0
                y = 200
                fireballs = []
                enemies = []
                coins = []
                speed = 15
                fire_cooldown_max = 60
                fire_cooldown = 0
                can_fire = True
                current_skin = player1_sk1
                shooting_animation_time = 0
                score = 0
                coins_collected = 0
                enemy_spawn_timer = 0
                lives = 3
                invulnerability_timer = 0
                extra_lives = 0
                current_skin_set = 1
                skins = sk1
                skin2_unlocked = False
                begin_time = time.time()  # Сбрасываем таймер при перезапуске
                final_time = 0  # Сбрасываем время окончания
                # Множитель монет сохраняется после перезапуска, так как он куплен навсегда

    if shop_open:
        # Отрисовка магазина
        screen.blit(shop_bg, (0, 0))
        
        title_text = big_font.render("МАГАЗИН", True, (255, 215, 0))
        screen.blit(title_text, (620, 50))
        
        coins_text = big_font.render(f"Монеты: {coins_collected}", True, (255, 215, 0))
        screen.blit(coins_text, (600, 120))
        
        if skin2_unlocked:
            unlocked_text = font.render("2 скин разблокирован!", True, (0, 255, 0))
            screen.blit(unlocked_text, (600, 210))
        
        # Отрисовка кнопок
        for button in shop_buttons:
            # Если это кнопка покупки скина и он уже куплен, меняем текст
            if button.action == "buy_skin2" and skin2_unlocked:
                button.text = "Переключить скин"
                button.price = 0
            elif button.action == "buy_skin2" and not skin2_unlocked:
                button.text = "Купить скин для игрока"
                button.price = 200
                
            # Если это кнопка множителя монет и он уже куплен, меняем текст
            if button.action == "coin_multiplier" and coin_multiplier_unlocked:
                button.text = "x2 монеты активирован"
                button.price = 0
            elif button.action == "coin_multiplier" and not coin_multiplier_unlocked:
                button.text = "x2 монеты навсегда"
                button.price = 300
                
            button.check_hover(mouse_pos)
            button.draw()
            
            if mouse_clicked and button.check_click(mouse_pos, True):
                if button.action == "close_shop":
                    shop_open = False
                elif button.action == "extra_life":
                    if coins_collected >= button.price:
                        coins_collected -= button.price
                        lives += 1
                        extra_lives += 1
                    else:
                        not_enough_coins_message = "Недостаточно монет!"
                        not_enough_coins_timer = 120
                elif button.action == "faster_fire":
                    if coins_collected >= button.price:
                        fire_cooldown_max = max(10, fire_cooldown_max - 12)
                        coins_collected -= button.price
                    else:
                        not_enough_coins_message = "Недостаточно монет!"
                        not_enough_coins_timer = 120
                elif button.action == "faster_move":
                    if coins_collected >= button.price:
                        speed = min(30, speed + 5)
                        coins_collected -= button.price
                    else:
                        not_enough_coins_message = "Недостаточно монет!"
                        not_enough_coins_timer = 120
                elif button.action == "buy_skin2":
                    if not skin2_unlocked:
                        if coins_collected >= 200:
                            coins_collected -= 200
                            skin2_unlocked = True
                        else:
                            not_enough_coins_message = "Недостаточно монет!"
                            not_enough_coins_timer = 120
                    else:
                        # Переключаем скин только если он уже куплен
                        if current_skin_set == 1:
                            current_skin_set = 2
                            skins = sk2
                            current_skin = sk2[0]
                        else:
                            current_skin_set = 1
                            skins = sk1
                            current_skin = sk1[0]
                elif button.action == "coin_multiplier":
                    if not coin_multiplier_unlocked:
                        if coins_collected >= 300:
                            coins_collected -= 300
                            coin_multiplier = 2
                            coin_multiplier_unlocked = True
                        else:
                            not_enough_coins_message = "Недостаточно монет!"
                            not_enough_coins_timer = 120
        
        # Отображение сообщения о недостатке монет
        if not_enough_coins_timer > 0:
            error_text = font.render(not_enough_coins_message, True, (255, 0, 0))
            screen.blit(error_text, (620, 650))
            not_enough_coins_timer -= 1
            
    elif not game_over:
        screen.blit(bg, (0, 0))
        
        keys = p.key.get_pressed()
        
        # Движение игрока
        if keys[p.K_RIGHT] and x < 1000:
            x += speed
        if keys[p.K_LEFT] and x > 0: 
            x -= speed
        if keys[p.K_DOWN] and y < 550: 
            y += speed
        if keys[p.K_UP] and not y < 10: 
            y -= speed

        # Обработка стрельбы
        if keys[p.K_SPACE] and can_fire:
            # Создаем файрбол с указанием текущего скина
            fireballs.append(Fireball(x + 120, y + 50, current_skin_set))
            can_fire = False
            fire_cooldown = fire_cooldown_max
            shooting_animation_time = 15
            current_skin = skins[1]  # Используем стреляющий скин из текущего набора
        
        # Обновляем анимацию стрельбы
        if shooting_animation_time > 0:
            shooting_animation_time -= 1
            if shooting_animation_time == 0:
                current_skin = skins[0]  # Возвращаем обычный скин из текущего набора
        
        # Обновляем перезарядку
        if not can_fire:
            fire_cooldown -= 1
            if fire_cooldown <= 0:
                can_fire = True
                fire_cooldown = 0

        # Обновляем таймер неуязвимости
        if invulnerability_timer > 0:
            invulnerability_timer -= 1

        # Спавн врагов
        enemy_spawn_timer += 1
        if enemy_spawn_timer >= 120:
            enemy_y = random.randint(50, 550)
            enemies.append(Enemy(1550, enemy_y))
            enemy_spawn_timer = 0

        # Отрисовка иконки магазина
        shop_rect = p.Rect(1370, 5, 150, 100)
        screen.blit(shop_icon, (1370, 5))
        
        # Проверка клика по магазину
        if mouse_clicked and shop_rect.collidepoint(mouse_pos):
            shop_open = True

        # Рисуем игрока
        if invulnerability_timer == 0 or invulnerability_timer % 10 < 5:
            screen.blit(current_skin, (x, y))

        # Обновляем файрболы
        for fb in fireballs[:]:
            fb.update()
            
            for enemy in enemies[:]:
                if fb.active and enemy.active:
                    if fb.get_rect().colliderect(enemy.get_rect()):
                        if enemy.hit():
                            score += 10
                            enemy.drop_coin(coins)
                        fb.active = False
                        break
            
            if fb.active:
                fb.draw()
            else:
                fireballs.remove(fb)

        # Обновляем врагов
        player_rect = p.Rect(x, y, 100, 180)
 
        for enemy in enemies[:]:
            enemy.update()
            
            if enemy.active and invulnerability_timer == 0:
                if enemy.get_rect().colliderect(player_rect):
                    lives -= 1
                    invulnerability_timer = 120
                    enemy.active = False
                    
                    if lives <= 0:
                        game_over = True
                        final_time = time.time()  # Записываем время окончания игры
            
            if enemy.active:
                enemy.draw()
            else:
                enemies.remove(enemy)

        # Обновляем монеты
        for coin in coins[:]:
            coin.update()
            
            if coin.active and coin.get_rect().colliderect(player_rect):
                coins_collected += coin.value * coin_multiplier  # Умножаем на множитель
                score += coin.value * 2 * coin_multiplier  # Умножаем на множитель
                coin.active = False
            
            if coin.active:
                coin.draw()
            else:
                coins.remove(coin)

        # Интерфейс
        if not can_fire:
            cooldown_text = font.render(f'Перезарядка: {fire_cooldown/60:.1f} сек', True, (255, 0, 0))
            screen.blit(cooldown_text, (10, 10))
        else:
            ready_text = font.render('Готов к стрельбе!', True, (0, 255, 0))
            screen.blit(ready_text, (10, 10))

        score_text = font.render(f'Счет: {score}', True, (255, 255, 255))
        screen.blit(score_text, (10, 50))

        coins_text = font.render(f'Монеты: {coins_collected}', True, (255, 215, 0))
        screen.blit(coins_text, (10, 90))

        if lives >= 3:
            screen.blit(h3, (0, 100))
        elif lives == 2:
            screen.blit(h2, (0, 100))
        elif lives == 1:
            screen.blit(h1, (0, 100))

        if lives > 3:
            extra_text = font.render(f'+{lives - 3}', True, (0, 255, 0))
            screen.blit(extra_text, (140, 130))

    else:
        # Вычисляем время игры только если игра окончена
        if final_time == 0:
            final_time = time.time()  # Записываем время окончания, если еще не записано
            
        elapsed_time = final_time - begin_time
        
        # Форматируем время
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        
        if minutes == 0:
            main_time = f"{seconds} секунд"
        elif minutes == 1:
            if seconds == 0:
                main_time = "1 минута"
            else:
                main_time = f"1 минута и {seconds} секунд"
        else:
            if seconds == 0:
                main_time = f"{minutes} минут"
            else:
                main_time = f"{minutes} минут и {seconds} секунд"

        # Экран окончания игры
        screen.blit(go, (0, 0))
        game_over_text = big_font.render(f'Счет: {score}', True, (255, 0, 0))
        coins_text = big_font.render(f'Монеты: {coins_collected}', True, (255, 215, 0))
        restart_text = big_font.render('Нажмите R для перезапуска', True, (255, 255, 255))
        time_text = big_font.render(f'Время игры: {main_time}', True, (255, 255, 255))
        
        screen.blit(game_over_text, (900, 600))
        screen.blit(coins_text, (400, 600))
        screen.blit(restart_text, (400, 700))
        screen.blit(time_text, (390, 90))

    p.display.update()
    clock.tick(60)

p.quit()