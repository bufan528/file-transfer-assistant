import flet as ft

def main(page: ft.Page):
    page.title = "File Transfer v1.2"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    def add_text(e):
        if text_field.value and text_field.value.strip():
            items.controls.append(build_item("text", text_field.value.strip()))
            text_field.value = ""
            page.update()
    
    def build_item(item_type, content):
        colors = {"text": ft.colors.BLUE, "link": ft.colors.GREEN}
        icons = {"text": ft.icons.NOTES, "link": ft.icons.LINK}
        c = colors.get(item_type, ft.colors.GREY)
        ic = icons.get(item_type, ft.icons.DOCUMENT)
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(ic, size=20, color=c),
                ft.Column([
                    ft.Text(content[:60] + ("..." if len(content) > 60 else ""), size=14),
                ], expand=True),
                ft.IconButton(ft.icons.DELETE, icon_color=ft.colors.RED_400,
                    on_click=lambda _, item=items.controls[-1]: delete_item(item))
            ], spacing=10),
            padding=12,
            bgcolor=ft.colors.WHITE,
            border=ft.border.all(1, ft.colors.GREY_200),
            border_radius=8,
        )
    
    def delete_item(item):
        items.controls.remove(item)
        page.update()
    
    items = ft.Column(spacing=8, expand=True)
    text_field = ft.TextField(hint_text="Enter text here...", expand=True,
        on_submit=add_text, border_radius=20)
    
    page.add(
        ft.Column([
            ft.Container(
                content=ft.Text("File Transfer", size=20, weight=ft.FontWeight.BOLD,
                    color=ft.colors.BLUE_600),
                padding=15, bgcolor=ft.colors.BLUE_50
            ),
            ft.Divider(),
            ft.Row([text_field, ft.ElevatedButton("Add",
                icon=ft.icons.ADD, on_click=add_text, style=ft.ButtonStyle(
                    bgcolor=ft.colors.BLUE_600, color=ft.colors.WHITE))],
                spacing=10, padding=10),
            ft.Divider(height=1),
            ft.Container(content=items, expand=True),
        ], expand=True, spacing=0)
    )

if __name__ == "__main__":
    ft.app(target=main)
