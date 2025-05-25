import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json


def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    keys = ServiceAccountCredentials.from_json_keyfile_name(
        "keys/service_account.json", scope
    )
    client = gspread.authorize(keys)

    with open("configs.json") as file:
        config = json.load(file)

    spreadsheet = client.open_by_key(config["spreadsheet_id"])
    return spreadsheet
