import time
import help_meneger as s
import sys
import os 

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
        s.manager.play_music(path)
    except:
        s.manager.say('Время вышло!')
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
