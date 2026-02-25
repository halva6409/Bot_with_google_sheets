import types
import main

m = types.SimpleNamespace(text='Расписание на весь день', chat=types.SimpleNamespace(id=main.user), from_user=types.SimpleNamespace(id=main.user))
main.to_day(m)
print('test finished')
