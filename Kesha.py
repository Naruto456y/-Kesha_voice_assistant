"""Голосовой помощник Кеша - финальная версия с улучшениями"""

import pygame
import speech_recognition as sr
from gtts import gTTS
import os
import time
import threading
import queue
import tempfile
import webbrowser
from datetime import datetime, timedelta, date
import psutil
import requests
from bs4 import BeautifulSoup
import keyboard
import mouse
import random
from urllib.parse import quote
from youtube_search import YoutubeSearch
import sys
import ctypes

# Импорты после установки
try:
    import AppOpener
except:
    pass

# Инициализация PyGame
pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Голосовой помощник Кеша")
try:
    if getattr(sys, 'frozen', False):
        # Если собрано в exe
        icon_path = os.path.join(sys._MEIPASS, 'Kesha_icoc.jpeg')
    else:
        # Если запуск из кода
        icon_path = __file__.replace("Kesha.py", 'Kesha_icoc.jpeg')
    
    icon = pygame.image.load(icon_path).convert()
    pygame.display.set_icon(icon)
except:
    print("Не удалось загрузить иконку")
    pass

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
LIGHT_GREEN = (144, 238, 144)

# Шрифты
font_large = pygame.font.SysFont('Times New Roman', 32)
font_medium = pygame.font.SysFont('Times New Roman', 20)
font_small = pygame.font.SysFont('Times New Roman', 16)
font_tiny = pygame.font.SysFont('Times New Roman', 14)

# Состояние интерфейса
class UIState:
    def __init__(self):
        self.is_listening = False
        self.is_wake_word_detected = False
        self.last_command = ""
        self.status = "Готов к работе"
        self.status_color = GREEN
        self.messages = []
        self.commands_scroll_offset = 0
        self.dialog_scroll_offset = 0
        self.animation_counter = 0
        self.max_dialog_messages = 50
        self.active_scroll_area = None  # 'dialog' или 'commands'

ui_state = UIState()

# Варианты ответов Кеши
RESPONSE_VARIANTS = {
    'ok': ['Принял!', 'Выполняю!', 'Сделано!', 'Уже делаю!', 'Есть!', 'Оброботал!'],
    'search': ['Ищу информацию...', 'Начинаю поиск...', 'Секунду...', 'Ищу в интернете...'],
    'open': ['Открываю...', 'Запускаю...', 'Выполняю...', 'Сейчас открою...'],
    'error': ['Не удалось выполнить', 'Возникла проблема', 'Не получилось', 'Ошибка выполнения'],
    'thanks': ['Всегда пожалуйста!', 'Рад помочь!', 'Обращайтесь!', 'К вашим услугам!']
}

# Полный список комманд 

COMMAND_CATEGORIES = {
    "🎯 Основные команды": [
        "Кеша привет - Поприветствовать",
        "Кеша как дела - Узнать состояние", 
        "Кеша молодец - Похвалить",
        "Кеша пока/стоп/выход - Завершить работу"
    ],
    "🌐 Интернет и поиск": [
        "Кеша найди [запрос] - Поиск в интернете",
        "Кеша найди в ютуби [запрос] - Поиск на YouTube",
        "Кеша youtube - Открыть YouTube",
        "Кеша игры - Открыть Яндекс Игры",
        "Кеша погода - Узнать погоду",
        "Кеша переводчик - Открыть переводчик",
        "Кеша дипси - Открыть нейросеть DeepSeek"
    ],
    "🎮 Игры": [
        "Кеша камень ножницы бумага - Запустить игру",
        "Кеша виселица - Запустить игру", 
        "Кеша викторина - Запустить игру",
        "Кеша квест - Запустить игру",
        "Кеша крестики-нолики - Запустить игру",
        "Кеша угадай число - Запустить игру"
    ],
    "💻 Система и приложения": [
        "Кеша открой [приложение] - Открыть программу",
        "Кеша закрой [приложение] - Закрыть программу",
        "Кеша открой проводник - Открыть файловый менеджер",
        "Кеша открой настройки - Открыть настройки системы",
        "Кеша сверни окно - Свернуть текущее окно",
        "Кеша закрой окно - Закрыть текущее окно",
        "Кеша открой roblox - Запустить Roblox",
        "Кеша открой minecraft - Запустить Minecraft",
        "Кеша камера - Открыть камеру",
        "Кеша селфи - Сделать селфи",
        "Кеша браузер - Открыть браузер"
        "Кеша левый/правый клик - Клик мышью",
    ],
    "🎵 Медиа и управление": [
        "Кеша музыка [название] - Найти музыку",
        "Кеша моя волна - Включить мою волну",
        "Кеша пауза/стоп - Поставить на паузу",
        "Кеша дальше/следующий - Следующий трек",
        "Кеша предыдущий/прошлый - Предыдущий трек",
        "Кеша лайк/нравится - Добавить в избранное",
        "Кеша дизлайк/не нравится - Убрать из рекомендаций",
        "Кеша громче - Увеличить громкость",
        "Кеша тише - Уменьшить громкость",
        "Кеша громкость [1-100] - Установить громкость"
    ],
    "⚙️ Системная информация": [
        "Кеша время - Текущее время",
        "Кеша состояние батареи - Информация о батарее",
        "Кеша выключи компьютер - Выключить ПК",
        "Кеша перезагрузка - Перезагрузить компьютер"
        "Кеша спящий режим - Включить спящий режим",
    ],
    "📚 Учеба": [
        "Кеша дз/домашнее - Показать домашнее задание",
        "Кеша оценки - Показать оценки",
        "Кеша расписание - Расписание на завтра"
    ],
    "🔧 Специальные команды": [
        "Кеша переведи на английский [текст] - Перевод",
        "Кеша переведи на русский [текст] - Перевод",
        "Кеша нарисуй [что-то] - Нарисовать",
        "Кеша включи свет - Умный дом",
        "Кеша выключи свет - Умный дом",
        "Кеша вниз - Скролл вниз",
        "Кеша верх - Скролл вверх",
        "Кеша поставь таймер на [минуты] - Таймер",
        "Кеша телефон - Совершить звонок",
        "Кеша пробел - Нажать пробел"
        "Кеша Bluetooth - Преключить Bluetooth"
    ]
}

all_commands = []
for category, commands in COMMAND_CATEGORIES.items():
    all_commands.append(category)
    all_commands.extend(commands)

# Инициализация аудио
pygame.mixer.init()
TEMP_DIR = tempfile.gettempdir()
command_queue = queue.Queue()

class ImprovedVoiceRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 400
        self.recognizer.pause_threshold = 0.8
        self.recognizer.dynamic_energy_threshold = True
        
        # Добавляем метод калибровки шума
        self.adjust_noise()

    def adjust_noise(self):
        with sr.Microphone() as source:
            print("Калибровка шума...")
            # Увеличиваем длительность калибровки до 3 секунд
            self.recognizer.adjust_for_ambient_noise(source, duration=3)
            print("Калибровка завершена")

    def listen(self, timeout=5):
        try:
            # Добавляем повтор калибровки каждые 30 минут
            if not hasattr(self, 'last_calibration') or (time.time() - self.last_calibration) > 1800:
                self.adjust_noise()
                self.last_calibration = time.time()
            with sr.Microphone() as source:
                ui_state.is_listening = True
                ui_state.status = "Слушаю..."
                ui_state.status_color = BLUE
                
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,
                    phrase_time_limit=5
                )
                
            text = self.recognizer.recognize_google(audio, language='ru-RU').lower()
            
            if text and any(word in text for word in ['кеша', 'кеш', 'гоша']):
                ui_state.messages.append(("Вы", text))
                if len(ui_state.messages) > ui_state.max_dialog_messages:
                    ui_state.messages.pop(0)
                    
            return text
            
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            return ""
        finally:
            ui_state.is_listening = False
            ui_state.status = "Готов к работе"
            ui_state.status_color = GREEN


class AudioManager:
    def __init__(self):
        self.is_speaking = False
        self.playback_thread = None

    def say(self, text):
        if not text.strip():
            return

        try:
            # Добавляем ответ в диалог
            ui_state.messages.append(("Кеша", text))
            if len(ui_state.messages) > ui_state.max_dialog_messages:
                ui_state.messages.pop(0)
                
            filename = os.path.join(TEMP_DIR, f"voice_{int(time.time()*1000)}.mp3")
            tts = gTTS(text=text, lang='ru', slow=False)
            tts.save(filename)

            if self.playback_thread and self.playback_thread.is_alive():
                pygame.mixer.music.stop()
                self.playback_thread.join(timeout=0.1)

            self.is_speaking = True
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()

            self.playback_thread = threading.Thread(
                target=self._cleanup_audio,
                args=(filename,),
                daemon=True
            )
            self.playback_thread.start()

        except Exception as e:
            pass
    def _cleanup_audio(self, filename):
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except:
            pass
        self.is_speaking = False

audio_manager = AudioManager()

def get_random_response(response_type):
    """Получить случайный вариант ответа"""
    variants = RESPONSE_VARIANTS.get(response_type, ['Выполняю!'])
    return random.choice(variants)

def get_layout():
    u = ctypes.windll.LoadLibrary("user32.dll")
    pf = getattr(u, "GetKeyboardLayout")
    if hex(pf(0)) == '0x4190419':
        return False
    if hex(pf(0)) == '0x4090409':
        return True

def rec(text):
    """Озвучивание текста с выводом в консоль"""
    audio_manager.say(text)

def start(name):
    """Открывает файл в папке с программой"""
    try:
        if getattr(sys, 'frozen', False):
            # Если приложение собрано в exe
            base_path = sys._MEIPASS
        else:
            # Если запуск из исходного кода
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        file_path = os.path.join(base_path, name)
        os.startfile(file_path)
        return True
    except Exception as e:
        print(f"Ошибка запуска {name}: {e}")
        return False

def get_text_with_url(api="28c9d95c5e0b423d23e81c1d43c10cf0", city="Москва"):
        # URL API
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api}&units=metric&lang=ru"
    
        try:
            # Отправляем запрос с таймаутом
            response = requests.get(url, timeout=10)
            response.raise_for_status()
    
            data = response.json()
            
            # Извлекаем данные (они уже числа)
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            description = data["weather"][0]["description"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]
    
            # Преобразуем числа в строки для конкатенации
            result = {
                "Температура": f"{temp} °C",
                "Ощущается как": f"{feels_like} °C",
                "Описание": description,
                "Влажность": f"{humidity} %",
                "Скорость ветра": f"{wind_speed} м/с"
            }
            return result['Температура']
            
        except requests.exceptions.RequestException as e:
            return f"Ошибка запроса: {str(e)}"
        except Exception as e:
            return f"Произошла ошибка: {str(e)}"
def search_and_open_youtube(query):
    """Поиск и открытие видео на YouTube"""
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if results:
            video_url = f"https://youtube.com{results[0]['url_suffix']}"
            webbrowser.open(video_url)
            return True
        return False
    except:
        return False

def set_system_volume(level):
    """Установка громкости системы"""
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume_control = cast(interface, POINTER(IAudioEndpointVolume))
        volume_control.SetMasterVolumeLevelScalar(level, None)
        return True
    except:
        return False
def get_system_volume():
    """Получение текущей громкости"""
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume_control = cast(interface, POINTER(IAudioEndpointVolume))
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

def listen_for_wake_word():
    """Прослушивание ключевых слов"""
    recognizer = ImprovedVoiceRecognizer()
    rec("Готов к работе! Говорите 'Кеша' и команду")
    
    WAKE_WORDS = ['кеша', 'кеш', 'гоша', 'кэш', 'валера', 'чебурек', 'алиса', 'сири']
    
    while True:
        try:
            # Ждем, пока Кеша закончит говорить
            while audio_manager.is_speaking:
                time.sleep(0.1)
                
            text = recognizer.listen(timeout=10)
            
            if text and any(word in text for word in WAKE_WORDS):
                ui_state.is_wake_word_detected = True
                ui_state.status = "Команда получена"
                ui_state.status_color = GREEN
                
                # Очищаем команду от ключевых слов
                clean_command = text
                for word in WAKE_WORDS:
                    clean_command = clean_command.replace(word, '').strip()
                
                if clean_command:
                    command_queue.put(("voice_command", clean_command))
                    time.sleep(0.5)
                else:
                    # Если только ключевое слово без команды
                    rec("Слушаю вас!")
                
                ui_state.is_wake_word_detected = False
                
        except Exception as e:
            time.sleep(0.5)

def process_commands():
    while True:
        try:
            command_type, command_data = command_queue.get()
            if command_type == "voice_command":
                # Обработка в отдельном потоке
                threading.Thread(
                    target=handle_command, 
                    args=(command_data,), 
                    daemon=True
                ).start()
        except Exception as e:
            print(f"Ошибка обработки команды: {e}")

def handle_command(text):
    """Обработка конкретной команды"""
    text = text.lower().strip()
    try:
        try:
            # Основные команды
            if any(word in text for word in ['пока', 'выход', 'стоп', 'выключись']):
                rec('До свидания! Рад был помочь!')
                time.sleep(2)
                os._exit(0)

            elif 'привет' in text:
                rec('Приветствую! Чем могу быть полезен?')

            elif 'как дела' in text:
                rec('Всё отлично! Готов к работе и жду ваших команд!')

            elif 'молодец' in text:
                rec(get_random_response('thanks'))

            # Интернет и поиск
            elif 'найди в ютуби' in text:
                query = text.replace("найди в ютуби", "").strip()
                if query:
                    if search_and_open_youtube(query):
                        rec('Вот что я нашёл')
                    else:
                        rec("Не удалось найти видео")
                else:
                    rec("Уточните, что искать?")

            elif 'youtube' in text:
                webbrowser.open('https://www.youtube.com/')
                rec(get_random_response('open'))

            elif 'найди' in text:
                query = text.replace("найди", "").strip()
                if query:
                    webbrowser.open(f'https://yandex.ru/search/?text={query}')
                    rec(get_random_response('search'))
                else:
                    rec("Что именно найти?")

            elif 'погод' in text:
                weather = get_text_with_url()
                rec(f"Погода: {weather}")

            elif 'дипси' in text or 'deepseek' in text:
                webbrowser.open('https://chat.deepseek.com/')
                rec("Открываю DeepSeek")

            elif 'переводчик' in text:
                webbrowser.open('https://translate.yandex.ru/')
                rec(get_random_response('open'))
            
            elif 'bluetooth' in text:
                keyboard.send('win + a')
                time.sleep(0.2)
                keyboard.send('right')
                time.sleep(0.1)
                keyboard.send('enter')
                time.sleep(0.1)
                keyboard.send('win + a')
                rec("Переключаю Bluetooth")
                
            # Игры

            elif 'игры' in text:
                webbrowser.open('https://yandex.ru/games/')
                rec("Открываю Яндекс Игры")

            elif 'камень ножницы бумага' in text:
                if start(r'games\stone_knots_paper.py'):
                    rec("Запускаю игру")
                else:
                    rec("Файл игры не найден")

            elif 'виселиц' in text:
                if start(r'games\hangman.py'):
                    rec("Запускаю игру")
                else:
                    rec("Файл игры не найден")

            elif 'викторин' in text:
                if start(r'games\quiz.py'):
                    rec("Запускаю игру") 
                else:
                    rec("Файл игры не найден")

            elif 'квест' in text:
                if start(r'games\quest.py'):
                    rec("Запускаю игру")
                else:
                    rec("Файл игры не найден")

            elif 'крестики-нолики' in text:
                if start(r'games\tictactoe.py'):
                    rec("Запускаю игру")
                else:
                    rec("Файл игры не найден")

            elif 'угадай число' in text:
                if start(r'games\rand_game.py'):
                    rec("Запускаю игру")
                else:
                    rec("Файл игры не найден")

            # Система
            elif 'открой roblox' in text:
                try:
                    a = __file__.split('\\')
                    b = a[0] + '\\' + a[1] + '\\' + a[2] + '\\OneDrive\\Рабочий стол\\Roblox Player.lnk'
                    os.startfile(b)
                    rec(get_random_response('open'))
                except:
                    rec("Не удалось открыть Roblox")

            elif 'ухож' in text or 'ушол' in text:
                webbrowser.open('https://alice.yandex.ru?')
                time.sleep(2)
                keyboard.write('Выключи светильник')
                keyboard.send('Enter')
                os.system("shutdown /s /t 10")
                rec("Выключаю компьютер и свет досвидания!")

            elif 'открой minecraft' in text:
                try:
                    a = __file__.split('\\')
                    b = a[0] + '\\' + a[1] + '\\' + a[2] + '\\OneDrive\\Рабочий стол\\МАЕНКРАФТ.exe'
                    os.startfile(b)
                    rec(get_random_response('open'))
                except:
                    rec("Не удалось открыть Minecraft")

            elif 'вниз' in text:
                mouse.wheel(-1)
                                                                                                                                                                                                                                                                                                                                                                                                    
            elif 'верх' in text:
                mouse.wheel(1)

            elif 'камер' in text:
                keyboard.send('win+2')
                rec(get_random_response('open'))

            elif 'селф' in text:
                keyboard.send('win+2')
                time.sleep(2)
                rec('Улубнитесь!')
                time.sleep(1.5)
                keyboard.send('space')

            elif 'сверн' in text:
                keyboard.send('Win + down')
                time.sleep(0.001)
                keyboard.send('Win + down')
                rec(get_random_response('ok'))

            elif 'закр' in text:
                keyboard.send('alt+F4')
                rec(get_random_response('ok'))
            
            elif 'открой проводник' in text:
                keyboard.send('win + e')
                rec(get_random_response('ok'))

            elif 'открой настройки' in text:
                keyboard.send('win + i')
                rec(get_random_response('ok'))

            # Медиа
            elif 'музык' in text:
                query = text.replace("музык", "").replace("а", "").replace("у", "").strip()
                if query:
                    try:
                        AppOpener.open('Yandex', True)
                        a = query.split(' ')
                        b = '+'.join(a)
                        webbrowser.open(f'https://music.yandex.ru/search?text={b}')
                        time.sleep(3)
                        rec('Включаю')
                        time.sleep(1)
                        mouse.move(259, 266)
                        time.sleep(0.1)
                        mouse.click('left')
                    except:
                        rec("Ошибка при открытии музыки")
                else:
                    rec("Какую музыку найти?")

            elif 'вол' in text or 'избр' in text:
                try:
                    AppOpener.open('Yandex', True)
                    webbrowser.open('https://music.yandex.ru/')
                    time.sleep(3.5)
                    rec('Включаю вашу волну')
                    time.sleep(0.5)
                    keyboard.send('K')
                except:
                    rec("Ошибка при открытии музыки")

            elif any(word in text for word in ['дальше', 'след', 'продол']):
                time.sleep(0.5)
                keyboard.send('n')
                rec(get_random_response('ok'))

            elif any(word in text for word in ['стоп', 'пауз', 'заткн']):
                time.sleep(0.5)
                keyboard.send('k')
                rec(get_random_response('ok'))

            elif any(word in text for word in ['пред', 'прошл', 'назад']):
                time.sleep(0.5)
                keyboard.send('p')
                rec(get_random_response('ok'))

            elif 'лайк' in text or 'нравит' in text:
                time.sleep(0.5)
                keyboard.send('f')
                time.sleep(0.5)
                rec('Ок, добавил в избранное!')

            elif any(word in text for word in ['дизлайк', 'не нравит']):
                time.sleep(0.5)
                keyboard.send('d')
                rec('Ок, больше не буду включать такое')

            # Системная информация
            elif 'врем' in text:
                current_time = datetime.now().strftime("%H:%M")
                rec(f"Сейчас {current_time}")

            elif 'батар' in text:
                battery = psutil.sensors_battery()
                if battery:
                    status = "заряжается" if battery.power_plugged else "не заряжается"
                    rec(f"Батарея {status}. Уровень: {battery.percent}%")
                else:
                    rec("Информация о батарее недоступна")

            elif 'выкл' in text and 'комп' in text:
                rec("Выключаю компьютер через 10 секунд")
                os.system("shutdown /s /t 10")

            # Учеба
            elif any(word in text for word in ['дз', 'домашн']):
                webbrowser.open('https://school.mos.ru/diary/homeworks/')
                rec("Открываю домашнее задание")

            elif 'оценк' in text:
                webbrowser.open('https://school.mos.ru/diary/marks/current-marks')
                rec("Показываю оценки")

            elif 'расписан' in text:
                tomorrow = date.today() + timedelta(days=1)
                tomorrow_str = tomorrow.strftime("%d-%m-%Y")
                webbrowser.open(f'https://school.mos.ru/diary/schedules/day/?date={tomorrow_str}')
                rec("Показываю расписание на завтра")
            
            # Специальные команды
            elif 'переведи на английский' in text:
                text_to_translate = text.replace("переведи на английский", "").strip()
                if text_to_translate:
                    webbrowser.open(f'https://translate.yandex.ru/?lang=ru-en&text={text_to_translate}')
                    rec("Открываю переводчик")
                else:
                    rec("Что перевести?")
            
            elif 'спящий' in text:
                keyboard.send('Win + m')
                time.sleep(1)
                keyboard.send('alt + F4')
                time.sleep(0.1)
                keyboard.send('up')
                time.sleep(0.1)
                keyboard.send('enter')

            elif 'переведи на русский' in text:
                text_to_translate = text.replace("переведи на русский", "").strip()
                if text_to_translate:
                    webbrowser.open(f'https://translate.yandex.ru/?lang=en-ru&text={text_to_translate}')
                    rec("Открываю переводчик")
                else:
                    rec("Что перевести?")

            elif 'нарисуй' in text:
                query = text.replace("нарисуй", "").strip()
                if query:
                    webbrowser.open(f'https://yandex.ru/images/search?text={query}')
                    rec("Ищу изображения...")
                else:
                    rec("Что нарисовать?")

            elif 'включи свет' in text:
                webbrowser.open('https://alice.yandex.ru/?')
                time.sleep(2)
                keyboard.write('Включи светильник')
                keyboard.send('Enter')
                rec(get_random_response('ok'))

            elif 'выключи свет' in text:
                webbrowser.open('https://alice.yandex.ru/?')
                time.sleep(2)
                keyboard.write('Выключи светильник')
                keyboard.send('Enter')
                rec(get_random_response('ok'))

            elif 'браузер' in text:
                AppOpener.open('yandex', True)
                time.sleep(0.1)
                keyboard.send('WIN + UP')
                rec(get_random_response('ok'))
                
            elif 'левый' in text:
                mouse.click('left')
            
            elif 'прав'  in text:
                mouse.click('right')

            elif 'заблок' in text and 'комп' in text:
                keyboard.send('Win + m')
                time.sleep(0.2)
                keyboard.send('alt + F4')
                time.sleep(0.1)
                for i in range(3): keyboard.send('up')
                time.sleep(0.01)
                keyboard.send('enter')

            elif 'телефон' in text:
                keyboard.send('Win + 3')
                time.sleep(4)
                mouse.move(299, 180)
                time.sleep(0.1)
                mouse.click('left')
                time.sleep(0.1)
                mouse.move(350, 129)
                time.sleep(0.1)
                mouse.click('left')
                rec('Уже звоню ищите')

            elif 'поставь таймер на' in text:
                w = text.replace("поставь таймер на", "").strip()
                w = w.replace("минуту", "").replace("минут", "").replace("ы", "").strip()
                if w and w.isdigit():
                    if start(r'Media\timer.py'):
                        time.sleep(3)
                        keyboard.write(w)
                        keyboard.send('Enter')
                        rec('Таймер успешно запущен')
                    else:
                        rec("Файл таймера не найден")
                else:
                    rec('Уточните на сколько поставить таймер')

            # Управление громкостью
            elif any(word in text for word in ['громче', 'увеличь громкость']):
                new_vol = change_volume('up')
                rec(f'Громкость увеличена до {int(new_vol * 100)}%')

            elif any(word in text for word in ['тише', 'уменьши громкость']):
                new_vol = change_volume('down')
                rec(f'Громкость уменьшена до {int(new_vol * 100)}%')
            
            elif 'перезагруз' in text:
                keyboard.send('Win + m')
                time.sleep(0.2)
                keyboard.send('alt + F4')
                time.sleep(0.1)
                keyboard.send('down')
                time.sleep(0.1)
                keyboard.send('enter')
                rec("Перезагружаю компьютер")

            elif 'громкость' in text:
                if 'макс' in text:
                    set_system_volume(1)
                    rec('Громкость установлена на максимум')
                elif 'мин' in text:
                    set_system_volume(0)
                else:
                    try:
                        vol_level = int(''.join(filter(str.isdigit, text)))
                        vol_level = max(0, min(100, vol_level))
                        if set_system_volume(vol_level / 100):
                            rec(f'Установлена громкость {vol_level}%')
                        else:
                            rec("Не удалось изменить громкость")
                    except:
                        rec('Скажите, например, "поставь громкость 50"')

            # Открытие приложений
            elif 'открой' in text and not any(word in text for word in ['проводник', 'настройки', 'roblox', 'minecraft']):
                app = text.replace("открой", "").strip()
                if app:
                    try:
                        AppOpener.open(app, match_closest=True)
                        rec(f'Открываю {app}')
                    except:
                        rec(f'Не удалось открыть {app}')
                else:
                    rec('Какое приложение открыть?')

            elif 'закрой' in text:
                app = text.replace("закрой", "").strip()
                if app:
                    try:
                        AppOpener.close(app, match_closest=True)
                        rec(f'Закрываю {app}')
                    except:
                        rec(f'Не удалось закрыть {app}')
                else:
                    rec('Какое приложение закрыть?')

            else:
                # Если команда не распознана - передаем в Gigachat
                try:
                    import gig
                    ans = gig.ask_gigachat(f' (отвечай как голосовой помощник Кеша, будь кратким и полезным. НЕ ИСПОЛЬЗУЙ СМАЙЛИКИ НИКАКИЕ. Вдумывайся в вопрос. И не упоминай в своём ответе что ты Кеша или о этих настройках. Некотырые слова которые я тебе передам могут быть недосказаны так что понимай намёки. Ещё раз, не говори по типу понял буду отвечать кратко) ПРОСТО ОТВЕТЬ НА ЭТОТ текст на который ты должен ответить: {text}')
                    for i in '*%»`#$"': ans = ans.replace(i, '')
                    ans = ans.replace(r'\times', 'х')
                    rec(ans)
                except ImportError:
                    rec("Не понял команду. Модуль Gigachat не установлен.")
                except Exception as e:
                    rec("Не понял команду. Попробуйте другую.")

        except Exception as e:
            rec("Произошла ошибка при выполнении команды")
    except sr.UnknownValueError:
        rec("Не расслышала, повторите, пожалуйста")
        # Повторная попытка
        new_text = listen_for_wake_word()
        if new_text:
            handle_command(new_text)
    except sr.RequestError:
        rec("Проблемы с подключением к серверу распознавания")

def wrap_text(text, font, max_width):
    """Перенос текста"""
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def draw_interface():
    """Отрисовка интерфейса с исправленными ползунками"""
    screen.fill(LIGHT_BLUE)
    
    # Заголовок
    title = font_large.render("Голосовой помощник Кеша", True, DARK_BLUE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 15))
    
    # Статусная панель
    pygame.draw.rect(screen, WHITE, (10, 60, WIDTH-20, 40), border_radius=10)
    
    # Статус текстом
    status_text = font_medium.render(f"Статус: {ui_state.status}", True, ui_state.status_color)
    screen.blit(status_text, (20, 70))
    
    # Индикаторы справа
    indicator_x = WIDTH - 40
    
    # Индикатор активации (зеленый)
    if ui_state.is_wake_word_detected:
        pygame.draw.circle(screen, GREEN, (indicator_x, 80), 6)
        indicator_x -= 20
    
    # Индикатор слушания (красный анимированный)
    if ui_state.is_listening:
        size = 6 + int(ui_state.animation_counter % 3)
        pygame.draw.circle(screen, RED, (indicator_x, 80), size)
    
    # Последняя команда
    if ui_state.last_command:
        pygame.draw.rect(screen, WHITE, (10, 110, WIDTH-20, 30), border_radius=10)
        # Обрезаем длинные команды
        cmd_display = ui_state.last_command
        if font_small.size(cmd_display)[0] > WIDTH - 50:
            for i in range(len(cmd_display)-3, 0, -1):
                if font_small.size(cmd_display[:i] + "...")[0] <= WIDTH - 50:
                    cmd_display = cmd_display[:i] + "..."
                    break
        cmd_text = font_small.render(f"Команда: {cmd_display}", True, BLACK)
        screen.blit(cmd_text, (20, 115))
    
    # Диалоговое окно
    pygame.draw.rect(screen, WHITE, (10, 150, WIDTH-20, 200), border_radius=10)
    dialog_title = font_medium.render("💬 Диалог:", True, DARK_BLUE)
    screen.blit(dialog_title, (20, 160))
    
    # Отображение диалога с прокруткой
    y_pos = 190
    visible_messages = ui_state.messages[ui_state.dialog_scroll_offset:ui_state.dialog_scroll_offset + 6]
    
    for sender, message in visible_messages:
        if y_pos > 330:
            break
            
        color = BLUE if sender == "Вы" else GREEN
        prefix = "👤 " if sender == "Вы" else "🤖 "
        
        # Обрезаем длинные сообщения
        display_message = f"{prefix}{message}"
        if font_small.size(display_message)[0] > WIDTH - 80:
            for i in range(len(display_message)-3, 0, -1):
                if font_small.size(display_message[:i] + "...")[0] <= WIDTH - 80:
                    display_message = display_message[:i] + "..."
                    break
        
        msg_text = font_small.render(display_message, True, color)
        screen.blit(msg_text, (25, y_pos))
        y_pos += 20
    
    # Ползунок диалога (ИСПРАВЛЕНО - правильные границы)
    if len(ui_state.messages) > 6:
        max_dialog_scroll = max(0, len(ui_state.messages) - 6)
        scroll_ratio = ui_state.dialog_scroll_offset / max_dialog_scroll if max_dialog_scroll > 0 else 0
        
        # Область прокрутки диалога
        scroll_area_height = 130  # Высота области прокрутки
        scroll_area_y = 190       # Начало области прокрутки
        
        # Вычисляем позицию ползунка с учетом границ
        scroll_pos = scroll_area_y + int(scroll_ratio * (scroll_area_height - 20))  # -20 для высоты ползунка
        
        # Ограничиваем позицию ползунка
        scroll_pos = max(scroll_area_y, min(scroll_pos, scroll_area_y + scroll_area_height - 20))
        
        # Фон ползунка
        pygame.draw.rect(screen, GRAY, (WIDTH - 35, scroll_area_y, 10, scroll_area_height), border_radius=5)
        # Ползунок
        pygame.draw.rect(screen, BLUE, (WIDTH - 35, scroll_pos, 10, 20), border_radius=5)
    
    # Область команд
    pygame.draw.rect(screen, WHITE, (10, 360, WIDTH-20, 280), border_radius=10)
    commands_title = font_medium.render("📋 Команды:", True, DARK_BLUE)
    screen.blit(commands_title, (20, 370))
    
    # Прокрутка команд с обрезкой длинного текста
    start_idx = ui_state.commands_scroll_offset
    end_idx = min(start_idx + 8, len(all_commands))
    
    y_pos = 405
    for i in range(start_idx, end_idx):
        if y_pos > 620:
            break
            
        command = all_commands[i]
        if command in COMMAND_CATEGORIES:
            # Заголовок категории - обрезаем если слишком длинный
            display_text = command
            if font_medium.size(command)[0] > WIDTH - 100:
                for j in range(len(command)-3, 0, -1):
                    if font_medium.size(command[:j] + "...")[0] <= WIDTH - 100:
                        display_text = command[:j] + "..."
                        break
            cat_text = font_medium.render(display_text, True, DARK_BLUE)
            screen.blit(cat_text, (25, y_pos))
            y_pos += 25
        else:
            # Команда - обрезаем если слишком длинная
            display_text = f"• {command}"
            if font_small.size(display_text)[0] > WIDTH - 100:
                for j in range(len(display_text)-3, 0, -1):
                    if font_small.size(display_text[:j] + "...")[0] <= WIDTH - 100:
                        display_text = display_text[:j] + "..."
                        break
            cmd_text = font_small.render(display_text, True, BLACK)
            screen.blit(cmd_text, (35, y_pos))
            y_pos += 20
    
    # Ползунок команд (ИСПРАВЛЕНО - правильные границы)
    if len(all_commands) > 8:
        max_commands_scroll = max(0, len(all_commands) - 8)
        scroll_ratio = ui_state.commands_scroll_offset / max_commands_scroll if max_commands_scroll > 0 else 0
        
        # Область прокрутки команд
        scroll_area_height = 215  # Высота области прокрутки
        scroll_area_y = 405       # Начало области прокрутки
        
        # Вычисляем позицию ползунка с учетом границ
        scroll_pos = scroll_area_y + int(scroll_ratio * (scroll_area_height - 30))  # -30 для высоты ползунка
        
        # Ограничиваем позицию ползунка
        scroll_pos = max(scroll_area_y, min(scroll_pos, scroll_area_y + scroll_area_height - 30))
        
        # Фон ползунка
        pygame.draw.rect(screen, GRAY, (WIDTH - 35, scroll_area_y, 10, scroll_area_height), border_radius=5)
        # Ползунок
        pygame.draw.rect(screen, BLUE, (WIDTH - 35, scroll_pos, 10, 30), border_radius=5)
    
    # Подсказки и управление
    pygame.draw.rect(screen, WHITE, (10, 650, WIDTH-20, 40), border_radius=10)
    
    tips = [
        "🗣️ Говорите: 'Кеша [команда]'",
        "🖱️ Наведите курсор и крутите колесо мыши",
    ]
    
    y_pos = 650
    for tip in tips:
        tip_text = font_small.render(tip, True, BLACK)
        screen.blit(tip_text, (20, y_pos))
        y_pos += 20
    
    # Кнопка выхода
    pygame.draw.rect(screen, RED, (WIDTH - 100, 655, 80, 30), border_radius=5)
    exit_text = font_small.render("Выход", True, WHITE)
    screen.blit(exit_text, (WIDTH - 85, 660))
    
    pygame.display.flip()
    ui_state.animation_counter += 0.3

def main():
    """Основная функция"""
    
    # Запуск потоков
    threading.Thread(target=listen_for_wake_word, daemon=True).start()
    threading.Thread(target=process_commands, daemon=True).start()
    
    # Главный цикл
    running = True
    clock = pygame.time.Clock()
    
    while running:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Определяем активную область прокрутки
        ui_state.active_scroll_area = None
        if 10 <= mouse_x <= WIDTH-10:
            if 150 <= mouse_y <= 350:  # Диалог
                ui_state.active_scroll_area = 'dialog'
            elif 360 <= mouse_y <= 640:  # Команды
                ui_state.active_scroll_area = 'commands'
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                
                # Кнопка выхода
                if WIDTH - 100 <= x <= WIDTH - 20 and 655 <= y <= 685:
                    rec("До свидания!")
                    time.sleep(1)
                    running = False
            
            elif event.type == pygame.MOUSEWHEEL:
                # Автоматическое определение области прокрутки
                if ui_state.active_scroll_area == 'dialog':
                    # Прокрутка диалога
                    if event.y > 0 and ui_state.dialog_scroll_offset > 0:
                        ui_state.dialog_scroll_offset -= 1
                    elif event.y < 0 and ui_state.dialog_scroll_offset < len(ui_state.messages) - 6:
                        ui_state.dialog_scroll_offset += 1
                
                elif ui_state.active_scroll_area == 'commands':
                    # Прокрутка команд
                    if event.y > 0 and ui_state.commands_scroll_offset > 0:
                        ui_state.commands_scroll_offset -= 1
                    elif event.y < 0 and ui_state.commands_scroll_offset < len(all_commands) - 8:
                        ui_state.commands_scroll_offset += 1
            
            elif event.type == pygame.KEYDOWN:
                # Управление стрелками
                if event.key == pygame.K_UP:
                    if ui_state.dialog_scroll_offset > 0:
                        ui_state.dialog_scroll_offset -= 1
                elif event.key == pygame.K_DOWN:
                    if ui_state.dialog_scroll_offset < len(ui_state.messages) - 6:
                        ui_state.dialog_scroll_offset += 1
                elif event.key == pygame.K_PAGEUP:
                    ui_state.dialog_scroll_offset = max(0, ui_state.dialog_scroll_offset - 3)
                elif event.key == pygame.K_PAGEDOWN:
                    ui_state.dialog_scroll_offset = min(len(ui_state.messages) - 6, ui_state.dialog_scroll_offset + 3)
                elif event.key == pygame.K_LEFT:
                    if ui_state.commands_scroll_offset > 0:
                        ui_state.commands_scroll_offset -= 1
                elif event.key == pygame.K_RIGHT:
                    if ui_state.commands_scroll_offset < len(all_commands) - 8:
                        ui_state.commands_scroll_offset += 1
        
        draw_interface()
        clock.tick(30)
    
    pygame.quit()

if __name__ == "__main__":
    main()