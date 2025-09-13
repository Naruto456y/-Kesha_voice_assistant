"""Привет, Это голосовой помощник Кеша. Чтобы начать скачайте все необходимые библиотеки и запустите файл."""

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
from datetime import date, datetime, timedelta  

# Инициализация PyGame для интерфейса
pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Голосовой помощник Кеша")
icon = pygame.image.load(__file__.replace('Kesha.py','Kesha_icon.png.jpg')).convert_alpha()
pygame.display.set_icon(icon)


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
        self.dialog_scroll_offset = 0  # Смещение для прокрутки диалога
        self.commands_scroll_offset = 0  # Смещение для прокрутки команд

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
        "Моя волна - Включает вашу волну в яндекс  музыке",
        "Музыка [название] - Найти музыку в яндекс  музыке ",
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
        "Нарисуй [что-то] - Нарисовать",
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
    WAKE_WORDS = ['кеша', 'ке', 'гоша', 'кэш','валера','чебурек']
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
            if len(ui_state.messages) > 20:  # Увеличил буфер сообщений
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

    def listen(self, timeout=4):
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
                if len(ui_state.messages) > 20:  # Увеличил буфер сообщений
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
    """Обработка конкретной команда"""
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
        
        elif 'камер' in text:
            keyboard.send('win+2')
            re('Открываю')    
            
        elif 'селф' in text:
            keyboard.send('win+2')
            time.sleep(2)
            re('Улубнитесь!')
            time.sleep(1.5)
            keyboard.send('space')  
            
        elif 'сверн' in text:
            mouse.move(1422, 22)
            time.sleep(0.1) 
            mouse.click('left')  
        
        elif 'закр' in text:
            mouse.move(1513, 22)
            time.sleep(0.1) 
            mouse.click('left')    
        
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
            
        elif 'дз' in text or 'домашн' in text:
            webbrowser.open('https://school.mos.ru/diary/homeworks/homeworks/')
            re('Вот что задали')    
        
        elif 'расписан' in text:
            today = date.today()  
            tomorrow = today + timedelta(days=1)
            tomorrow = (str(tomorrow)).split('-')
            tomorrow = tomorrow[2] + '-' + tomorrow[1] + '-' + tomorrow[0]
            webbrowser.open(f'https://school.mos.ru/diary/schedules/day/?date={tomorrow}')
            re('Вот расписание на завтра')   
        
        elif 'телефон' in text:
            keyboard.send('Win + 3')
            time.sleep(3)
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
            
        elif 'запис' in text:
            keyboard.send('Win + 6')
            time.sleep(5)
            mouse.move(378, 600)
            time.sleep(0.1)
            re('Начинаю запись')
            time.sleep(1)
            mouse.click('left')
            
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
        
        elif 'нарисуй' in text:
            t = text.split('нарисуй')[1].strip()
            if t:
                webbrowser.open('https://alice.yandex.ru?')
                time.sleep(2)
                keyboard.write('нарисуй несколько вариантов ' + t)
                keyboard.send('Enter')
                re('Генирирую картинку')
            else:
                re('Уточните пожалуйста, что нарисовать?')
                
        elif 'включи свет' in text:
            webbrowser.open('https://alice.yandex.ru?')
            time.sleep(2)
            keyboard.write('Включи светильник')
            keyboard.send('Enter')
            re('Ок')
        
        elif 'выключи свет' in text:
            webbrowser.open('https://alice.yandex.ru?')
            time.sleep(2)
            keyboard.write('Выключи светильник')
            keyboard.send('Enter')
            re('Ок')
        
        elif 'браузер' in text:
            keyboard.send('Win + 9')
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
                a = q.split(' ')
                b = ''
                for i in a:
                    if not i == a[-1]:
                        b = b + i + '+'
                    else:
                        b = b + i
                webbrowser.open(f'https://music.yandex.ru/search?text={b}')
                time.sleep(3)
                re('Включаю')
                mouse.move(272, 262)
                time.sleep(0.1)
                mouse.click('left')
        elif 'волн' in text:
            AppOpener.open('Yandex',True)
            webbrowser.open('https://music.yandex.ru/')
            time.sleep(3)
            mouse.move(765, 334)
            time.sleep(0.1)
            mouse.click('left')
            re('Включаю вашу волну')

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

        elif 'время' in text or 'времени' in text:
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

def wrap_text(text, font, max_width):
    """Перенос текста на несколько строк, чтобы не выходил за границы"""
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        # Оцениваем ширину текста
        test_width = font.size(test_line)[0]
        if test_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

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
        screen.blit(active_text, (WIDTH - 120, 72))
    
    # Индикатор слушания (только после активации)
    if ui_state.is_listening and ui_state.is_wake_word_detected:
        # Анимированный индикатор
        size = 8 + int(ui_state.animation_counter % 3)
        pygame.draw.circle(screen, RED, (WIDTH - 150, 80), size)
        listen_text = font_small.render("Слушаю...", True, RED)
        screen.blit(listen_text, (WIDTH - 240, 72))
    
    # Последняя команда
    if ui_state.last_command:
        pygame.draw.rect(screen, WHITE, (10, 110, WIDTH-20, 30), border_radius=10)
        cmd_text = font_small.render(f"Последняя команда: {ui_state.last_command}", True, BLACK)
        screen.blit(cmd_text, (20, 115))
    
    # Область сообщений (поднята выше)
    pygame.draw.rect(screen, WHITE, (10, 150, WIDTH-20, 150), border_radius=10)
    msg_title = font_medium.render("Диалог:", True, DARK_BLUE)
    screen.blit(msg_title, (20, 155))
    
    # Отображение сообщений с прокруткой
    y_pos = 185
    visible_messages = ui_state.messages[ui_state.dialog_scroll_offset:]
    
    for sender, message in visible_messages:
        if y_pos > 280:  # Не выходить за границы области
            break
            
        if sender == "Вы":
            color = BLUE
            prefix = "👤 "
        else:
            color = GREEN
            prefix = "🤖 "
        
        # Перенос текста, чтобы не выходил за границы
        wrapped_lines = wrap_text(f"{prefix}{message}", font_small, WIDTH - 50)
        
        for line in wrapped_lines:
            if y_pos > 280:  # Не выходить за границы области
                break
            msg_text = font_small.render(line, True, color)
            screen.blit(msg_text, (25, y_pos))
            y_pos += 20
    
    # Область команд (поднята выше)
    pygame.draw.rect(screen, WHITE, (10, 310, WIDTH-20, 300), border_radius=10)
    commands_title = font_medium.render("📋 Доступные команды:", True, DARK_BLUE)
    screen.blit(commands_title, (20, 320))
    
    # Отображение команд с прокруткой
    start_idx = ui_state.commands_scroll_offset
    end_idx = min(start_idx + 12, len(all_commands))  # Больше команд на экран
    
    y_pos = 355
    for i in range(start_idx, end_idx):
        if y_pos > 590:  # Не выходить за границы области
            break
            
        command = all_commands[i]
        if command in COMMAND_CATEGORIES:
            # Это заголовок категории
            cat_text = font_medium.render(command, True, DARK_BLUE)
            screen.blit(cat_text, (25, y_pos))
            y_pos += 25
        else:
            # Это команда - переносим текст
            wrapped_lines = wrap_text(f"• {command}", font_tiny, WIDTH - 50)
            for line in wrapped_lines:
                if y_pos > 590:  # Не выходить за границы области
                    break
                cmd_text = font_tiny.render(line, True, BLACK)
                screen.blit(cmd_text, (35, y_pos))
                y_pos += 18
    
    # Индикатор прокрутки команд
    if len(all_commands) > 12:
        scroll_pos = int((ui_state.commands_scroll_offset / len(all_commands)) * 250)
        pygame.draw.rect(screen, GRAY, (WIDTH - 25, 355, 10, 250), border_radius=5)
        pygame.draw.rect(screen, BLUE, (WIDTH - 25, 355 + scroll_pos, 10, 30), border_radius=5)
    
    # Подсказки внизу
    pygame.draw.rect(screen, WHITE, (10, 620, WIDTH-20, 70), border_radius=10)
    tips = [
        "🗣️ Скажите: 'Кеша' для активации, затем команду",
        "⚡ Используйте колесо мыши или стрелки для прокрутки"
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
    
    # Кнопка прокрутки вниз
    pygame.draw.rect(screen, BLUE, (WIDTH - 240, 635, 100, 30), border_radius=5)
    down_text = font_small.render("Вниз", True, WHITE)
    screen.blit(down_text, (WIDTH - 220, 640))
    
    # Кнопка прокрутки вверх
    pygame.draw.rect(screen, BLUE, (WIDTH - 360, 635, 100, 30), border_radius=5)
    up_text = font_small.render("Вверх", True, WHITE)
    screen.blit(up_text, (WIDTH - 345, 640))
    
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
                
                # Кнопка прокрутки вниз
                elif WIDTH - 240 <= x <= WIDTH - 140 and 635 <= y <= 665:
                    if ui_state.commands_scroll_offset < len(all_commands) - 12:
                        ui_state.commands_scroll_offset += 1
                
                # Кнопка прокрутки вверх
                elif WIDTH - 360 <= x <= WIDTH - 260 and 635 <= y <= 665:
                    if ui_state.commands_scroll_offset > 0:
                        ui_state.commands_scroll_offset -= 1
            
            # Прокрутка колесом мыши
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:  # Прокрутка вверх
                    if ui_state.commands_scroll_offset > 0:
                        ui_state.commands_scroll_offset -= 1
                elif event.y < 0:  # Прокрутка вниз
                    if ui_state.commands_scroll_offset < len(all_commands) - 12:
                        ui_state.commands_scroll_offset += 1
            
            # Прокрутка стрелками клавиатуры
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if ui_state.commands_scroll_offset > 0:
                        ui_state.commands_scroll_offset -= 1
                elif event.key == pygame.K_DOWN:
                    if ui_state.commands_scroll_offset < len(all_commands) - 12:
                        ui_state.commands_scroll_offset += 1
                elif event.key == pygame.K_PAGEUP:
                    ui_state.commands_scroll_offset = max(0, ui_state.commands_scroll_offset - 5)
                elif event.key == pygame.K_PAGEDOWN:
                    ui_state.commands_scroll_offset = min(len(all_commands) - 12, ui_state.commands_scroll_offset + 5)
        
        draw_interface()
        clock.tick(30)
    
    pygame.quit()
    os._exit(0)

if __name__ == "__main__":
    main()