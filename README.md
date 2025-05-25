# Telegram Бот для учёта продаж
## Инструкция по запуску

1. Перейти на Google Cloud Console
2. Создать проект
3. Включить Google Sheets API и Google Drive API
4. Создать сервисный аккаунт
5. Скачать .json-файл ключа, создать папку keys, положить в keys/service_account.json
6. В .env указать TELEGRAM_TOKEN от бота
7. В configs.py занести:
- spreadsheet_id(id таблицы)
- directors(telegram id директора магазина:id магазина)
- representatives(telegram id представителя)
8. Установить окружение, установить зависимости pip install -r requirements.txt
9. python bot.py
10. Функции: 
- /id - показать telegram id пользователя 
- /report <груши> <яблоки> <апельсины> <мандарины> <ананасы> (занести данные в таблицу, доступна только директору)
- /stats показать отчет о продажах в exel (доступно только представителю)
