import json
import os
import tempfile
import openpyxl
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from googlesheets_api import get_sheet
from datetime import datetime
from telegram import InputFile


load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")


with open("configs.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

SPREADSHEET_ID = CONFIG["spreadsheet_id"]
DIRECTORS = CONFIG["directors"]
REPRESENTATIVES = set(CONFIG["representatives"])

def is_director(user_id: int) -> bool:
    return str(user_id) in DIRECTORS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать в бот магазина")

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"Ваш ID: {user.id}")

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if not is_director(int(user_id)):
        await update.message.reply_text("У вас нет доступа к вводу данных.")
        return

    try:
        sales = list(map(int, context.args))
        if len(sales) != 5:
            raise ValueError

        store_number = DIRECTORS[user_id]
        spreadsheet = get_sheet()
        sheet = spreadsheet.worksheet("Продажи")

        row = [datetime.now().strftime("%Y-%m-%d"), store_number] + sales
        sheet.append_row(row)

        await update.message.reply_text("Отчет сохранен!")

    except ValueError:
        await update.message.reply_text(
            "Формат: /report <груши> <яблоки> <апельсины> <мандарины> <ананасы>"
        )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id not in REPRESENTATIVES:
        await update.message.reply_text("У вас нет доступа к этой команде.")
        return

    sheet = get_sheet()
    plans_sheet = sheet.worksheet("Планы")
    sales_sheet = sheet.worksheet("Продажи")

    plans_data = plans_sheet.get_all_values()[1:]
    sales_data = sales_sheet.get_all_values()[1:]

    plans = {row[0]: list(map(int, row[1:])) for row in plans_data}

    sales_summary = {store: [0]*5 for store in plans.keys()}

    for row in sales_data:
        store = row[1]
        fruits = list(map(int, row[2:]))
        if store in sales_summary:
            sales_summary[store] = [s + f for s, f in zip(sales_summary[store], fruits)]

    header = ["Магазин", "Груши", "Яблоки", "Апельсины", "Мандарины", "Ананасы", "Средний %"]

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Отчет по продажам"
    ws.append(header)

    for store in sorted(plans.keys(), key=int):
        store_plan = plans[store]
        store_sales = sales_summary[store]
        percents = [min(int(s / p * 100), 999) if p > 0 else 0 for s, p in zip(store_sales, store_plan)]
        avg = sum(percents) / len(percents)
        row = [int(store)] + [f"{p}%" for p in percents] + [f"{avg:.1f}%"]
        ws.append(row)

    for col in ws.columns:
        max_length = 0
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        adjusted_width = max_length + 2
        ws.column_dimensions[col_letter].width = adjusted_width

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmpfile:
        wb.save(tmpfile.name)
        tmpfile_path = tmpfile.name

    with open(tmpfile_path, "rb") as f:
        await update.message.reply_document(document=InputFile(f, filename="report.xlsx"))

    os.remove(tmpfile_path)


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("id", get_id))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("start", start))

    print("Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
