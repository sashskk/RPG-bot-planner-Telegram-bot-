from aiogram import types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from script import base_xp
from database.actual_bd import create_pool, add_user, get_user, add_quest, get_quests, show_quests, show_profile
import app.keyboards as kb

pool = None
router = Router()


class Register(StatesGroup):
    name = State()
    goal = State()


class Addquest(StatesGroup):
    add_quest = State()
    complete_quest1 = State()


class Allocatepoints(StatesGroup):
    allocate_points = State()


@router.message(CommandStart())
async def handle_start(message: types.Message):
    await message.answer(text=f'Приветствую тебя в моем боте'
                              f'\nЧтобы начать пользоваться ботом, нужно создать профиль!',
                         reply_markup=kb.register)


@router.message(Command('help'))
async def handle_help(message: types.Message):
    await message.answer(text='🆘 <b>Помощь</b>\n\n'
                              '📋 Профиль — посмотреть свой уровень, опыт, золото и стату.\n'
                              '📜 Мои квесты — список заданий, которые ты выполняешь.\n'
                              '➕ Добавить квест — создать новое задание и получить за него награды.\n'
                              '🏅 Выполнить квест — отметить задание как выполненное и забрать XP и монеты.\n\n'
                              '💡 Совет: начинай с простых квестов, постепенно прокачивая уровень и получая награды!')


@router.message(lambda m: m.text == 'Создать профиль!')
async def process_create_profile(message: Message, state: FSMContext):
    await state.set_state(Register.name)
    await message.answer('Введите ваше имя')


@router.message(Register.name)
async def register_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Register.goal)
    await message.answer('Введите вашу цель')


@router.message(Register.goal)
async def register_goal(message: Message, state: FSMContext):
    global pool
    if not pool:
        pool = await create_pool()
    await state.update_data(goal=message.text)
    user_data = await state.get_data()
    name = user_data['name']
    goal = user_data['goal']
    await add_user(pool, message.from_user.id, name, goal)
    await message.answer(f'✅ Профиль создан! \nИмя: {name} \nЦель: {goal}', reply_markup=kb.main)
    await state.clear()


@router.message(lambda m: m.text == '📋 Посмотреть профиль')
async def show_user_profile(message: Message):
    global pool
    if not pool:
        pool = await create_pool()
    text = await show_profile(pool, message.from_user.id)
    await message.answer(text, reply_markup=kb.main)
    user, stats = await get_user(pool, message.from_user.id)
    if not user:
        await message.answer("❌ Профиль не найден. \nСначала создайте профиль", reply_markup=kb.register)
        return


@router.message(lambda m: m.text == '📜 Мои квесты')
async def show_user_quests(message: Message):
    global pool
    if not pool:
        pool = await create_pool()
    text = await show_quests(pool, message.from_user.id)
    await message.answer(text, reply_markup=kb.complete_main)
    user = await get_user(pool, message.from_user.id)
    if not user:
        await message.answer("❌ Профиль не найден. \nСначала создайте профиль", reply_markup=kb.register)
        return


@router.message(lambda m: m.text == '➕ Добавить квест')
async def adding_quest(message: Message, state: FSMContext):
    await state.set_state(Addquest.add_quest)
    await message.answer('Введите ваш квест')


@router.message(Addquest.add_quest)
async def adding_quest1(message: Message, state: FSMContext):
    await state.update_data(add_quest=message.text)
    await message.answer('Выберите категорию квеста', reply_markup=kb.categories)
    user, stats = await get_user(pool, message.from_user.id)
    if not user:
        await message.answer("❌ Профиль не найден. \nСначала создайте профиль", reply_markup=kb.register)
        await state.clear()
        return


@router.callback_query(F.data.in_(['intelligence', 'strength']))
async def process_category(callback: CallbackQuery, state: FSMContext):
    global pool
    if not pool:
        pool = await create_pool()

    user_data = await state.get_data()
    quest_title = user_data.get('add_quest')
    category = callback.data
    user, stats = await get_user(pool, callback.from_user.id)
    if not user:
        await callback.message.answer("❌ Профиль не найден. \nСначала создайте профиль", reply_markup=kb.register)
        return
    stat_level = stats[category]
    base = base_xp.get(category, 10)
    reward_xp = int(base * (1 + (stat_level - 1) * 0.5))
    await add_quest(pool, callback.from_user.id, quest_title, category, reward_xp)
    await callback.answer('Вы выбрали категорию')
    await callback.message.answer(
        f'✅ Квест "{quest_title}" добавлен!\n📂Категория: {category}\n🏆Награда: {reward_xp} XP',
        reply_markup=kb.main
    )
    await state.clear()


@router.message(lambda m: m.text == '🛠️ Распределить очки')
async def allocating(message: Message, state: FSMContext):
    await state.set_state(Allocatepoints.allocate_points)
    user, stats = await get_user(pool, message.from_user.id)
    if not user:
        await message.answer("❌ Профиль не найден. \nСначала создайте профиль", reply_markup=kb.register)
        await state.clear()
        return
    if user['skill_points'] <= 0:
        await message.answer('❌ Нет доступных очков')
        await state.clear()
        return
    await state.set_state(Allocatepoints.allocate_points)
    await message.answer(
        f'У вас {user["skill_points"]} свободных очков. \nВыберите стат для прокачки:',
        reply_markup=kb.stats
    )


@router.callback_query(F.data.startswith('stat_'))
async def process_stats(callback: CallbackQuery, state: FSMContext):
    global pool
    if not pool:
        pool = await create_pool()

    stat = callback.data.split('_', 1)[1]
    user, stats = await get_user(pool, callback.from_user.id)

    if not user:
        await callback.message.answer("❌ Профиль не найден. \nСначала создайте профиль", reply_markup=kb.register)
        await state.clear()
        return

    if user['skill_points'] <= 0:
        await callback.message.answer('❌ У вас больше нет очков для распределения.')
        await state.clear()

        return

    async with pool.acquire() as conn:
        await conn.execute(
            f'UPDATE stats SET {stat} = {stat} + 1 WHERE user_id=$1',
            callback.from_user.id
        )
        await conn.execute(
            f'UPDATE users SET skill_points = skill_points - 1 WHERE id=$1',
            callback.from_user.id
        )

    await callback.answer('Вы выбрали стат')
    await callback.message.answer(
        f'✅ {stat.capitalize()} увеличен на 1!\n'
        f'Осталось очков: {user["skill_points"] - 1}',
        reply_markup=kb.main
    )
    await state.clear()


@router.message(lambda m: m.text == '✅ Выполнить квест')
async def adding_quest(message: Message, state: FSMContext):
    user, stats = await get_user(pool, message.from_user.id)
    if not user:
        await message.answer("❌ Профиль не найден. \nСначала создайте профиль", reply_markup=kb.register)
        await state.clear()
        return

    await state.set_state(Addquest.complete_quest1)
    await message.answer('Введите номер квеста, который хотите выполнить')


@router.message(Addquest.complete_quest1)
async def adding_quest1(message: Message, state: FSMContext):
    global pool
    if not pool:
        pool = await create_pool()

    user_id = message.from_user.id
    quests = await get_quests(pool, user_id)
    user, stats = await get_user(pool, message.from_user.id)

    if not user:
        await message.answer("❌ Профиль не найден. \nСначала создайте профиль", reply_markup=kb.register)
        await state.clear()
        return

    if not message.text.isdigit():
        await message.answer('❌ Введите корректный номер квеста')
        return
    quest_number = int(message.text)

    if quest_number < 1 or quest_number > len(quests):
        await message.answer('❌ Такого квеста нет, попробуйте еще раз')
        return
    quest = quests[quest_number - 1]

    if quest['done']:
        await message.answer('❌ Этот квест уже выполнен. \nВыберите другой')
        return

    stat_key = quest['category']
    stat_level = stats[stat_key]
    base = quest['reward_xp']
    final_xp = int(base * (1 + (stat_level - 1) * 0.5))

    async with pool.acquire() as conn:
        await conn.execute(
            'UPDATE quests SET done=TRUE WHERE id=$1',
            quest['id'],)

        new_xp= user['xp'] + final_xp
        new_gold = user['gold'] + 5
        new_level = user['level']
        new_points = user['skill_points']
        bonus_gold = 10 * user['level']

        needed_xp = new_level * 100
        if new_xp >= needed_xp:
            new_level += 1
            new_points += 2
            new_gold += bonus_gold
            new_xp = new_xp - needed_xp

        await conn.execute(
            'UPDATE users SET xp=$1, gold=$2, level=$3, skill_points=$4 WHERE id=$5',
            new_xp, new_gold, new_level, new_points, user_id
        )

    await message.answer(f'✅ Квест "{quest["title"]}" выполнен!\n'
                         f'Вы получили {final_xp} XP\n'
                         f'Вы заработали 5 монет \n')

    if new_level > user['level']:
        await message.answer(f'🎉 Поздравляем! Вы повысили уровень до {new_level}!\n'
                             f'Вы получили 2 очков прокачки и {bonus_gold} монет!')
