import random
import sys

def knb():
        sp = ['камень','ножницы','бумага']
        ai = random.choice(sp)
        print('\033[1m'+'Здраствуйте! Это игра камень,ножницы,бумага. ')
        print('Как играть: к = камень, н = ножницы, б = бумага')
        try:
            while True:
                i = str(input('Введите к/н/б:')).lower().strip()
                if i not in 'кнб':
                    print('Пожалуйста введите к, н или б')
                    continue
                elif len(i) != 1:
                    print('Пожалуйста введите к, н или б')
                    continue
                elif i == '':
                    print('Пожалуйста введите к, н или б')
                    continue
                else:
                    break
        except ValueError:
            print('Пожалуйста введите к, н или б')

        print(f"Компьютер выбрал: {ai}")
        if ai == 'камень':
            ai = 'к'
        elif ai == 'ножницы':
            ai = 'н'
        elif ai == 'бумага':
            ai = 'б'
        if i == ai :
            print('Ничья!')
        elif i == 'к' and ai == 'н':
            print('Вы выиграли!')
        elif i == 'н' and ai == 'б':
            print('Вы выиграли!')
        elif i == 'б' and ai == 'к':
            print('Вы выиграли!')
        else:
            print('Вы проиграли!')
        print('Хотите сыграть ещё раз? (да/нет)')
        while True:
            ans = input('Напишите Да или Нет: ')
            if ans.lower() == 'да':
                print('\n'+'НОВАЯ ИГРА'+'\n')
                knb()
            elif ans.lower() == 'нет':
                break
            else:
                print('Пожалуйста, введите "да" или "нет".')
if __name__ == '__main__':
    knb()