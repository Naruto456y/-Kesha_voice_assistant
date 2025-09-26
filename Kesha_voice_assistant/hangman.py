import random

def game():
        # Состаяние человечков:
        hangman_stages = [
        """
        +---+
        |   |
        |
        |
        |
        |
        ======
        """,
        """
        +---+
        |   |
        |   O
        |
        |
        |
        ======
        """,
        """
        +---+
        |   |
        |   O
        |   |
        |
        |
        ======
        """,
        """
        +---+
        |   |
        |   O
        |  /|
        |
        |
        ======
        """,
        """
        +---+
        |   |
        |   O
        |  /|\ 
        |
        |
        ======
        """,
        """
        +---+
        |   |
        |   O
        |  /|\ 
        |  / \ 
        |
        ======
        """
    ]

        # Список слов для угадывания
        words = (
            'солнце',
            'мармелад',
            'ледокол',
            'аттракцион',
            'дрессировка',
            'ошейник',
            'карамель',
            'водолаз',
            'защита',
            'батарея',
            'решётка',
            'квартира',
            'дельфин',
            'туча',
            'вход',
            'пешеход',
            'перекрёсток',
            'башня',
            'стрелка',
            'градусник'
        )
        
        lives = 6
        secret_word = random.choice(words)
        len_s = len(secret_word)
        s = '_' * len_s
        
        print('Здравствуйте! Это игра "Виселица", где вам нужно угадать слово, называя буквы.')
        print(f'Загаданное слово: {s}')
        print('У вас 6 попыток')
        
        while lives > 0:
            put = input('Напишите строчную букву: ').lower()
            
            if len(put) != 1 or not put.isalpha():
                print('Пожалуйста, введите одну строчную букву!')
                continue
                
            for i in range(len_s):
                if secret_word[i] == put:
                    s = s[:i] + put + s[i+1:]
            
            if put not in secret_word:
                lives -= 1
                print(f'Такой буквы нет в слове.')
            
            print(f'Текущее слово: {s}\n')
            
            if s == secret_word:
                print(f'Поздравляем! Вы угадали слово: {secret_word}!')
                print('Хотите сыграть ещё раз? (Да/Нет)')
                ans = input('Напишите Да или Нет: ')
                if ans.lower() == 'да':
                    game(True)
                else:
                    break
            else:
                if lives == 5:
                    print(hangman_stages[0])
                elif lives == 4:
                    print(hangman_stages[1])
                elif lives == 3:
                    print(hangman_stages[2])
                elif lives == 2:
                    print(hangman_stages[3])
                elif lives == 1:
                    print(hangman_stages[4])
                elif lives == 0:
                    print(hangman_stages[5])
                
                print(f'Осталось попыток: {lives}')
            if lives <= 0:
                print(f'Игра окончена! Загаданное слово было: {secret_word}')
                print('Хотите сыграть ещё раз? (Да/Нет)')
                ans = input('Напишите Да или Нет: ')
                if ans.lower() == 'да':
                    game()
                elif ans.lower() == 'нет':
                    break
                else:
                    print('Пожалуйста, введите "да" или "нет".')
if __name__ == '__main__':
    game()