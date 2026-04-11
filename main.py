import flet as ft
from storage import Storage
from file_handler import FileHandler
from ui import UI

def main(page: ft.Page):
    storage = Storage()
    file_handler = FileHandler(storage)
    ui = UI(page, storage, file_handler)
    ui.build()

if __name__ == "__main__":
    ft.app(target=main)