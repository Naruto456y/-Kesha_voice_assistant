import time
import sys
import os 
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import tempfile
import speech_recognition as sr
import pygame

class manager():
    """Это класс помагатор для меня"""
    
    def open_file(name):
        """Открывает файл с помощью терминала"""
        os.system(f'start cmd /k python "{name}"')

    def search_file_path(file_path):
        """Помагает узнавать путь к файлу"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        absolute_path = os.path.join(current_dir, file_path)
        return absolute_path

    def play_music(file_path):
        """Воспроизводит mp3 файлы"""
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            # Ждем пока музыка играет
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Ошибка при воспроизведении: {e}")

    def listen_text(listen_seconds=5):
        """
        Слушает микрофон в течение указанного времени и возвращает распознанный текст.
        
        :param listen_seconds: количество секунд для прослушивания (по умолчанию 5)
        :return: распознанный текст или None в случае ошибки
        """
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        try:
                with microphone as source:
                    print("Слушаю... (говорите)")
                    recognizer.adjust_for_ambient_noise(source)  # Уменьшение шума
                    audio = recognizer.listen(source, timeout=listen_seconds, phrase_time_limit=listen_seconds)
                
                text = recognizer.recognize_google(audio, language="ru-RU")  # Для русского языка
                return text
        except AssertionError:
                print("Время ожидания истекло, речь не обнаружена.")
                return None            
        except sr.WaitTimeoutError:
                print("Время ожидания истекло, речь не обнаружена.")
                return None
        except sr.UnknownValueError:
                print("Речь не распознана.")
                return None
        except Exception as e:
                print(f"Произошла ошибка: {e}")
                return None

    def say(text, lang='ru'):
        """Озвучка текста с использованием gTTS и pydub"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as fp:
                temp_file = fp.name
            
            tts = gTTS(text=text, lang=lang)
            tts.save(temp_file)
            
            sound = AudioSegment.from_mp3(temp_file)
            play(sound)
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
                
def countdown(minutes):
    seconds = minutes * 60
    while seconds > 0:
        mins, secs = divmod(seconds, 60)
        print(f"\rОсталось: {mins:02d}:{secs:02d}", end="")
        time.sleep(1)
        seconds -= 1
    print("\n⏰ Время вышло!")
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(current_dir, 'basic-alarm-ringtone.mp3')
        manager.play_music(path)
    except:
        manager.say('Время вышло!')
    sys.exit(0)

if __name__ == "__main__":
    try:
        minutes_input = input('Введите количество минут для таймера: ')
        
        # Извлекаем только цифры из ввода
        digits = [d for d in minutes_input if d.isdigit()]
        
        if not digits:
            print("Ошибка: введите хотя бы одну цифру")
        else:
            minutes_num = int(''.join(digits))
            
            if minutes_num <= 0:
                print("Ошибка: число минут должно быть положительным")
            else:
                print(f"Таймер запущен на {minutes_num} минут(ы)")
                countdown(minutes_num)
                
    except ValueError:
        print("Ошибка: введите корректное число минут")
    except KeyboardInterrupt:
        print("\nТаймер отменён")
        sys.exit(0)