import flet as ft
import os
from datetime import datetime

class UI:
    def __init__(self, page: ft.Page, storage, file_handler):
        self.page = page
        self.storage = storage
        self.file_handler = file_handler
        self.current_tab = "all"
        self.items = []
        self.search_query = ""

    def build(self):
        self.page.title = "文件传输助手"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0

        self._build_app_bar()
        self._build_content()
        self._build_bottom_nav()
        self._build_add_dialog()
        self._build_detail_dialog()
        self._build_delete_dialog()

        self.page.update()
        self.load_items()

    def _build_app_bar(self):
        self.search_field = ft.TextField(
            hint_text="搜索...",
            prefix_icon=ft.icons.SEARCH,
            on_submit=self._on_search,
            expand=True
        )
        self.page.appbar = ft.AppBar(
            title=ft.Text("文件传输助手", weight=ft.FontWeight.W_500),
            actions=[
                self.search_field,
                ft.IconButton(icon=ft.icons.SEARCH, on_click=self._on_search)
            ],
            bgcolor=ft.colors.BLUE
        )

    def _build_content(self):
        self.content_list = ft.ListView(
            expand=True,
            spacing=5,
            padding=10
        )

        self.empty_view = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.icons.FOLDER_OPEN, size=80, color=ft.colors.GREY_400),
                    ft.Text("暂无内容", size=18, color=ft.colors.GREY_500),
                    ft.Text("点击下方 + 按钮添加内容", size=14, color=ft.colors.GREY_400)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            alignment=ft.alignment.center,
            expand=True,
            visible=False
        )

        self.content_column = ft.Column(
            [self.content_list, self.empty_view],
            expand=True
        )

        self.page.add(self.content_column)

    def _build_bottom_nav(self):
        self.nav_items = [
            ft.NavigationBarItem(icon=ft.icons.ALL_INBOX, label="全部"),
            ft.NavigationBarItem(icon=ft.icons.TEXT_FIELDS, label="文本"),
            ft.NavigationBarItem(icon=ft.icons.LINK, label="链接"),
            ft.NavigationBarItem(icon=ft.icons.ATTACH_FILE, label="文件"),
            ft.NavigationBarItem(icon=ft.icons.IMAGE, label="图片")
        ]

        self.bottom_nav = ft.NavigationBar(
            destinations=self.nav_items,
            selected_index=0,
            on_change=self._on_nav_change
        )

        self.fab = ft.FloatingActionButton(
            icon=ft.icons.ADD,
            on_click=self._show_add_dialog,
            bgcolor=ft.colors.BLUE
        )

        self.page.add(self.bottom_nav, self.fab)

    def _build_add_dialog(self):
        self.add_type_tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="文本", icon=ft.icons.TEXT_FIELDS),
                ft.Tab(text="链接", icon=ft.icons.LINK),
                ft.Tab(text="文件", icon=ft.icons.ATTACH_FILE),
                ft.Tab(text="截图", icon=ft.icons.IMAGE)
            ]
        )

        self.text_input = ft.TextField(
            label="文本内容",
            multiline=True,
            min_lines=3,
            max_lines=10
        )

        self.link_input = ft.TextField(
            label="链接地址",
            hint_text="https://example.com",
            keyboard_type=ft.KeyboardType.URL
        )

        self.link_title_input = ft.TextField(
            label="标题（可选）",
            hint_text="给链接起个名字"
        )

        self.file_picker = ft.FilePicker(on_result=self._on_file_picked)
        self.selected_file_text = ft.Text("未选择文件", color=ft.colors.GREY_600)
        self.selected_file_path = None

        self.add_dialog = ft.AlertDialog(
            title=ft.Text("添加内容"),
            content=ft.Container(
                content=ft.Column([
                    self.add_type_tabs,
                    ft.Container(height=10),
                    self.text_input,
                    self.link_input,
                    self.link_title_input,
                    self.selected_file_text,
                    ft.ElevatedButton("选择文件", icon=ft.icons.FILE_OPEN, on_click=lambda _: self.file_picker.pick_files()),
                    self.file_picker
                ]),
                width=400
            ),
            actions=[
                ft.TextButton("取消", on_click=self._close_add_dialog),
                ft.ElevatedButton("保存", on_click=self._save_item)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

    def _build_detail_dialog(self):
        self.detail_content = ft.Container(
            content=ft.Column([
                ft.Text("", weight=ft.FontWeight.BOLD, size=18),
                ft.Container(height=10),
                ft.Text("", size=14, selectable=True)
            ]),
            padding=10
        )

        self.detail_dialog = ft.AlertDialog(
            title=ft.Text("详细内容"),
            content=self.detail_content,
            actions=[
                ft.TextButton("关闭", on_click=lambda _: self.page.close(self.detail_dialog))
            ]
        )

    def _build_delete_dialog(self):
        self.delete_dialog = ft.AlertDialog(
            title=ft.Text("确认删除"),
            content=ft.Text("确定要删除这条内容吗？"),
            actions=[
                ft.TextButton("取消", on_click=lambda _: self.page.close(self.delete_dialog)),
                ft.ElevatedButton("删除", bgcolor=ft.colors.RED, on_click=self._confirm_delete)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

    def load_items(self, filter_type=None, search_query=None):
        self.current_tab = filter_type or "all"
        self.search_query = search_query or ""

        if self.search_query:
            items = self.storage.search_items(self.search_query)
        else:
            items = self.storage.get_items(filter_type)

        self.items = items
        self._render_items()

    def _render_items(self):
        self.content_list.controls.clear()

        if not self.items:
            self.empty_view.visible = True
            self.content_list.visible = False
        else:
            self.empty_view.visible = False
            self.content_list.visible = True

            for item in self.items:
                card = self._create_item_card(item)
                self.content_list.controls.append(card)

        self.page.update()

    def _create_item_card(self, item: dict):
        icon_map = {
            "text": (ft.icons.TEXT_FIELDS, ft.colors.BLUE),
            "link": (ft.icons.LINK, ft.colors.GREEN),
            "file": (ft.icons.ATTACH_FILE, ft.colors.ORANGE),
            "image": (ft.icons.IMAGE, ft.colors.PURPLE)
        }

        icon, color = icon_map.get(item["type"], (ft.icons.ARTICLE, ft.colors.GREY))

        content_preview = item["content"]
        if item["type"] == "link":
            content_preview = item["content"][:50] + "..." if len(item["content"]) > 50 else item["content"]
        elif item["type"] == "text":
            content_preview = item["content"][:100] + "..." if len(item["content"]) > 100 else item["content"]

        card = ft.Card(
            elevation=2,
            margin=5,
            child=ft.ListTile(
                leading=ft.CircleAvatar(icon=icon, bgcolor=color),
                title=ft.Text(item.get("title", "未命名"), weight=ft.FontWeight.W_500),
                subtitle=ft.Text(content_preview, max_lines=2, color=ft.colors.GREY_600),
                trailing=ft.PopupMenuButton(
                    icon=ft.icons.MORE_VERT,
                    items=[
                        ft.PopupMenuItem(text="查看详情", icon=ft.icons.VISIBILITY,
                                       on_click=lambda _, i=item: self._show_detail(i)),
                        ft.PopupMenuItem(text="复制内容", icon=ft.icons.COPY,
                                       on_click=lambda _, i=item: self._copy_content(i)),
                        ft.PopupMenuItem(text="删除", icon=ft.icons.DELETE, text_color=ft.colors.RED,
                                       on_click=lambda _, i=item: self._show_delete(i))
                    ]
                ),
                on_click=lambda _, i=item: self._show_detail(i)
            )
        )
        return card

    def _show_add_dialog(self, e=None):
        self.add_type_tabs.selected_index = 0
        self.text_input.value = ""
        self.link_input.value = ""
        self.link_title_input.value = ""
        self.selected_file_text.value = "未选择文件"
        self.selected_file_path = None
        self.page.open(self.add_dialog)

    def _close_add_dialog(self, e=None):
        self.page.close(self.add_dialog)

    def _on_file_picked(self, e):
        if e.files:
            self.selected_file_text.value = e.files[0].name
            self.selected_file_path = e.files[0].path
            self.page.update()

    def _save_item(self, e=None):
        tab_index = self.add_type_tabs.selected_index

        if tab_index == 0:
            content = self.text_input.value.strip()
            if content:
                self.storage.add_item("text", content)
                self._show_snack_bar("文本已保存")
            else:
                self._show_snack_bar("请输入文本内容", is_error=True)
                return
        elif tab_index == 1:
            url = self.link_input.value.strip()
            title = self.link_title_input.value.strip()
            if url:
                result = self.file_handler.save_link(url, title)
                if result["success"]:
                    self.storage.add_item("link", url, title or result["title"])
                    self._show_snack_bar("链接已保存")
                else:
                    self._show_snack_bar(result["error"], is_error=True)
                    return
            else:
                self._show_snack_bar("请输入链接地址", is_error=True)
                return
        elif tab_index == 2:
            if self.selected_file_path:
                result = self.file_handler.save_file(self.selected_file_path)
                if result["success"]:
                    self.storage.add_item(
                        "file",
                        result["path"],
                        result["original_name"]
                    )
                    self._show_snack_bar("文件已保存")
                else:
                    self._show_snack_bar(result["error"], is_error=True)
                    return
            else:
                self._show_snack_bar("请选择文件", is_error=True)
                return
        elif tab_index == 3:
            self._show_snack_bar("截图功能需要设备支持", is_error=True)
            return

        self._close_add_dialog()
        self.load_items(self.current_tab if self.current_tab != "all" else None)

    def _show_detail(self, item: dict):
        type_labels = {
            "text": "文本内容",
            "link": "链接地址",
            "file": "文件路径",
            "image": "图片"
        }

        title_text = self.detail_content.controls[0]
        content_text = self.detail_content.controls[2]

        title_text.value = item.get("title", "未命名")
        content_text.value = item["content"]

        self.detail_dialog.title = ft.Text(type_labels.get(item["type"], "内容"))
        self.page.open(self.detail_dialog)

    def _copy_content(self, item: dict):
        self.page.set_clipboard(item["content"])
        self._show_snack_bar("已复制到剪贴板")

    def _show_delete(self, item: dict):
        self.item_to_delete = item
        self.page.open(self.delete_dialog)

    def _confirm_delete(self, e=None):
        if self.item_to_delete:
            if self.item_to_delete["type"] in ["file", "image"]:
                self.file_handler.delete_file(
                    os.path.basename(self.item_to_delete["content"]),
                    self.item_to_delete["type"]
                )
            self.storage.delete_item(self.item_to_delete["id"])
            self._show_snack_bar("已删除")
            self.load_items(self.current_tab if self.current_tab != "all" else None)
        self.page.close(self.delete_dialog)

    def _on_nav_change(self, e):
        tab_map = {0: None, 1: "text", 2: "link", 3: "file", 4: "image"}
        filter_type = tab_map.get(e.control.selected_index, None)
        self.load_items(filter_type)

    def _on_search(self, e=None):
        query = self.search_field.value or ""
        self.load_items(filter_type=self.current_tab if self.current_tab != "all" else None,
                        search_query=query)

    def _show_snack_bar(self, message: str, is_error: bool = False):
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.colors.RED if is_error else ft.colors.GREEN
            )
        )