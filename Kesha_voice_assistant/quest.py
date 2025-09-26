import os
# Файл для сохранения прогресса
SAVE_FILE = 'game_save.txt'

# Функция для сохранения прогресса
def save_progress(progress):
    with open(SAVE_FILE, 'w') as file:
        file.write(progress)

# Функция для загрузки прогресса
def load_progress():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as file:
            return file.read()
    return None

# Основная логика игры
def game():
    progress = load_progress()
    if progress:
        print(f"Мы нашли сохранение: {progress}")
        continue_game = input("Хотите продолжить? (да/нет): ").lower()
        if continue_game != 'да':
            progress = None
    else:
        print("Новая игра!")

    if not progress:
        progress = 'начало'

    while True:
        if progress == 'начало':
            print("Вы стоите у входа в лес. Что делаете?")
            print("1. Идти в лес")
            print("2. Вернуться домой")
            choice = input("Ваш выбор: ")
            if choice == '1':
                progress = 'в лесу'
            elif choice == '2':
                print("Вы решили не идти в лес. Игра окончена.")
                break
            save_progress(progress)

        elif progress == 'в лесу':
            print("Вы в лесу. Впереди два пути.")
            print("1. Пойти по тропинке")
            print("2. Заблудиться и вернуться назад")
            choice = input("Ваш выбор: ")
            if choice == '1':
                progress = 'на поляне'
            elif choice == '2':
                print("Вы заблудились и вышли из игры.")
                break
            save_progress(progress)

        elif progress == 'на поляне':
            print("Вы на поляне. Тут спрятан сундук.")
            print("1. Открыть сундук")
            print("2. Уйти с поляны")
            choice = input("Ваш выбор: ")
            if choice == '1':
                print("Вы нашли сокровище! Игра завершена.")
                os.remove(SAVE_FILE)  # Удаляем сохранение
                break
            elif choice == '2':
                print("Вы уходите с поляны. Игра окончена.")
                break
if __name__ == "__main__":
    game()