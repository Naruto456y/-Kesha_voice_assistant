from gtts import gTTS
import speech_recognition as sr
import pygame
import os
import time
import random
import keyboard
import webbrowser
from datetime import datetime
import AppOpener
import threading
import queue
import psutil
import tempfile
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import gig
from youtube_search import YoutubeSearch
import mouse

# Инициализация PyGame для интерфейса
pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Голосовой помощник Кеша")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (0, 0, 139)
YELLOW = (255, 255, 0)

# Шрифты
font_large = pygame.font.SysFont('Arial', 32)
font_medium = pygame.font.SysFont('Arial', 20)
font_small = pygame.font.SysFont('Arial', 16)
font_tiny = pygame.font.SysFont('Arial', 14)

# Состояние интерфейса
class UIState:
    def __init__(self):
        self.is_listening = False
        self.is_wake_word_detected = False
        self.last_command = ""
        self.status = "Готов к работе"
        self.status_color = GREEN
        self.messages = []
        self.commands_page = 0
        self.total_command_pages = 0
        self.animation_counter = 0

ui_state = UIState()

# Полный список команд
COMMAND_CATEGORIES = {
    "🎯 Основные команды": [
        "Привет - Поприветствовать",
        "Как дела - Узнать состояние",
        "Молодец - Похвалить",
        "Пока/Стоп/Выход - Завершить работу"
    ],
    "🌐 Интернет и поиск": [
        "Найди [запрос] - Поиск в интернете",
        "Найди в ютуби [запрос] - Поиск на YouTube",
        "Youtube - Открыть YouTube",
        "Игры - Открыть Яндекс Игры",
        "Погода - Узнать погоду",
        "Переводчик - Открыть переводчик"
    ],
    "🎮 Игры": [
        "Камень ножницы бумага - Запустить игру",
        "Виселица - Запустить игру",
        "Викторина - Запустить игру",
        "Шахматы - Запустить шахматы",
        "Квест - Запустить игру",
        "Крестики-нолики - Запустить игру",
        "Угадай число - Запустить игру",
        "FireKill - Запустить игру"
    ],
    "💻 Система и приложения": [
        "Открой [приложение] - Открыть программу",
        "Закрой [приложение] - Закрыть программу",
        "Открой проводник - Открыть файловый менеджер",
        "Открой настройки - Открыть настройки системы",
        "Сверни окно - Свернуть текущее окно",
        "Закрой окно - Закрыть текущее окно"
    ],
    "🎵 Медиа и управление": [
        "Музыка - Открыть музыку",
        "Музыка [название] - Найти музыку",
        "Пауза - Поставить на паузу",
        "Дальше - Следующий трек",
        "Пробел - Нажать пробел",
        "Громче - Увеличить громкость",
        "Тише - Уменьшить громкость",
        "Громкость [1-100] - Установить громкость"
    ],
    "⚙️ Системная информация": [
        "Время - Текущее время",
        "Состояние батареи - Информация о батарее",
        "Выключи компьютер - Выключить ПК"
    ],
    "🔧 Специальные команды": [
        "Переведи на английский [текст] - Перевод",
        "Переведи на русский [текст] - Перевод",
        "Включи свет - Умный дом",
        "Выключи свет - Умный дом",
        "Поставь таймер на [минуты] - Таймер",
        "Телефон - Совершить звонок"
    ]
}

# Вычисляем общее количество страниц команд
all_commands = []
for category, commands in COMMAND_CATEGORIES.items():
    all_commands.append(category)
    all_commands.extend(commands)

ui_state.total_command_pages = (len(all_commands) + 7) // 8  # 8 команд на страницу

def get_text_with_url(url, class_name):
    """Функция для получения текста из элемента с указанным классом на веб-странице"""
    try:
        encoded_url = quote(url, safe=':/?&=')
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
        response = requests.get(encoded_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        element = soup.find(class_=class_name)

        if element:
            return element.text.strip()
        else:
            return f"Элемент с классом '{class_name}' не найден"

    except requests.exceptions.RequestException as e:
        return f"Ошибка запроса: {e}"
    except Exception as e:
        return f"Произошла ошибка: {e}"

def start(name):
    """Открывает файл или папку в этой папке"""
    path = __file__.replace('Kesha.py', name)
    os.startfile(path)

def search_and_open_youtube(query):
    """Ищет видео на YouTube по запросу и открывает первое найденное видео в браузере"""
    results = YoutubeSearch(query, max_results=1).to_dict()
    
    if not results:
        print("Ничего не найдено.")
        return
    
    video_url = f"https://youtube.com{results[0]['url_suffix']}"
    webbrowser.open(video_url)
    print(f"Открываю видео: {results[0]['title']}")

# Инициализация аудио системы
pygame.mixer.init()
TEMP_DIR = tempfile.gettempdir()
command_queue = queue.Queue()

# Настройки голосового помощника
class Config:
    WAKE_WORDS = ['кеша', 'кеш', 'гоша', 'кэш','валера','чебурек']
    SENSITIVITY = 0.5
    ENERGY_THRESHOLD = 1000
    PAUSE_THRESHOLD = 2
    DYNAMIC_ENERGY = True
    TIMEOUT = 1.5
    PHRASE_LIMIT = 3

# Инициализация управления громкостью
try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume_control = cast(interface, POINTER(IAudioEndpointVolume))
    VOLUME_CONTROL_ENABLED = True
except:
    VOLUME_CONTROL_ENABLED = False
    print("Не удалось инициализировать управление громкостью")

class AudioManager:
    """Управление воспроизведением аудио"""
    def __init__(self):
        self._init_mixer()
        self.playback_thread = None
        self.is_speaking = False

    def _init_mixer(self):
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        except:
            print("Ошибка инициализации аудио микшера")

    def say(self, text):
        """Асинхронное воспроизведение текста"""
        if not text.strip():
            return

        try:
            # Добавляем сообщение в интерфейс
            ui_state.messages.append(("Кеша", text))
            if len(ui_state.messages) > 10:
                ui_state.messages.pop(0)
                
            filename = os.path.join(TEMP_DIR, f"voice_{int(time.time()*1000)}.mp3")
            tts = gTTS(text=text, lang='ru', slow=False)
            tts.save(filename)

            if self.playback_thread and self.playback_thread.is_alive():
                pygame.mixer.music.stop()
                self.playback_thread.join(timeout=0.1)

            self.is_speaking = True
            try:
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()
            except:
                self._init_mixer()
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()

            self.playback_thread = threading.Thread(
                target=self._cleanup_audio,
                args=(filename,),
                daemon=True
            )
            self.playback_thread.start()

        except Exception as e:
            print(f"Ошибка воспроизведения: {e}")

    def _cleanup_audio(self, filename):
        """Очистка аудиофайлов после воспроизведения"""
        while pygame.mixer.music.get_busy():
            time.sleep(0.05)
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except:
            pass
        self.is_speaking = False

audio_manager = AudioManager()

class VoiceRecognizer:
    """Распознавание голосовых команд"""
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = Config.ENERGY_THRESHOLD
        self.recognizer.pause_threshold = Config.PAUSE_THRESHOLD
        self.recognizer.dynamic_energy_threshold = Config.DYNAMIC_ENERGY

    def listen(self, timeout=1.5):
        """Слушаем микрофон с таймаутом"""
        with sr.Microphone() as source:
            try:
                ui_state.is_listening = True
                ui_state.status = "Слушаю..."
                ui_state.status_color = BLUE
                
                # Ждем, пока Кеша закончит говорить
                while audio_manager.is_speaking:
                    time.sleep(0.1)
                
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,
                    phrase_time_limit=Config.PHRASE_LIMIT
                )
                text = self.recognizer.recognize_google(audio, language='ru-RU').lower()
                
                ui_state.messages.append(("Вы", text))
                if len(ui_state.messages) > 10:
                    ui_state.messages.pop(0)
                    
                ui_state.is_listening = False
                ui_state.status = "Готов к работе"
                ui_state.status_color = GREEN
                
                return text
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                ui_state.is_listening = False
                ui_state.status = "Готов к работе"
                ui_state.status_color = GREEN
                return ""
            except Exception as e:
                print(f"Ошибка распознавания: {e}")
                ui_state.is_listening = False
                ui_state.status = "Ошибка распознавания"
                ui_state.status_color = RED
                return ""

def re(text):
    """Быстрый вывод и озвучивание текста"""
    print(text)
    audio_manager.say(text)

def listen_for_wake_word():
    """Прослушивание ключевого слова для активации"""
    recognizer = VoiceRecognizer()
    re("Готов к работе, жду ключевое слово...")
    print("кеша, кеш, гоша, кэш, валера, чебурек")
    
    while True:
        try:
            # Ждем, пока Кеша закончит говорить
            while audio_manager.is_speaking:
                time.sleep(0.1)
                
            text = recognizer.listen(timeout=Config.TIMEOUT)
            if any(word in text for word in Config.WAKE_WORDS):
                ui_state.is_wake_word_detected = True
                ui_state.status = "Активирован! Говорите команду..."
                ui_state.status_color = GREEN
                command_queue.put("wake_word_detected")
                time.sleep(2)
                ui_state.is_wake_word_detected = False
        except Exception as e:
            print(f"Ошибка в listen_for_wake_word: {e}")
            time.sleep(0.1)

def recognize_command():
    """Распознавание команды после активации"""
    recognizer = VoiceRecognizer()
    re("Слушаю...")
    return recognizer.listen()

def process_commands():
    """Обработка команд из очереди"""
    while True:
        command = command_queue.get()
        if command == "wake_word_detected":
            command_text = recognize_command()
            if command_text:
                ui_state.last_command = command_text
                threading.Thread(
                    target=handle_command,
                    args=(command_text,),
                    daemon=True
                ).start()
            else:
                re("Я вас не расслышал, повторите пожалуйста")

def set_system_volume(level):
    """Установка громкости системы"""
    if not VOLUME_CONTROL_ENABLED:
        return False
    try:
        volume_control.SetMasterVolumeLevelScalar(level, None)
        return True
    except:
        return False

def get_system_volume():
    """Получение текущей громкости"""
    if not VOLUME_CONTROL_ENABLED:
        return 0.5
    try:
        return volume_control.GetMasterVolumeLevelScalar()
    except:
        return 0.5

def change_volume(direction):
    """Изменение громкости"""
    current = get_system_volume()
    if direction == 'up':
        new_vol = min(1.0, current + 0.1)
    elif direction == 'down':
        new_vol = max(0.0, current - 0.1)
    else:
        return current

    if set_system_volume(new_vol):
        return new_vol
    return current

def handle_command(text):
    """Обработка конкретной команды"""
    if not text:
        return

    print(f"Распознанная команда: {text}")
    text = text.lower().strip()
    try:
        if any(word in text for word in ['пока', 'выход', 'стоп']):
            re('До свидания!')
            time.sleep(2)
            os._exit(0)

        elif 'найди в ютуби' in text:
            quertty = text.replace("найди в ютуби", "").strip()
            if quertty:
                search_and_open_youtube(quertty)
                re('Вот что я нашёл')
            else:
                re('Что именно вам найти?')

        elif 'открой roblox' in text:
            os.startfile(r'C:\Users\Yusuf\AppData\Local\Roblox\Versions\version-fe20d41d8fec4770\RobloxPlayerBeta')
            re('Открываю')

        elif 'открой minecraft' in text:
            os.startfile(r'C:\Users\Yusuf\OneDrive\Рабочий стол\MINECRAFT')
            re('Открываю')
            
        elif 'переведи на' in text:
                if 'английский' in text:
                    m = text.replace("переведи на английский", "").strip()
                    while True:
                        try:
                            webbrowser.open(f'https://translate.yandex.ru/?from=tableau_yabro&source_lang=ru&target_lang=en&text={m}')
                            time.sleep(2)
                            for i in range(13):
                                time.sleep(0.0000001)
                                keyboard.send('Tab')
                            re(f'{m} на английском')
                            time.sleep(2)
                            keyboard.send('alt+ctrl+V')
                            break
                        except:
                            keyboard.send('alt+Shift')
                            keyboard.send('alt+ctrl+V')
                            break

                elif 'русский' in text:
                    m = text.replace("переведи на русский", "").strip()
                    while True:
                        try:
                            webbrowser.open(f'https://translate.yandex.ru/?from=tableau_yabro&source_lang=en&target_lang=ru&text={m}')
                            time.sleep(2)
                            for i in range(13):
                                time.sleep(0.0000001)
                                keyboard.send('Tab')
                            re(f'{m} на русском')
                            time.sleep(2)
                            keyboard.send('alt+ctrl+V')
                            break
                        except:
                            keyboard.send('alt+Shift')
                            keyboard.send('alt+ctrl+V')
                            break

        elif 'youtube' in text:
            webbrowser.open('https://www.youtube.com/')
            re('Открываю YouTube')
        
        elif 'камень ножницы бумага' in text:
            re('Запускаю игру камень ножницы бумага\n')
            start('stone_knots_paper.py')

        elif 'виселиц' in text:
            re('Запускаю игру виселица\n')
            start('hangman.py')

        elif 'викторин' in text:
            re('Запускаю игру викторина\n')
            start('quiz.py')

        elif 'вниз' in text:
            mouse.wheel(-1)

        elif 'верх' in text:
            mouse.wheel(1)

        elif 'квест' in text:
            re('Запускаю игру квест\n')
            start('quest.py')

        elif 'крестики-нолики' in text:
            re('Запускаю игру крестики нолики\n')
            start('tictactoe.py')

        elif 'угадай число' in text:
            re('Запускаю игру угадай число\n')
            start('rand_game.py')

        elif any(word in text for word in ['дипси', 'deep', 'deepseek']):
            re('Открываю нейросеть дипсик')
            webbrowser.open('https://chat.deepseek.com/a/chat/s/5e62a9fe-9717-452d-9a82-89c2ca2dd30b')

        elif 'переводчик' in text:
            re('Открываю переводчик')
            webbrowser.open('https://translate.yandex.ru/?111=')

        elif 'игры' in text:
            re('Открываю яндекс игры')
            webbrowser.open('https://yandex.ru/games/')

        elif 'как дела' in text:
           re('Всё отлично!Будет ещё лучше если я смогу вам помочь')

        elif 'молодец' in text:
            re('Спасибо!Всегда к вашим услугам')

        elif 'привет' in text:
            re('Привет! Чем могу помочь?')

        elif 'найди' in text:
            querty = text.replace("найди", "").strip()
            if querty:
                webbrowser.open_new_tab(f'https://yandex.ru/search/?text={querty}')
                re(f'Ищу {querty}')
            else:
                re('Что именно вам найти?')

        elif 'погод' in text:
            a = get_text_with_url('https://rp5.ru/Погода_в_Сосенках,_Москва','t_0')
            re(a)
            
        elif 'fire kill' in text:
            start(r'game\FireKill.py')
            re('Запускаю')
            
        elif 'телефон' in text:
            keyboard.send('Win + 3')
            time.sleep(1)
            mouse.move(299, 180)
            time.sleep(0.1)
            mouse.click('left')
            time.sleep(0.1)
            mouse.move(350, 129)
            time.sleep(0.1)
            mouse.click('left')
            re('Уже звоню ищите')    
            
        elif 'fuck you' in text:
            start(r'game\FireKill.py')
            re('Запускаю')
            
        elif 'открой настройки' in text:
            keyboard.send('Win + I')
            re('Есть')

        # Для тех у кого умный дом

        elif 'включи свет' in text:
            webbrowser.open('https://alice.yandex.ru?')
            time.sleep(2)
            keyboard.write('Включи светильник')
            keyboard.send('Enter')
            re('Ок')
        
        elif 'выключи свет' in text:
            webbrowser.open('https://alice.yandex.ru?')
            time.sleep(2)
            keyboard.write('Выключи свет')
            keyboard.send('Enter')
            re('Ок')

        elif 'поставь таймер на' in text:
            w = text.replace("поставь таймер на", "").strip()
            w = w.replace("минуту", "").strip()
            w = w.replace("минут", "").strip()
            w = w.replace("ы", "").strip()
            if w:
                start('timer.py')
                time.sleep(3)
                keyboard.write(w)
                keyboard.send('Enter') 
                re('Таймер успешно запущен') 
            else:
                re('Уточните на сколько поставить таймер')

        elif 'музыка' in text:
            q = text.replace("музыка", "").strip()
            if q:
                AppOpener.open('Yandex',True)
                webbrowser.open(f'https://rus.hitmotop.com/search?q={q}')
                time.sleep(1)
                keyboard.send('Tab')
                keyboard.send('space')
                re('Послушайте, что я нашёл')
                time.sleep(2)
                mouse.move(252, 794)
                mouse.click('left')
            else:
                AppOpener.open('Yandex',True)
                webbrowser.open('https://rus.hitmotop.com')
                re('Открываю')

        elif 'открой проводник' in text:
            keyboard.send('Win + E')
            re('Есть')

        elif 'дальше' in text:
            keyboard.send('shift + N')
            re('Есть')

        elif 'пробел' in text:
            keyboard.send('space')
            re('Есть')

        elif 'полный экран' in text:
            keyboard.send('F')
            re('Есть')

        elif 'время' in text:
            current_time = datetime.now().strftime("%H:%M")
            re(f'Сейчас {current_time}')

        elif 'времени' in text:
            current_time = datetime.now().strftime("%H:%M")
            re(f'Сейчас {current_time}')    

        elif 'состояние' in text or 'батарея' in text:
            battery = psutil.sensors_battery()
            if battery.power_plugged:
                status = "заряжается"
            else:
                status = "работает от батареи"
            re(f'Батарея {status}, уровень заряда {battery.percent}%')

        elif any(word in text for word in ['громче', 'увеличь громкость']):
            new_vol = change_volume('up')
            re(f'Громкость увеличена до {int(new_vol * 100)}%')

        elif any(word in text for word in ['тише', 'уменьши громкость']):
            new_vol = change_volume('down')
            re(f'Громкость уменьшена до {int(new_vol * 100)}%')

        elif 'громкость' in text:
            try:
                vol_level = int(''.join(filter(str.isdigit, text)))
                vol_level = max(0, min(100, vol_level))
                if set_system_volume(vol_level / 100):
                    re(f'Установлена громкость {vol_level}%')
            except:
                re('Скажите, например, "поставь громкость 50"')

        elif 'открой' in text:
            app = text.replace("открой", "").strip()
            if app:
                try:
                    AppOpener.open(app,match_closest=True)
                    re(f'Открываю {app}')
                except:
                    re(f'Не удалось открыть {app}')
            else:
                re('Какое приложение открыть?')

        elif 'закрой' in text:
            app = text.replace("закрой", "").strip()
            if app:
                try:
                    AppOpener.close(app,match_closest=True)
                    re(f'Закрываю {app}')
                except:
                    re(f'Не удалось закрыть {app}')
            else:
                re('Какое приложение закрыть?')

        elif 'выключи компьютер' in text:
            re('Выключаю компьютер через 10 секунд')
            os.system("shutdown /s /t 10")

        else:
            ans = gig.ask_gigachat(text)
            for i in '*%»`#$"':
                ans = ans.replace(i, '')
            re(ans)

    except Exception as e:
        re('Произошла ошибка при обработке команды')
        print(f"Ошибка: {e}")

def draw_interface():
    """Отрисовка интерфейса"""
    screen.fill(LIGHT_BLUE)
    
    # Заголовок
    title = font_large.render("Голосовой помощник Кеша", True, DARK_BLUE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 15))
    
    # Статусная панель
    pygame.draw.rect(screen, WHITE, (10, 60, WIDTH-20, 40), border_radius=10)
    status_text = font_medium.render(f"Статус: {ui_state.status}", True, ui_state.status_color)
    screen.blit(status_text, (20, 70))
    
    # Индикатор активации (только когда сказали "Кеша")
    if ui_state.is_wake_word_detected:
        pygame.draw.circle(screen, GREEN, (WIDTH - 30, 80), 8)
        active_text = font_small.render("Активен!", True, GREEN)
        screen.blit(active_text, (WIDTH - 80, 72))
    
    # Индикатор слушания (только после активации)
    if ui_state.is_listening and ui_state.is_wake_word_detected:
        # Анимированный индикатор
        size = 8 + int(ui_state.animation_counter % 3)
        pygame.draw.circle(screen, RED, (WIDTH - 80, 80), size)
        listen_text = font_small.render("Слушаю...", True, RED)
        screen.blit(listen_text, (WIDTH - 130, 72))
    
    # Последняя команда
    if ui_state.last_command:
        pygame.draw.rect(screen, WHITE, (10, 110, WIDTH-20, 30), border_radius=10)
        cmd_text = font_small.render(f"Последняя команда: {ui_state.last_command}", True, BLACK)
        screen.blit(cmd_text, (20, 115))
    
    # Область сообщений
    pygame.draw.rect(screen, WHITE, (10, 150, WIDTH-20, 150), border_radius=10)
    msg_title = font_medium.render("Диалог:", True, DARK_BLUE)
    screen.blit(msg_title, (20, 155))
    
    y_pos = 185
    for sender, message in ui_state.messages[-4:]:
        if sender == "Вы":
            color = BLUE
            prefix = "👤 "
        else:
            color = GREEN
            prefix = "🤖 "
        
        msg_text = font_small.render(f"{prefix}{message}", True, color)
        screen.blit(msg_text, (25, y_pos))
        y_pos += 25
    
    # Область команд
    pygame.draw.rect(screen, WHITE, (10, 310, WIDTH-20, 300), border_radius=10)
    commands_title = font_medium.render("📋 Доступные команды:", True, DARK_BLUE)
    screen.blit(commands_title, (20, 320))
    
    # Отображение команд постранично
    start_idx = ui_state.commands_page * 8
    end_idx = min(start_idx + 8, len(all_commands))
    
    y_pos = 355
    for i in range(start_idx, end_idx):
        command = all_commands[i]
        if command in COMMAND_CATEGORIES:
            # Это заголовок категории
            cat_text = font_medium.render(command, True, DARK_BLUE)
            screen.blit(cat_text, (25, y_pos))
            y_pos += 25
        else:
            # Это команда
            cmd_text = font_tiny.render(f"• {command}", True, BLACK)
            screen.blit(cmd_text, (35, y_pos))
            y_pos += 20
    
    # Навигация по страницам команд
    if ui_state.total_command_pages > 1:
        page_text = font_small.render(f"Страница {ui_state.commands_page + 1}/{ui_state.total_command_pages}", True, BLACK)
        screen.blit(page_text, (WIDTH - 160, 320))
        
        # Кнопки навигации (исправлены координаты)
        if ui_state.commands_page > 0:
            pygame.draw.rect(screen, BLUE, (WIDTH - 200, 315, 30, 25), border_radius=5)
            prev_text = font_small.render("←", True, WHITE)
            screen.blit(prev_text, (WIDTH - 190, 315))
        
        if ui_state.commands_page < ui_state.total_command_pages - 1:
            pygame.draw.rect(screen, BLUE, (WIDTH - 50, 315, 30, 25), border_radius=5)
            next_text = font_small.render("→", True, WHITE)
            screen.blit(next_text, (WIDTH - 40, 315))
    
    # Подсказки внизу
    pygame.draw.rect(screen, WHITE, (10, 620, WIDTH-20, 70), border_radius=10)
    tips = [
        "🗣️ Скажите: 'Кеша' для активации, затем команду",
        "⚡ Используйте кнопки ниже для управления"
    ]
    
    y_pos = 630
    for tip in tips:
        tip_text = font_small.render(tip, True, BLACK)
        screen.blit(tip_text, (20, y_pos))
        y_pos += 20
    
    # Кнопка выхода
    pygame.draw.rect(screen, RED, (WIDTH - 120, 635, 100, 30), border_radius=5)
    exit_text = font_small.render("Выход", True, WHITE)
    screen.blit(exit_text, (WIDTH - 95, 640))
    
    # Кнопка следующей страницы команд
    pygame.draw.rect(screen, BLUE, (WIDTH - 240, 635, 100, 30), border_radius=5)
    next_text = font_small.render("След. стр", True, WHITE)
    screen.blit(next_text, (WIDTH - 235, 640))
    
    # Кнопка предыдущей страницы
    pygame.draw.rect(screen, BLUE, (WIDTH - 360, 635, 100, 30), border_radius=5)
    prev_text = font_small.render("Пред. стр", True, WHITE)
    screen.blit(prev_text, (WIDTH - 355, 640))
    
    pygame.display.flip()
    ui_state.animation_counter += 0.5

def main():
    """Основная функция"""
    print("🚀 Голосовой помощник Кеша с интерфейсом активирован!")
    
    # Запуск потоков
    threading.Thread(target=listen_for_wake_word, daemon=True).start()
    threading.Thread(target=process_commands, daemon=True).start()
    
    # Главный цикл интерфейса
    running = True
    clock = pygame.time.Clock()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                
                # Кнопка выхода
                if WIDTH - 120 <= x <= WIDTH - 20 and 635 <= y <= 665:
                    re("Выключаюсь")
                    running = False
                
                # Кнопка следующей страницы команд (исправлены координаты)
                elif WIDTH - 240 <= x <= WIDTH - 140 and 635 <= y <= 665:
                    if ui_state.commands_page < ui_state.total_command_pages - 1:
                        ui_state.commands_page += 1
                
                # Кнопка предыдущей страницы команд (исправлены координаты)
                elif WIDTH - 360 <= x <= WIDTH - 260 and 635 <= y <= 665:
                    if ui_state.commands_page > 0:
                        ui_state.commands_page -= 1
                
                # Кнопки навигации в области команд (исправлены координаты)
                elif WIDTH - 200 <= x <= WIDTH - 170 and 315 <= y <= 340:
                    if ui_state.commands_page > 0:
                        ui_state.commands_page -= 1
                
                elif WIDTH - 50 <= x <= WIDTH - 20 and 315 <= y <= 340:
                    if ui_state.commands_page < ui_state.total_command_pages - 1:
                        ui_state.commands_page += 1
        
        draw_interface()
        clock.tick(30)
    
    pygame.quit()
    os._exit(0)

if __name__ == "__main__":
    main()
