import time
import sys
import json
import os
import random

SAVE_FILE = "game_save.json"

def type_text(text, delay=0.01):
    """Функция для печати текста с эффектом печатания"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def save_game(current_stage, choices_made):
    """Сохраняет прогресс игры"""
    save_data = {
        "current_stage": current_stage,
        "choices_made": choices_made,
        "timestamp": time.time()
    }
    
    try:
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        type_text("\n💾 Прогресс сохранён!")
    except Exception as e:
        type_text(f"\n❌ Ошибка сохранения: {e}")

def load_game():
    """Загружает сохранённую игру"""
    if not os.path.exists(SAVE_FILE):
        return None, []
    
    try:
        with open(SAVE_FILE, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
        
        type_text(f"\n📁 Найдено сохранение от {time.ctime(save_data['timestamp'])}")
        type_text(f"Прогресс: этап {save_data['current_stage']}")
        return save_data["current_stage"], save_data["choices_made"]
    except Exception as e:
        type_text(f"\n❌ Ошибка загрузки: {e}")
        return None, []

def delete_save():
    """Удаляет файл сохранения"""
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
        type_text("💾 Сохранение удалено.")

def game_over(reason):
    """Функция завершения игры при неудаче"""
    type_text(f"\n❌ {reason}")
    type_text("Игра окончена. Попробуйте снова!")
    
    while True:
        inp = input("\nХотите выйти? (1-да / 2-нет): ").lower()
        if inp == '1' or inp == 'да':
            sys.exit()
        elif inp == '2' or inp == 'нет':
            main()
            break

def victory(choices_made):
    """Функция победы"""
    type_text("\n🎉 ПОБЕДА!")
    type_text("Ты выполнил миссию! Данные 'Щита' обнародованы.")
    type_text("'Гидра' уничтожена. Ты начинаешь новую жизнь под другим именем.")
    type_text("Макс был бы горд. Миссия выполнена!")
    
    type_text(f"\n📊 Статистика игры:")
    type_text(f"Пройдено этапов: {len(choices_made)}")
    type_text(f"Ваши выборы: {', '.join(choices_made)}")

    delete_save()
    while True:
        inp = input("\nХотите выйти? (1-да / 2-нет): ").lower()
        if inp == '1' or inp == 'да':
            sys.exit()
        elif inp == '2' or inp == 'нет':
            main()
            break

def print_options(options, correct_option):
    """Печать вариантов ответов (случайный порядок) и возвращает правильный номер"""
    shuffled_options = options.copy()
    random.shuffle(shuffled_options)
    
    # Находим новый индекс правильного ответа после перемешивания
    correct_index = shuffled_options.index(correct_option) + 1
    
    for i, option in enumerate(shuffled_options, 1):
        type_text(f"{i}. {option}")
    
    return correct_index, shuffled_options

def show_menu():
    """Показывает главное меню"""
    type_text("\n=== ОПЕРАЦИЯ 'ТИХИЙ ЩИТ' ===")
    type_text("1. Начать новую игру")
    type_text("2. Загрузить игру")
    type_text("3. Выйти")
    
    choice = input("\nВыберите действие (1-3): ")
    return choice

def execute_stage(stage_num, choices_made):
    """Выполняет определённый этап игры"""
    
    if stage_num == 1:
        type_text("\n--- ЭТАП 1: Проникновение ---")
        type_text("Ты подъезжаешь к заброшенному заводу-прикрытию.")
        type_text("Куда направишься?")
        
        correct_option = "К чёрному ходу у погрузочной платформы"
        options = [
            "К главному входу",
            "К вентиляционной шахте", 
            correct_option
        ]
        
        correct_index, displayed_options = print_options(options, correct_option)
        
        choice = input("\nТвой выбор (1-3) или 'save' для сохранения: ")
        
        if choice.lower() == 'save':
            save_game(stage_num, choices_made)
            return stage_num, choices_made
        
        if choice == str(correct_index):
            type_text("\n✅ Ты незаметно проникаешь внутрь. Путь свободен.")
            choices_made.append("Чёрный ход")
            return stage_num + 1, choices_made
        else:
            wrong_choice = displayed_options[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= 3 else "неизвестный путь"
            if wrong_choice == "К главному входу":
                game_over("Ты напоролся на вооружённую охрану 'Гидры'. Пришлось отступать под огнём.")
            else:
                game_over("Шахта вела в тупик. Сработала сигнализация.")

    elif stage_num == 2:
        type_text("\n--- ЭТАП 2: Навигация ---")
        type_text("Внутри темно и запутанно. Перед тобой три коридора.")
        
        correct_option = "Коридор с синим светом и проводкой на стенах"
        options = [
            "Коридор с зелёной аварийной подсветкой",
            "Коридор с мигающей красной лампой",
            correct_option
        ]
        
        correct_index, displayed_options = print_options(options, correct_option)
        
        choice = input("\nТвой выбор (1-3) или 'save' для сохранения: ")
        
        if choice.lower() == 'save':
            save_game(stage_num, choices_made)
            return stage_num, choices_made
        
        if choice == str(correct_index):
            type_text("\n✅ Это серверная ветка. Ты на верном пути.")
            choices_made.append("Синий коридор")
            return stage_num + 1, choices_made
        else:
            wrong_choice = displayed_options[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= 3 else "неизвестный путь"
            if wrong_choice == "Коридор с зелёной аварийной подсветкой":
                game_over("Это оказался путь в столовую. Ты столкнулся с двумя техниками.")
            else:
                game_over("Ты вышел к генераторам. Чуть не наткнулся на патруль.")

    elif stage_num == 3:
        type_text("\n--- ЭТАП 3: Взлом ---")
        type_text("Ты нашёл серверную. Дверь защищена электронным замком.")
        
        correct_option = "Подключить портативный декодер к шлейфу данных"
        options = [
            "Попытаться подобрать код вручную",
            "Выстрелить в панель замка из электрошокера",
            correct_option
        ]
        
        correct_index, displayed_options = print_options(options, correct_option)
        
        choice = input("\nТвой выбор (1-3) или 'save' для сохранения: ")
        
        if choice.lower() == 'save':
            save_game(stage_num, choices_made)
            return stage_num, choices_made
        
        if choice == str(correct_index):
            type_text("\n✅ Замок тихо щёлкнул. Дверь открыта.")
            choices_made.append("Декодер")
            return stage_num + 1, choices_made
        else:
            wrong_choice = displayed_options[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= 3 else "неизвестный метод"
            if wrong_choice == "Попытаться подобрать код вручную":
                game_over("После третьей ошибки замок заблокировался на 5 минут.")
            else:
                game_over("Короткое замыкание спалило твой ноутбук.")

    elif stage_num == 4:
        type_text("\n--- ЭТАП 4: Поиск данных ---")
        type_text("В серверной три стойки. Где искать данные?")
        
        correct_option = "Стойка без маркировки, но с активным охлаждением"
        options = [
            "Стойка с маркировкой 'Архив'",
            "Стойка с маркировкой 'Основные базы'",
            correct_option
        ]
        
        correct_index, displayed_options = print_options(options, correct_option)
        
        choice = input("\nТвой выбор (1-3) или 'save' для сохранения: ")
        
        if choice.lower() == 'save':
            save_game(stage_num, choices_made)
            return stage_num, choices_made
        
        if choice == str(correct_index):
            type_text("\n✅ Именно здесь хранится проект 'Щит'. Загрузка пошла...")
            choices_made.append("Стойка с охлаждением")
            return stage_num + 1, choices_made
        else:
            wrong_choice = displayed_options[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= 3 else "неизвестная стойка"
            if wrong_choice == "Стойка с маркировкой 'Архив'":
                game_over("Здесь только старые логи. Ты потратил 10 минут впустую.")
            else:
                game_over("Данные сильно зашифрованы. На взлом уйдёт больше часа.")

    elif stage_num == 5:
        type_text("\n--- ЭТАП 5: Скрытность ---")
        type_text("Данные загружаются. Внезапно слышишь шаги. Кто-то идёт.")
        
        correct_option = "Остаться на месте и замереть, приглушив свет экрана"
        options = [
            "Спрятаться за серверными стойками",
            "Притвориться техником и пойти навстречу", 
            correct_option
        ]
        
        correct_index, displayed_options = print_options(options, correct_option)
        
        choice = input("\nТвой выбор (1-3) или 'save' для сохранения: ")
        
        if choice.lower() == 'save':
            save_game(stage_num, choices_made)
            return stage_num, choices_made
        
        if choice == str(correct_index):
            type_text("\n✅ Охранник мельком заглянул и ушёл, ничего не заметив.")
            choices_made.append("Маскировка")
            return stage_num + 1, choices_made
        else:
            wrong_choice = displayed_options[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= 3 else "неизвестное действие"
            if wrong_choice == "Спрятаться за серверными стойками":
                game_over("Охранник заметил торчащий кабель и поднял тревогу.")
            else:
                game_over("Твой внешний вид и отсутствие пропуска вызвали подозрения.")

    elif stage_num == 6:
        type_text("\n--- ЭТАП 6: Загрузка ---")
        type_text("Загрузка на 80%. По рации охраны объявляют тревогу. Тебя ищут.")
        
        correct_option = "Дождаться полной загрузки, оставаясь на месте"
        options = [
            "Немедленно прервать загрузку и бежать",
            "Ускорить загрузку, послав серверам команду на приоритет",
            correct_option
        ]
        
        correct_index, displayed_options = print_options(options, correct_option)
        
        choice = input("\nТвой выбор (1-3) или 'save' для сохранения: ")
        
        if choice.lower() == 'save':
            save_game(stage_num, choices_made)
            return stage_num, choices_made
        
        if choice == str(correct_index):
            type_text("\n✅ Загрузка завершена! Данные твои!")
            choices_made.append("Ожидание загрузки")
            return stage_num + 1, choices_made
        else:
            wrong_choice = displayed_options[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= 3 else "неизвестное решение"
            if wrong_choice == "Немедленно прервать загрузку и бежать":
                game_over("Данные повреждены. Миссия провалена.")
            else:
                game_over("Система защиты зафиксировала аномалию и заблокировала доступ.")

    elif stage_num == 7:
        type_text("\n--- ЭТАП 7: Побег ---")
        type_text("Данные у тебя. Но все выходы блокированы.")
        
        correct_option = "Взломать систему управления зданием и отключить свет"
        options = [
            "Попытаться прорваться с боем",
            "Спрятаться в вентиляции и ждать",
            correct_option
        ]
        
        correct_index, displayed_options = print_options(options, correct_option)
        
        choice = input("\nТвой выбор (1-3) или 'save' для сохранения: ")
        
        if choice.lower() == 'save':
            save_game(stage_num, choices_made)
            return stage_num, choices_made
        
        if choice == str(correct_index):
            type_text("\n✅ В темноте и суматохе ты смог проскользнуть к запасному выходу.")
            choices_made.append("Отключение света")
            return stage_num + 1, choices_made
        else:
            wrong_choice = displayed_options[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= 3 else "неизвестный план"
            if wrong_choice == "Попытаться прорваться с боем":
                game_over("Тебя окружили в первом же коридоре. Сопротивление бесполезно.")
            else:
                game_over("Охрана пустила служебных собак. Тебя нашли по запаху.")

    elif stage_num == 8:
        type_text("\n--- ЭТАП 8: Уход ---")
        type_text("Ты на улице. За тобой погоня на машинах.")
        
        correct_option = "Добраться до заранее приготовленного убежища в городе"
        options = [
            "Уходить через густой лес",
            "Угнать первую попавшуюся машину",
            correct_option
        ]
        
        correct_index, displayed_options = print_options(options, correct_option)
        
        choice = input("\nТвой выбор (1-3) или 'save' для сохранения: ")
        
        if choice.lower() == 'save':
            save_game(stage_num, choices_made)
            return stage_num, choices_made
        
        if choice == str(correct_index):
            type_text("\n✅ Ты растворился в городских улицах.")
            choices_made.append("Городское убежище")
            return stage_num + 1, choices_made
        else:
            wrong_choice = displayed_options[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= 3 else "неизвестный маршрут"
            if wrong_choice == "Уходить через густой лес":
                game_over("В лесу тебя быстро нашли с дронов с тепловизорами.")
            else:
                game_over("Машина оказалась с GPS-маяком. Тебя выследили за 10 минут.")

    elif stage_num == 9:
        type_text("\n--- ЭТАП 9: Распространение ---")
        type_text("Ты в убежище. Что делать с данными?")
        
        correct_option = "Расшифровать и сделать копии для СМИ и спецслужб"
        options = [
            "Немедленно выложить в сеть",
            "Передать заказчику и забыть",
            correct_option
        ]
        
        correct_index, displayed_options = print_options(options, correct_option)
        
        choice = input("\nТвой выбор (1-3) или 'save' для сохранения: ")
        
        if choice.lower() == 'save':
            save_game(stage_num, choices_made)
            return stage_num, choices_made
        
        if choice == str(correct_index):
            type_text("\n✅ Правда всплыла. 'Гидра' обезглавлена.")
            choices_made.append("Распространение данных")
            return stage_num + 1, choices_made
        else:
            wrong_choice = displayed_options[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= 3 else "неизвестная стратегия"
            if wrong_choice == "Немедленно выложить в сеть":
                game_over("Данные попали к конкурентам раньше, чем к правоохранителям.")
            else:
                game_over("Заказчик оказался связан с 'Гидрой'. Теперь ты и сам в опасности.")

    elif stage_num == 10:
        type_text("\n--- ЭТАП 10: Финал ---")
        type_text("Всё кончено. Твои дальнейшие действия?")
        
        correct_option = "Исчезнуть и начать новую жизнь под другим именем"
        options = [
            "Вернуться к обычной жизни",
            "Начать работать на правительство", 
            correct_option
        ]
        
        correct_index, displayed_options = print_options(options, correct_option)
        
        choice = input("\nТвой выбор (1-3) или 'save' для сохранения: ")
        
        if choice.lower() == 'save':
            save_game(stage_num, choices_made)
            return stage_num, choices_made
        
        if choice == str(correct_index):
            victory(choices_made)
        else:
            wrong_choice = displayed_options[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= 3 else "неизвестный выбор"
            if wrong_choice == "Вернуться к обычной жизни":
                game_over("Тебя нашли сообщники 'Гидры'. Отомстили.")
            else:
                game_over("Ты стал винтиком в системе. Свободы больше нет.")

def main():
    current_stage = 1
    choices_made = []
    
    # Главное меню
    while True:
        menu_choice = show_menu()
        
        if menu_choice == "1":
            # Новая игра
            delete_save()
            
            break
        elif menu_choice == "2":
            # Загрузка игры
            loaded_stage, loaded_choices = load_game()
            if loaded_stage:
                current_stage = loaded_stage
                choices_made = loaded_choices
                type_text("\nИгра загружена! Продолжаем...")
                break
            else:
                type_text("\nСохранение не найдено или повреждено. Начинаем новую игру.")
                break
        elif menu_choice == "3":
            type_text("Выход из игры. До свидания!")
            time.sleep(1)
            sys.exit()
        else:
            type_text("Неверный выбор. Попробуйте снова.")
    
    # Основной игровой цикл
    type_text("\n" + "="*50)
    type_text("=== ОПЕРАЦИЯ 'ТИХИЙ ЩИТ' ===")
    type_text("\nТы - Алекс, хакер. Твой напарник Макс в беде.")
    type_text("Его последнее сообщение: 'Алекс, они меня вычислили! Данные о проекте Щит не должны уйти к Гидре...'") 
    type_text("Связи прервалась. У тебя есть 1 час...")
    
    # Выполнение этапов игры
    while current_stage <= 10:
        current_stage, choices_made = execute_stage(current_stage, choices_made)

if __name__ == "__main__":
    main()