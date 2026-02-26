import gspread, sqlite3, telebot, secret, re, time
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
search_row_ranges = [(2,2),(32,32),(62,62),(92,92),(122,122),(152,152)]  # list of (start_row, end_row) tuples or None = search whole sheet
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
        bot.send_chat_action(user, action='typing')
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        b1 = telebot.types.KeyboardButton(text="Расписание на весь день")
        b2 = telebot.types.KeyboardButton(text="Сдед. дела")
        b3 = telebot.types.KeyboardButton(text="Расписание на завтра")
        b4 = telebot.types.KeyboardButton(text="Прочее")
        keyboard.add(b1)
        keyboard.add(b2,b3,b4)
        time.sleep(10)
        bot.send_message(user, f"Привет , я твой личный помошник, ты сам как создатель знаешь что я могу, спасибо что меня создал", reply_markup=keyboard)
    else:
        bot.send_message(m.chat.id , "Вы не пользователь бота")
        if m.from_user.id not in blocked:
            blocked.append(m.from_user.id)
#Вывод дня
@bot.message_handler(func=lambda message: message.text == "Расписание на весь день")
def to_day(m):
    bot.send_chat_action(user, action='typing')
    today = check_date()  # Получаем число текущего дня (int)
    all_values = lst.get_all_values()  # Загружаем все значения листа в память
    print(all_values)

    # Найти ячейку с сегодняшним числом
    day_re = re.compile(r"\b(\d{1,2})\b")  # Регекс для поиска 1-2 цифр
    found = None  # Координаты найденной даты
    for r_idx, row_vals in enumerate(all_values, start=1):  # Перебираем строки (1-based)
        # Если заданы диапазоны строк — пропускаем строки вне диапазонов
        if search_row_ranges:
            in_any = False
            for a, b in search_row_ranges:
                if a <= r_idx <= b:
                    in_any = True
                    break
            if not in_any:
                continue
        for c_idx, cell_val in enumerate(row_vals, start=1):  # Перебираем ячейки в строке (1-based)
            if not cell_val:  # Пропускаем пустые ячейки
                continue
            s = cell_val.strip()  # Убираем пробелы по краям
            mnum = day_re.search(s)  # Ищем число в тексте ячейки
            num = None  # Временная переменная для найденного числа
            if mnum:
                try:
                    num = int(mnum.group(1))  # Преобразуем найденную подстроку в int
                    print(num)
                except Exception:
                    num = None  # Если не получилось — оставляем None
            if num == today or s == str(today):  # Совпадение по числу или по точной строке
                found = {'row': r_idx, 'col': c_idx}  # Запоминаем координаты
                break  # Выходим из цикла по столбцам
        if found:  # Если нашли — выходим из внешнего цикла
            break

    if not found:  # Если дата не найдена — сообщаем и выходим
        bot.send_message(m.chat.id, "Дата не найдена")
        return

    row = found['row']  # Номер строки с датой
    col = found['col']  # Номер столбца с датой

    sections = OrderedDict()  # Упорядоченный словарь для секций (метка -> список строк)
    last_label = None  # Последняя непустая метка (для наследования меток)

    # Проходим следующие 20 строк после строки с датой, пропуская каждую 7-ю
    for offset in range(1, 21):
        if offset % 7 == 0:  # Пропуск каждой 7-ой строки (как в оригинальной логике)
            continue
        rpos = row + offset  # Фактический индекс строки в таблице
        row_vals = all_values[rpos - 1] if 0 <= rpos - 1 < len(all_values) else []  # Берём строку или пустую
        label = (row_vals[0].strip() if len(row_vals) >= 1 and row_vals[0] else "")  # Метка из первой колонки
        v1 = (row_vals[col - 1].strip() if len(row_vals) >= col and row_vals[col - 1] else "")  # Значение в колонке даты
        v2 = (row_vals[col].strip() if len(row_vals) >= col + 1 and row_vals[col] else "")  # Доп. колонка рядом

        if label:  # Если в первой колонке есть метка
            lab = label  # Используем её
            last_label = lab  # Запоминаем как последнюю метку
            if lab not in sections:
                sections[lab] = []  # Создаём список для новой секции
        elif last_label:  # Если метки нет, но есть предыдущая — используем её
            lab = last_label
        else:  # Если ни метки, ни предыдущей — помещаем в 'Без секции'
            lab = 'Без секции'
            if lab not in sections:
                sections[lab] = []

        if lab not in sections:
            sections[lab] = []  # Гарантируем наличие ключа

        if v1 or v2:  # Если есть содержимое — добавляем строку в секцию
            sections[lab].append(f"{v1} -- {v2}")

    for lab, items in sections.items():  # Отправляем каждую секцию сообщением
        msg = lab + ("\n" + "\n".join(items) if items else "")  # Формируем текст: заголовок + строки
        try:
            bot.send_message(m.chat.id, msg)  # Отправка пользователю
        except Exception:
            pass  # Игнорируем ошибки отправки

        

@bot.message_handler(commands=['first'])
def first(m):
    if m.from_user.id not in blocked:
        bot.send_message(user, lst.cell(1,2).value)











































print('Успешно')
if __name__ == '__main__':
    bot.polling(non_stop=True)
    