import gspread, sqlite3

gc = gspread.service_account(filename='my-plans-db-ab289859d1b5.json')

sh = gc.open("for_bot_testing")

print(ws.get_all_values())