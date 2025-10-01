parse_mode = 'HTML'

profile = {
    "Name": "",
    "Goal": "",
    "XP": 0,
    "Level": 1,
    "Skill Points": 0,
    "Quests": [

    ],
    "Stats": {
        "intelligence": 1,
        "strength": 1
    },
    "Gold": 0
}

base_xp = {
    "strength": 10,
    "intelligence": 10
}


#
# def ask_input(prompt, max_length=30):
#     while True:
#         user_input = input(prompt)
#
#         if len(user_input) == 0: #Check: Is string empty?
#             print('Sorry, string cannot be empty. Try it again')
#             continue
#
#         if len(user_input) > max_length: #Check: Is length more than 30 symbols?
#             print(f'String is too huge ({len(user_input)}) (maximum {max_length} symbols). Try it again')
#             continue
#
#         return user_input #If everything is okay


# def show_profile(profile):
#     text = ''
#     for key, value in profile.items():
#         if key == 'Stats':
#             text += f'{key}:\n'
#             for stat, points in value.items():
#                 text += f' - {stat}: {points}\n'
#         elif key == 'Quests':
#             text += f'{key}\n'
#             if not value:
#                 text += ' - Нет квестов\n'
#             else:
#                 for i, quest in enumerate(value, 1):
#                     text += (f' - {i}. {quest["Title"]}: '
#                              f'Категория: {quest["Category"]} - '
#                              f'Награда: {quest["Reward XP"]}'
#                              f' XP - Выполнено: {quest["Done"]}\n')
#         else:
#             text += f'{key}: {value}\n'
#     return text

def show_profile(profile):
    completed = 0
    not_completed = 0

    text = ""
    text += f"👤 <b>Имя</b>: {profile['Name']}\n"
    text += f"🎯 <b>Цель</b>: {profile['Goal']}\n\n"
    text += f"⭐️ <b>Уровень</b>: {profile['Level']}\n"
    text += f"📈 <b>Опыт</b>: {profile['XP']}/{profile['Level']*100}\n"
    text += f"💎 <b>Монеты</b>: {profile['Gold']}\n"
    text += f"🛠️ <b>Очки прокачки</b>: {profile.get('Skill Points', 0)}\n\n"
    text += "📊 <b>Статы:</b>\n"

    for stat, points in profile['Stats'].items():
        if stat.lower() == 'strength':
            emoji = '💪'
        elif stat.lower() == 'intelligence':
            emoji = '🧠'
        else:
            emoji = '⚡️'
        text += f" {emoji} {stat.capitalize()}: {points}\n"
    text += "\n"
    text += "------------------------"

    text += "\n\n📜 <b>Квесты:</b>\n"
    for quest in profile['Quests']:
        if quest['вone']:
            completed += 1
        else:
            not_completed += 1


    if profile['Quests']:
        text += f"Сводка квестов: \nВыполнено: {completed} ✅\nНе выполнено: {not_completed} ❌\n"
    else:
        text += ' - Нет активных квестов\n'

    for i, quest in enumerate(profile['Quests'], 1):
        if quest['Done'] == True:
            done = '✅'
        else:
            done = '❌'

    return text

def show_quests(profile):
    if not profile['Quests']:
        return "📜 - Нет активных квестов. \nДобавьте новый, чтобы начать!"

    text = "📜 <b>Ваши квесты:</b> \n\n"
    for i, quest in enumerate(profile['Quests'], 1):
        if quest['Done'] == True:
            done = '✅ Выполнен'
        else:
            done = '❌ Не выполнен'
        text += (f" {i}. {quest['Title']}\n"
                 f"    📂 Категория: {quest['Category']}\n"
                 f"    🏆 Награда: {quest['Reward XP']} XP\n"
                 f"    Статус: {done}\n\n"
                )
    return text

def add_xp(profile, amount):
    profile['XP'] += amount
    leveled_up = False
    earned_gold = 0
    earned_points = 0
    gold_reward = 0
    earned_gold_xp = 20

    needed_xp = profile['Level'] * 100
    if profile['XP'] >= needed_xp:
        while profile['XP'] >= needed_xp:
            profile['XP'] -= needed_xp
            profile['Level'] += 1
            gold_reward += 20 * profile['Level']
            profile['Gold'] += gold_reward
            profile['Skill Points'] += 2
            earned_gold += gold_reward
            earned_points += 2
            leveled_up = True
            needed_xp = profile['Level'] * 100

    remaining_xp = profile['XP']
    return leveled_up, earned_gold, earned_points, remaining_xp, needed_xp


def add_gold(profile, amount):
    bonus = profile['Level'] * 2
    profile['Gold'] += amount + bonus
    total_gold = profile['Gold']
    return amount, bonus, total_gold



def add_quest(profile):
    title = str(input('Введите название квеста: '))
    chosen_category = input('К какой категории относится ваш квест? - ').lower()
    if chosen_category not in base_xp:
        print('Такой категории нет. Попробуй снова')
        chosen_category = input('К какой категории относится ваш квест? - ').lower()
    xp = 10 + (0.5 * base_xp[chosen_category])
    xp = xp
    profile['Quests'].append({
        'Title': title,
        'Category': chosen_category,
        'Reward XP': xp,
        'Done': False
    })

def allocate_points(profile):
    chose = input('Какой стат вы хотите прокачать? - ').lower()
    if chose not in base_xp:
        print('Такой категории нет. Попробуй снова')
        chose = input('Какой стат вы хотите прокачать? - ').lower()
    profile['Stats'][chose] += 1
    base_xp[chose] += 5
    profile['Skill Points'] -= 1
    print(f'Вы успешно прокачали стат! {profile["Stats"][chose]}'
          f'\nОсталось очков для повышения: {profile["Skill Points"]}')


def complete_quest(profile):
    index = int(input('Какой квест выполнен? '))
    index -= 1
    while True:
        if not 0 <= index < len(profile['Quests']):
            print('Такого нет, повторите попытку')
            index = int(input('Какой квест выполнен? '))
            continue
        quest = profile['Quests'][index]
        quest['Done'] = True

        print(f'Квест "{quest["Title"]}" выполнен! Получено {quest["Reward XP"]} опыта')
        add_xp(profile, quest['Reward XP'])
        add_gold(profile, 5)
        break
#
#
#
#
