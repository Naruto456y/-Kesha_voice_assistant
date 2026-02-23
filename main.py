# main.py
import os
import sys
import traceback

def resource_path(relative_path):
    """Получить абсолютный путь к ресурсу для PyInstaller"""
    try:
        # PyInstaller создает временную папку, путь в _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def main():
    """Основная функция запуска приложения"""
    print("Запуск голосового помощника Кеша...")
    
    # Для PyInstaller: добавляем правильные пути
    if getattr(sys, 'frozen', False):
        # Если приложение собрано в exe
        application_path = sys._MEIPASS
    else:
        # Если запуск из исходного кода
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    sys.path.insert(0, application_path)
    
    try:
        # Пытаемся импортировать и запустить основной модуль
        from Kesha import main as kesha_main
        kesha_main()
    except ImportError as e:
        print(f"Ошибка импорта: {e}")
        print("Убедитесь, что все файлы находятся в одной папке:")
        print("- Kesha.py")
        print("- Все игровые файлы (*.py)")
        print("- Иконка Kesha_icoc.ico")
        input("Нажмите Enter для выхода...")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        print("Детали ошибки:")
        traceback.print_exc()
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()