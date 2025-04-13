from aiogram import Router, types
from aiogram.filters import Command #фильтр для команд 
from db import set_budget, log_transaction, get_summary, add_user, check_current_balance, change_current_balance

router = Router() #обьект который собирает и регистрирует все обработчики команд

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    add_user(message.from_user.id) #добавление юзера по его тг айди
    await message.answer("Hi! I'll help you keep track of your finances. Use /help for the list of commands.")

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("""
 Commands:
• /start — start
• /help — list of commands
• /config <category> <summ> — set a budget
• /log <+/-summ> <category> — record income/expense
• /summary — show balance by categories
""")

@router.message(Command("config"))
async def cmd_config(message: types.Message):
    args = message.text.strip().split() #разбиваем сообщения на слова 
    if len(args) != 3:
        return await message.answer(" Format: /config <category> <summ>") #проверка, введено ли 3 части

    _, category, amount = args #распаковка аргументов
    try:
        amount = int(amount) #преобразование суммы в число
    except ValueError:
        return await message.answer(" The sum must be a number ") #выводиться ошибка при неверном вводе

    set_budget(message.from_user.id, category, amount) # сохранение бюджета в базу данных
    await message.answer(f" Budget for the category '{category}' set: {amount}₸") #сообщение которое видит юзер, подтверждение установки бюджета

@router.message(Command("log"))
async def cmd_log(message: types.Message):
    args = message.text.strip().split()
    if len(args) != 3:
        return await message.answer(" Format: /log <+/-summ> <category>")

    _, amount_str, category = args
    try:
        amount = int(amount_str[1::]) #убираем знак и проебразуем сумму в число
        action = amount_str[0]
    except ValueError:
        return await message.answer(" The sum must be a signed number +/-")

    if action == '-': # - = расход 
        log_transaction(message.from_user.id, amount, category) #сохранение в историю транзакций
        change_current_balance(message.from_user.id, amount, category, action) #уменьшаем баланс
        await message.answer(f" Recorded: {amount}₸ in category '{category}'") #сообщение о успешном выполнении действия
    elif action == '+': # + = доход
        log_transaction(message.from_user.id, amount, category)
        change_current_balance(message.from_user.id, amount, category, action) # увеличиваем баланс
        await message.answer(f" Recorded: {amount}₸ in category '{category}'")

@router.message(Command("summary"))
async def cmd_summary(message: types.Message):
    user_id = message.from_user.id
    budgets = get_summary(user_id) # получем данные о юзере из базы данных

    if not budgets:
        return await message.answer(" No budgets were set yet.") #выводим это если нет устаровленных бюджетов

    lines = [" Current balance:\n"]
    for category, (current_balance, amount) in budgets.items(): #формируем список с данными по каждой категории
        line = f"• {category}: {current_balance}₸ / Budget: {amount}₸"
        if current_balance < 0:
            line += " ⚠️ Exceeds" #есои бюджет был превышен то выводи это
        lines.append(line)

    await message.answer("\n".join(lines))
