# main.py
import os
import sys

def main():
    """Основная функция запуска приложения"""
    print("Запуск голосового помощника Кеша...")
    
    # Добавляем текущую директорию в PATH для импорта модулей
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    try:
        # Запускаем основной файл
        from Kesha import main as kesha_main
        kesha_main()
    except ImportError as e:
        print(f"Ошибка импорта: {e}")
        input("Нажмите Enter для выхода...")
    except Exception as e:
        print(f"Ошибка: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()