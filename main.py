import flet as ft
from storage import Storage
from file_handler import FileHandler
from ui import UI

def main(page: ft.Page):
    try:
        page.title = "File Transfer Assistant"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        page.bgcolor = ft.colors.GREY_50
        
        storage = Storage()
        file_handler = FileHandler(storage)
        
        app_ui = UI(page, storage, file_handler)
        app_ui.build()
        
    except Exception as e:
        error_container = ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.ERROR_OUTLINE, size=80, color=ft.colors.RED_400),
                ft.Text("App Error", size=28, weight=ft.FontWeight.BOLD, color=ft.colors.RED_700),
                ft.Container(height=20),
                ft.Text(f"Details: {str(e)}", size=14, color=ft.colors.GREY_600),
                ft.Container(height=10),
                ft.ElevatedButton("Retry", icon=ft.icons.REFRESH, on_click=lambda _: page.window.close())
            ], 
            alignment=ft.MainAxisAlignment.CENTER, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
            ),
            alignment=ft.alignment.center,
            bgcolor=ft.colors.WHITE,
            border_radius=15,
            padding=30,
            shadow=ft.BoxShadow(blur_radius=20, color=ft.colors.BLACK26)
        )
        page.add(error_container)

if __name__ == "__main__":
    ft.app(target=main)
