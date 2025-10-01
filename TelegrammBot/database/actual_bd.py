import asyncpg


async def create_pool():
    pool = await asyncpg.create_pool(
        #your database
    )
    return pool


async def add_user(pool, user_id, name, goal):
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO users (id, name, goal, xp, level, skill_points, gold)
            VALUES ($1, $2, $3, 0, 1, 0, 0)
            ON CONFLICT (id) DO NOTHING
        ''', user_id, name, goal)
        await conn.execute('''
            INSERT INTO stats (user_id, intelligence, strength)
            VALUES ($1, 1, 1)
            ON CONFLICT (user_id) DO NOTHING
        ''', user_id)


async def get_user(pool, user_id):
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT * FROM users WHERE id=$1', user_id)
        stats = await conn.fetchrow('SELECT * FROM stats WHERE user_id=$1', user_id)
    return user, stats


async def add_quest(pool, user_id, title, category, reward_xp):
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO quests (user_id, title, category, reward_xp, done)
            VALUES ($1, $2, $3, $4, FALSE)
        ''', user_id, title, category, reward_xp)


async def get_quests(pool, user_id):
    async with pool.acquire() as conn:
        return await conn.fetch('SELECT * FROM quests WHERE user_id=$1', user_id)


async def show_quests(pool, user_id: int):
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            'SELECT id, title, category, reward_xp, done FROM quests WHERE user_id=$1 ORDER BY id', user_id
        )
    if not rows:
        return "📜 - Нет активных квестов. \nДобавьте новый, чтобы начать!"
    text = "📜 <b>Ваши квесты:</b> \n\n"
    for i, quest in enumerate(rows, 1):
        if quest['done'] == True:
            done = '✅ Выполнен'
        else:
            done = '❌ Не выполнен'
        text += (f" {i}. {quest['title']}\n"
                 f"    📂 Категория: {quest['category']}\n"
                 f"    🏆 Награда: {quest['reward_xp']} XP\n"
                 f"    Статус: {done}\n\n"
                 )
    return text


async def show_profile(pool, user_id: int):
    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            'SELECT name, goal, xp, level, skill_points, gold FROM users WHERE id=$1',
            user_id
        )
        if not user:
            return "❌ Профиль не найден."
        stats = await conn.fetchrow(
            'SELECT intelligence, strength FROM stats WHERE user_id=$1',
            user_id
        )
        quests = await conn.fetch(
            'SELECT title, category, reward_xp, done FROM quests WHERE user_id=$1 ORDER BY id',
            user_id
        )
    completed = 0
    not_completed = 0
    text = ""
    text += f"👤 <b>Имя</b>: {user['name']}\n"
    text += f"🎯 <b>Цель</b>: {user['goal']}\n\n"
    text += f"⭐️ <b>Уровень</b>: {user['level']}\n"
    text += f"📈 <b>Опыт</b>: {user['xp']}/{user['level'] * 100}\n"
    text += f"💎 <b>Монеты</b>: {user['gold']}\n"
    text += f"🛠️ <b>Очки прокачки</b>: {user['skill_points']}\n\n"
    text += "📊 <b>Статы:</b>\n"
    stats_dict = dict(stats)
    for stat, points in stats_dict.items():
        if stat.lower() == 'strength':
            emoji = '💪'
        elif stat.lower() == 'intelligence':
            emoji = '🧠'
        else:
            emoji = '⚡️'
        text += f" {emoji} {stat.capitalize()}: {points}\n"

    for quest in quests:
        if quest['done']:
            completed += 1
        else:
            not_completed += 1

    text += "\n------------------------\n\n"
    text += "📜 <b>Квесты:</b>\n"
    if quests:
        text += f"Сводка квестов: \nВыполнено: {completed} ✅\nНе выполнено: {not_completed} ❌\n\n"
    else:
        text += " - Нет активных квестов\n"
    for i, quest in enumerate(quests, 1):
        if quest['done'] == True:
            done = '✅'
        else:
            done = '❌'
    return text
