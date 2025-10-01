import asyncpg
import asyncio


async def create_pool():
    pool = await asyncpg.create_pool(
        #your database
    )
    return pool


async def main():
    pool = await create_pool()
    async with pool.acquire() as connection:
        await connection.execute('''
            CREATE TABLE IF NOT EXISTS users(
            id BIGINT PRIMARY KEY,
            name TEXT,
            goal TEXT,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            skill_points INTEGER DEFAULT 0,
            gold INTEGER DEFAULT 0
            )
        ''')
        await connection.execute('''
            CREATE TABLE IF NOT EXISTS quests(
            id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(id),
            title TEXT,
            category TEXT,
            reward_xp INTEGER,
            done BOOLEAN
            )            
        ''')
        await connection.execute('''
            CREATE TABLE IF NOT EXISTS stats(
            user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
            intelligence INTEGER DEFAULT 1,
            strength INTEGER DEFAULT 1,
            PRIMARY KEY(user_id)
            )            
        ''')

        await pool.close()
    print("Таблицы успешно созданы!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f'Ошибка: {e}')
    except KeyboardInterrupt:
        print('Операция прервана пользователем')
