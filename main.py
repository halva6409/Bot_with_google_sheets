import gspread, sqlite3, telebot, secret, re
from collections import OrderedDict
from datetime import datetime
from secret import user, sh, filename_db, SPREADSHEET_ID

bot = telebot.TeleBot(secret.TOKEN)
gc = gspread.service_account(filename_db)
sheet = gc.open_by_key(SPREADSHEET_ID)
month = "Мар"
lst = sheet.worksheet(month)

m = 'message'
blocked = []
#Инициализация даты
def check_date():
    today = datetime.now().day
    return int(today)
#Получение месяца
@bot.message_handler(commands=['settings'])
def setting(m):
    parts = m.text.split()
    month = parts[1] 
    bot.reply_to(m, f"Принято, {month}")
#Приветствие, постоянные кнопки
@bot.message_handler(commands=['start'])
def start(m):
    if m.from_user.id == user:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        b1 = telebot.types.KeyboardButton(text="Расписание на весь день")
        b2 = telebot.types.KeyboardButton(text="Сдед. дела")
        b3 = telebot.types.KeyboardButton(text="Расписание на завтра")
        b4 = telebot.types.KeyboardButton(text="Прочее")
        keyboard.add(b1)
        keyboard.add(b2,b3,b4)
        bot.send_message(user, f"Привет , я твой личный помошник, ты сам как создатель знаешь что я могу, спасибо что меня создал", reply_markup=keyboard)
    else:
        bot.send_message(m.chat.id , "Вы не пользователь бота")
        if m.from_user.id not in blocked:
            blocked.append(m.from_user.id)
#Вывод дня
@bot.message_handler(func=lambda message: message.text == "Расписание на весь день")
def to_day(m):
    today = check_date()  # число дня, int
    found = None

    all_values = lst.get_all_values()  # все значения таблицы

    # Ищем ячейку, которая содержит номер дня (любой формат, содержащий число дня)
    day_re = re.compile(r"\b(\d{1,2})\b")
    for r_idx, row_values in enumerate(all_values, start=1):
        for c_idx, value in enumerate(row_values, start=1):
            if not value:
                continue
            sval = value.strip()
            mnum = day_re.search(sval)
            num = None
            if mnum:
                try:
                    num = int(mnum.group(1))
                except Exception:
                    num = None
            # Сравнение по извлечённому числу или по точной строке
            if num == today or sval == str(today):
                found = {'row': r_idx, 'col': c_idx}
                break
        if found:
            break

    if not found:
        return

    row = found['row']
    col = found['col']

    # Отправляем в телеграм и печатаем в терминал: сначала 6 строк после даты (исключая дату),
    # затем пропускаем одну строку (например, 'Обед'), затем снова 6 строк и т.д.
    groups = 3
    start_row = row + 1
    sections = OrderedDict()
    last_label = None
    # Собираем строки по меткам (колонка 1) в порядке появления
    for g in range(groups):
        for i in range(6):
            rpos = start_row + g * (6 + 1) + i
            try:
                label = lst.cell(rpos, 1).value
            except Exception:
                label = None
            try:
                v1 = lst.cell(rpos, col).value
                v2 = lst.cell(rpos, col + 1).value
            except Exception:
                v1 = None
                v2 = None
            lab = None
            if label and str(label).strip():
                lab = str(label).strip()
                if lab != last_label:
                    if lab not in sections:
                        sections[lab] = []
                    last_label = lab
            # Если метки ещё не было и есть предыдущая — используем предыдущую
            if lab is None and last_label is not None:
                lab = last_label
            # Если нет метки и нет last_label — используем 'Без секции'
            if lab is None:
                lab = 'Без секции'
                if lab not in sections:
                    sections[lab] = []
            # Проверяем содержимое строки
            has_content = False
            if v1 and str(v1).strip():
                has_content = True
            if v2 and str(v2).strip():
                has_content = True
            # Добавляем пустую секцию (если ещё не добавлена) — пользователь просил видеть 'Прочее' даже если пусто
            if lab not in sections:
                sections[lab] = []
            # Если есть содержимое — добавляем строку
            if has_content:
                line = f"{v1} -- {v2}"
                sections[lab].append(line)
    # Отправляем каждую секцию отдельным сообщением: сначала заголовок (метка), затем её строки (если есть)
    for lab, items in sections.items():
        if items:
            msg = lab + "\n" + "\n".join(items)
        else:
            msg = lab
        try:
            bot.send_message(m.chat.id, msg)
        except Exception:
            pass

        

@bot.message_handler(commands=['first'])
def first(m):
    if m.from_user.id not in blocked:
        bot.send_message(user, lst.cell(1,2).value)











































print('Успешно')
if __name__ == '__main__':
    bot.polling(non_stop=True)
    