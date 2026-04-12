import flet as ft
import os

class UI:
    def __init__(self, page: ft.Page, storage, file_handler):
        self.page = page
        self.storage = storage
        self.file_handler = file_handler
        self.current_filter = None
        self.items = []
        self.search_query = ""
        self.item_to_delete = None
        
        self.colors = {
            "primary": ft.colors.BLUE_600,
            "primary_light": ft.colors.BLUE_50,
            "secondary": ft.colors.AMBER_500,
            "text": ft.colors.GREY_800,
            "text_secondary": ft.colors.GREY_600,
            "background": ft.colors.GREY_50,
            "surface": ft.colors.WHITE,
            "error": ft.colors.RED_500,
            "success": ft.colors.GREEN_500,
        }
        
        self.type_config = {
            "text": {
                "icon": ft.icons.NOTES,
                "color": ft.colors.BLUE,
                "bg_color": ft.colors.BLUE_50,
                "label": "Text"
            },
            "link": {
                "icon": ft.icons.LINK,
                "color": ft.colors.GREEN,
                "bg_color": ft.colors.GREEN_50,
                "label": "Link"
            },
            "file": {
                "icon": ft.icons.INSERT_DRIVE_FILE,
                "color": ft.colors.ORANGE,
                "bg_color": ft.colors.ORANGE_50,
                "label": "File"
            },
            "image": {
                "icon": ft.icons.IMAGE,
                "color": ft.colors.PURPLE,
                "bg_color": ft.colors.PURPLE_50,
                "label": "Image"
            }
        }

    def build(self):
        try:
            self._setup_page()
            self._build_ui()
            self.page.overlay.append(self.file_picker)
            self.page.update()
            self.load_items()
        except Exception as e:
            print(f"Critical error in UI build: {e}")
            self._show_error_screen(str(e))

    def _setup_page(self):
        self.page.title = "File Transfer"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.bgcolor = self.colors["background"]

    def _build_ui(self):
        self._create_app_bar()
        self._create_main_content()
        self._create_bottom_navigation()
        self._create_floating_action_button()
        self._create_add_dialog()
        self._create_detail_dialog()
        self._create_delete_confirmation()

    def _create_app_bar(self):
        self.search_field = ft.TextField(
            hint_text="Search items...",
            hint_style=ft.TextStyle(color=self.colors["text_secondary"]),
            prefix_icon=ft.icons.SEARCH_ROUNDED,
            border_color=ft.colors.TRANSPARENT,
            bgcolor=ft.colors.WHITE24,
            border_radius=25,
            height=40,
            content_padding=ft.padding.symmetric(horizontal=15),
            on_submit=self._on_search,
            expand=True,
            text_size=14
        )
        
        self.app_bar = ft.AppBar(
            title=ft.Row([
                ft.Icon(ft.icons.FOLDER_SHARED, size=28, color=self.colors["primary"]),
                ft.Text("File Transfer", size=20, weight=ft.FontWeight.W_600, color=self.colors["text"]),
            ], spacing=8),
            center_title=False,
            bgcolor=self.colors["primary"],
            foreground_color=ft.colors.WHITE,
            elevation=4,
            actions=[
                self.search_field,
                ft.IconButton(
                    icon=ft.icons.FILTER_LIST,
                    tooltip="Filter",
                    icon_color=ft.colors.WHITE,
                    on_click=lambda _: self._toggle_search()
                )
            ],
            toolbar_height=65
        )
        self.page.appbar = self.app_bar

    def _create_main_content(self):
        self.content_list = ft.ListView(
            expand=True,
            spacing=12,
            padding=ft.padding.symmetric(horizontal=16, vertical=10)
        )

        self.empty_state = ft.Container(
            content=ft.Column([
                ft.Container(height=60),
                ft.Icon(
                    ft.icons.INVENTORY_2_OUTLINED, 
                    size=100, 
                    color=self.colors["primary"].with_opacity(0.3)
                ),
                ft.Container(height=20),
                ft.Text(
                    "No items yet",
                    size=22,
                    weight=ft.FontWeight.W_600,
                    color=self.colors["text"]
                ),
                ft.Container(height=8),
                ft.Text(
                    "Tap the + button to add your first item",
                    size=14,
                    color=self.colors["text_secondary"]
                ),
                ft.Container(height=30),
                ft.ElevatedButton(
                    "Add Item",
                    icon=ft.icons.ADD_CIRCLE_OUTLINE,
                    style=ft.ButtonStyle(
                        bgcolor=self.colors["primary"],
                        color=ft.colors.WHITE,
                        padding=ft.padding.symmetric(horizontal=30, vertical=15),
                        shape=ft.RoundedRectangleBorder(radius=20)
                    ),
                    on_click=self._show_add_dialog
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            alignment=ft.alignment.center,
            expand=True,
            visible=False
        )

        self.main_content = ft.Stack([
            self.content_list,
            self.empty_state
        ], expand=True)

        self.page.add(self.main_content)

    def _create_bottom_navigation(self):
        nav_items_data = [
            (ft.icons.DASHBOARD_OUTLINE, "All", None),
            (ft.icons.TEXT_SNIPPET_OUTLINE, "Text", "text"),
            (ft.icons.LINK_OUTLINE, "Link", "link"),
            (ft.icons.DESCRIPTION_OUTLINE, "File", "file"),
            (ft.icons.PHOTO_LIBRARY_OUTLINE, "Image", "image"),
        ]
        
        self.nav_items = [
            ft.NavigationBarItem(
                icon=item[0],
                label=item[1],
                selected_icon=ft.icons.DASHBOARD if i == 0 else item[0]
            ) for i, item in enumerate(nav_items_data)
        ]
        
        self.nav_filters = [item[2] for item in nav_items_data]
        
        self.bottom_nav = ft.NavigationBar(
            destinations=self.nav_items,
            selected_index=0,
            animation_duration=300,
            label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
            on_change=self._on_nav_change,
            bgcolor=self.colors["surface"],
            elevation=8,
            height=70
        )
        
        self.page.add(self.bottom_nav)

    def _create_floating_action_button(self):
        self.fab = ft.FloatingActionButton(
            icon=ft.icons.ADD,
            bgcolor=self.colors["primary"],
            foreground_color=ft.colors.WHITE,
            elevation=6,
            shape=ft.RoundedRectangleBorder(radius=15),
            on_click=self._show_add_dialog,
            extended=True,
            text="Add New",
            width=140,
            height=50
        )
        
        self.page.add(self.fab)

    def _create_add_dialog(self):
        self.tab_content = ft.Column([], scroll=ft.ScrollMode.AUTO, expand=True)
        
        self.text_input = ft.TextField(
            label="Enter your text",
            multiline=True,
            min_lines=4,
            max_lines=8,
            border_radius=12,
            focused_border_color=self.colors["primary"],
            hint_text="Type or paste your text here..."
        )
        
        self.link_input = ft.TextField(
            label="URL",
            keyboard_type=ft.KeyboardType.URL,
            prefix_icon=ft.icons.LINK,
            border_radius=12,
            focused_border_color=self.colors["primary"],
            hint_text="https://example.com"
        )
        
        self.link_title = ft.TextField(
            label="Title (optional)",
            prefix_icon=ft.icons.LABEL_OUTLINE,
            border_radius=12,
            focused_border_color=self.colors["primary"],
            hint_text="Give this link a name"
        )
        
        self.selected_file_info = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.ATTACH_FILE, size=18, color=self.colors["text_secondary"]),
                ft.Text("No file selected", size=13, color=self.colors["text_secondary"])
            ]),
            padding=10,
            border_radius=8,
            bgcolor=ft.colors.GREY_100
        )
        self.selected_file_path = None
        
        self.file_picker = ft.FilePicker(on_result=self._on_file_picked)
        
        self.select_file_btn = ft.ElevatedButton(
            "Choose File",
            icon=ft.icons.FOLDER_OPEN,
            style=ft.ButtonStyle(
                bgcolor=self.colors["primary_light"],
                color=self.colors["primary"],
                shape=ft.RoundedRectangleBorder(radius=10)
            ),
            on_click=lambda _: self.file_picker.pick_files(allow_multiple=False)
        )
        
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_length=200,
            tabs=[
                ft.Tab(text="Text", icon=ft.icons.NOTES),
                ft.Tab(text="Link", icon=ft.icons.LINK),
                ft.Tab(text="File", icon=ft.icons.UPLOAD_FILE),
                ft.Tab(text="Image", icon=ft.icons.ADD_PHOTO_ALTERNATE),
            ],
            on_change=self._on_tab_change
        )
        
        self._update_tab_content(0)
        
        self.add_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.icons.ADD_BOX, size=26, color=self.colors["primary"]),
                ft.Text("Add New Item", size=18, weight=ft.FontWeight.W_600),
            ], spacing=10),
            content=ft.Container(
                content=ft.Column([
                    self.tabs,
                    ft.Divider(height=1),
                    self.tab_content
                ], spacing=0),
                width=420,
                height=480
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    style=ft.ButtonStyle(color=self.colors["text_secondary"]),
                    on_click=self._close_add_dialog
                ),
                ft.ElevatedButton(
                    "Save",
                    icon=ft.icons.CHECK,
                    style=ft.ButtonStyle(
                        bgcolor=self.colors["primary"],
                        color=ft.colors.WHITE,
                        padding=ft.padding.symmetric(horizontal=25, vertical=12),
                        shape=ft.RoundedRectangleBorder(radius=10)
                    ),
                    on_click=self._save_item
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=20)
        )

    def _update_tab_content(self, index):
        self.tab_content.controls.clear()
        
        if index == 0:
            self.tab_content.controls.append(
                ft.Container(content=self.text_input, padding=20)
            )
        elif index == 1:
            self.tab_content.controls.extend([
                ft.Container(content=self.link_input, padding=ft.padding.only(left=20, right=20, top=20)),
                ft.Container(content=self.link_title, padding=ft.padding.only(left=20, right=20, bottom=20))
            ])
        elif index == 2:
            self.tab_content.controls.append(
                ft.Container(
                    content=ft.Column([
                        self.selected_file_info,
                        ft.Container(height=10),
                        self.select_file_btn
                    ], horizontal_alignment=ft.CrossAxisAlignment.START),
                    padding=20
                )
            )
        elif index == 3:
            self.tab_content.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.PHOTO_CAMERA_ALT_OUTLINED, size=60, color=self.colors["primary"].with_opacity(0.3)),
                        ft.Text("Image upload feature coming soon!", 
                               size=14, 
                               color=self.colors["text_secondary"],
                               weight=ft.FontWeight.W_500),
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    padding=40
                )
            )

    def _on_tab_change(self, e):
        self._update_tab_content(e.control.selected_index)
        self.page.update()

    def _create_detail_dialog(self):
        self.detail_title = ft.Text("", size=20, weight=ft.FontWeight.BOLD, color=self.colors["text"])
        self.detail_type_badge = ft.Container()
        self.detail_date = ft.Text("", size=12, color=self.colors["text_secondary"])
        self.detail_content = ft.SelectableText("", size=14, color=self.colors["text"], selection_color=self.colors["primary"].with_opacity(0.2))
        
        self.detail_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Column([
                self.detail_title,
                ft.Row([self.detail_type_badge, ft.Container(), self.detail_date], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ], spacing=5),
            content=ft.Container(
                content=ft.Column([
                    ft.Divider(),
                    self.detail_content
                ], scroll=ft.ScrollMode.AUTO),
                width=450,
                height=350
            ),
            actions=[
                ft.IconButton(
                    icon=ft.icons.CONTENT_COPY,
                    tooltip="Copy",
                    icon_color=self.colors["primary"],
                    on_click=lambda _: self._copy_current_item()
                ),
                ft.IconButton(
                    icon=ft.icons.DELETE_OUTLINE,
                    tooltip="Delete",
                    icon_color=self.colors["error"],
                    on_click=lambda _: self._delete_from_detail()
                ),
                ft.ElevatedButton(
                    "Close",
                    icon=ft.icons.CLOSE,
                    style=ft.ButtonStyle(
                        bgcolor=self.colors["background"],
                        color=self.colors["text"]
                    ),
                    on_click=lambda _: self.page.close(self.detail_dialog)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=20)
        )
        self.current_detail_item = None

    def _create_delete_confirmation(self):
        self.delete_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.icons.WARNING_AMBER_ROUNDED, size=26, color=ft.colors.AMBER_600),
                ft.Text("Confirm Delete", size=18, weight=ft.FontWeight.W_600),
            ], spacing=10),
            content=ft.Text(
                "Are you sure you want to delete this item? This action cannot be undone.",
                size=14,
                color=self.colors["text_secondary"]
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    style=ft.ButtonStyle(color=self.colors["text_secondary"]),
                    on_click=lambda _: self.page.close(self.delete_dialog)
                ),
                ft.ElevatedButton(
                    "Delete",
                    icon=ft.icons.DELETE_FOREVER,
                    style=ft.ButtonStyle(
                        bgcolor=self.colors["error"],
                        color=ft.colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=10)
                    ),
                    on_click=self._confirm_delete
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=20)
        )

    def load_items(self, filter_type=None, search_query=None):
        try:
            self.current_filter = filter_type
            self.search_query = search_query or ""

            if self.search_query.strip():
                items = self.storage.search_items(self.search_query.strip())
            else:
                items = self.storage.get_items(filter_type)

            self.items = items
            self._render_items()
            
        except Exception as e:
            print(f"Error loading items: {e}")
            self._show_snack_bar("Error loading items", is_error=True)

    def _render_items(self):
        try:
            self.content_list.controls.clear()

            if not self.items:
                self.empty_state.visible = True
                self.content_list.visible = False
            else:
                self.empty_state.visible = False
                self.content_list.visible = True
                
                for idx, item in enumerate(self.items):
                    card = self._build_item_card(item, idx)
                    self.content_list.controls.append(card)

            self.page.update()
        except Exception as e:
            print(f"Error rendering items: {e}")

    def _build_item_card(self, item: dict, index: int) -> ft.Control:
        item_type = item.get("type", "text")
        config = self.type_config.get(item_type, self.type_config["text"])
        
        title = item.get("title", "Untitled")
        content = item.get("content", "")
        created_at = item.get("created_at", "")
        
        preview = self._get_preview_text(content, item_type)
        
        type_badge = ft.Container(
            content=ft.Row([
                ft.Icon(config["icon"], size=14, color=config["color"]),
                ft.Text(config["label"], size=11, weight=ft.FontWeight.W_600, color=config["color"])
            ], spacing=4),
            bgcolor=config["bg_color"],
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
            border_radius=ft.border_radius.all(15)
        )
        
        leading_avatar = ft.Container(
            content=ft.Icon(config["icon"], size=26, color=config["color"]),
            width=52,
            height=52,
            bgcolor=config["bg_color"],
            border_radius=ft.border_radius.all(14),
            alignment=ft.alignment.center
        )
        
        card = ft.Card(
            elevation=2,
            margin=ft.margin.only(bottom=5),
            surface_tint_color=ft.colors.TRANSPARENT,
            child=ft.Container(
                content=ft.ListTile(
                    leading=leading_avatar,
                    title=ft.Text(title, size=15, weight=ft.FontWeight.W_600, color=self.colors["text"]),
                    subtitle=ft.Column([
                        ft.Container(height=4),
                        ft.Row([type_badge], spacing=0),
                        ft.Container(height=6),
                        ft.Text(preview, size=13, color=self.colors["text_secondary"], max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                    ], spacing=0, tight=True),
                    trailing=ft.PopupMenuButton(
                        icon=ft.icons.MORE_VERT,
                        icon_color=self.colors["text_secondary"],
                        items=[
                            ft.PopupMenuItem(
                                content=ft.Row([ft.Icon(ft.icons.VISIBILITY, size=18), ft.Text("View Details")], spacing=10),
                                on_click=lambda _, i=item: self._show_detail(i)
                            ),
                            ft.PopupMenuItem(
                                content=ft.Row([ft.icons.CONTENT_COPY, ft.Text("Copy Content")], spacing=10),
                                on_click=lambda _, i=item: self._copy_content(i)
                            ),
                            ft.PopupMenuItem(),
                            ft.PopupMenuItem(
                                content=ft.Row([ft.Icon(ft.icons.DELETE, size=18, color=self.colors["error"]), ft.Text("Delete", color=self.colors["error"])], spacing=10),
                                on_click=lambda _, i=item: self._show_delete_confirm(i)
                            ),
                        ]
                    ),
                    on_click=lambda _, i=item: self._show_detail(i)
                ),
                border_radius=ft.border_radius.all(16),
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS
            )
        )
        
        return card

    def _get_preview_text(self, content: str, item_type: str) -> str:
        if not content:
            return "(empty)"
        
        if item_type == "link":
            return content[:80] + ("..." if len(content) > 80 else "")
        elif item_type == "text":
            return content[:120] + ("..." if len(content) > 120 else "")
        else:
            filename = os.path.basename(content) if content else "Unknown file"
            return filename

    def _show_add_dialog(self, e=None):
        try:
            self.tabs.selected_index = 0
            self._update_tab_content(0)
            self.text_input.value = ""
            self.link_input.value = ""
            self.link_title.value = ""
            self.selected_file_path = None
            self.selected_file_info.content = ft.Row([
                ft.Icon(ft.icons.ATTACH_FILE, size=18, color=self.colors["text_secondary"]),
                ft.Text("No file selected", size=13, color=self.colors["text_secondary"])
            ])
            self.page.open(self.add_dialog)
        except Exception as ex:
            print(f"Error showing add dialog: {ex}")

    def _close_add_dialog(self, e=None):
        try:
            self.page.close(self.add_dialog)
        except Exception:
            pass

    def _on_file_picked(self, e):
        try:
            if e.files and len(e.files) > 0:
                file = e.files[0]
                self.selected_file_path = file.path
                self.selected_file_info.content = ft.Row([
                    ft.Icon(ft.icons.CHECK_CIRCLE, size=18, color=self.colors["success"]),
                    ft.Text(file.name, size=13, color=self.colors["success"], weight=ft.FontWeight.W_500)
                ])
                self.selected_file_info.bgcolor = ft.colors.GREEN_50
                self.page.update()
        except Exception as ex:
            print(f"Error picking file: {ex}")

    def _save_item(self, e=None):
        try:
            tab_idx = self.tabs.selected_index
            
            if tab_idx == 0:
                content = (self.text_input.value or "").strip()
                if not content:
                    self._show_snack_bar("Please enter some text", is_error=True)
                    return
                result = self.storage.add_item("text", content)
                
            elif tab_idx == 1:
                url = (self.link_input.value or "").strip()
                title = (self.link_title.value or "").strip()
                
                if not url:
                    self._show_snack_bar("Please enter a URL", is_error=True)
                    return
                    
                check = self.file_handler.save_link(url, title)
                if not check["success"]:
                    self._show_snack_bar(check["error"], is_error=True)
                    return
                    
                result = self.storage.add_item("link", url, title or check["title"])
                
            elif tab_idx == 2:
                if not self.selected_file_path:
                    self._show_snack_bar("Please select a file first", is_error=True)
                    return
                    
                save_result = self.file_handler.save_file(self.selected_file_path)
                if not save_result["success"]:
                    self._show_snack_bar(save_result["error"], is_error=True)
                    return
                    
                result = self.storage.add_item(
                    "file",
                    save_result["path"],
                    save_result["original_name"]
                )
                
            elif tab_idx == 3:
                self._show_snack_bar("Image feature coming soon!", is_error=True)
                return
            else:
                return
            
            if result:
                self._close_add_dialog()
                self.load_items(self.current_filter)
                self._show_snack_bar("Item saved successfully!")
            else:
                self._show_snack_bar("Failed to save item", is_error=True)
                
        except Exception as ex:
            print(f"Error saving item: {ex}")
            self._show_snack_bar(f"Error: {str(ex)}", is_error=True)

    def _show_detail(self, item: dict):
        try:
            self.current_detail_item = item
            item_type = item.get("type", "text")
            config = self.type_config.get(item_type, self.type_config["text"])
            
            self.detail_title.value = item.get("title", "Untitled")
            self.detail_type_badge.content = ft.Row([
                ft.Icon(config["icon"], size=14, color=config["color"]),
                ft.Text(config["label"], size=11, weight=ft.FontWeight.W_600, color=config["color"])
            ], spacing=4)
            self.detail_type_badge.bgcolor = config["bg_color"]
            self.detail_type_badge.padding = ft.padding.symmetric(horizontal=10, vertical=5)
            self.detail_type_badge.border_radius = ft.border_radius.all(15)
            self.detail_date.value = item.get("created_at", "")
            self.detail_content.value = item.get("content", "")
            
            self.page.open(self.detail_dialog)
        except Exception as e:
            print(f"Error showing detail: {e}")

    def _copy_current_item(self):
        if self.current_detail_item:
            self._copy_content(self.current_detail_item)

    def _copy_content(self, item: dict):
        try:
            content = item.get("content", "")
            if content:
                self.page.set_clipboard(content)
                self._show_snack_bar("Copied to clipboard!")
            else:
                self._show_snack_bar("Nothing to copy", is_error=True)
        except Exception as e:
            print(f"Error copying: {e}")
            self._show_snack_bar("Failed to copy", is_error=True)

    def _delete_from_detail(self):
        if self.current_detail_item:
            self._show_delete_confirm(self.current_detail_item)

    def _show_delete_confirm(self, item: dict):
        try:
            self.item_to_delete = item
            self.page.open(self.delete_dialog)
        except Exception as e:
            print(f"Error showing delete dialog: {e}")

    def _confirm_delete(self, e=None):
        try:
            if self.item_to_delete:
                item_id = self.item_to_delete.get("id")
                item_type = self.item_to_delete.get("type")
                content = self.item_to_delete.get("content", "")
                
                if item_type in ["file", "image"] and content:
                    filename = os.path.basename(content)
                    self.file_handler.delete_file(filename, item_type)
                    
                self.storage.delete_item(item_id)
                self._show_snack_bar("Item deleted successfully")
                self.load_items(self.current_filter)
                
                try:
                    self.page.close(self.detail_dialog)
                except:
                    pass
                    
            self.page.close(self.delete_dialog)
            self.item_to_delete = None
        except Exception as ex:
            print(f"Error deleting: {ex}")
            self._show_snack_bar("Failed to delete item", is_error=True)

    def _on_nav_change(self, e):
        try:
            selected_index = e.control.selected_index
            if 0 <= selected_index < len(self.nav_filters):
                filter_type = self.nav_filters[selected_index]
                self.load_items(filter_type)
        except Exception as ex:
            print(f"Error changing navigation: {ex}")

    def _toggle_search(self):
        if self.search_field.visible:
            self.search_field.visible = False
        else:
            self.search_field.visible = True
            self.search_field.focus()
        self.page.update()

    def _on_search(self, e=None):
        query = (self.search_field.value or "").strip()
        self.load_items(self.current_filter, query)

    def _show_snack_bar(self, message: str, is_error: bool = False):
        try:
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(message, color=ft.colors.WHITE),
                    bgcolor=is_error and self.colors["error"] or self.colors["success"],
                    duration=2500,
                    behavior=ft.SnackBarBehavior.FLOATING,
                    shape=ft.RoundedRectangleBorder(radius=10),
                    margin=ft.margin.only(bottom=20, left=16, right=16)
                )
            )
        except Exception as e:
            print(f"Error showing snackbar: {e}")

    def _show_error_screen(self, error_msg: str):
        error_view = ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.ERROR_OUTLINE, size=80, color=self.colors["error"]),
                ft.Text("Something went wrong", size=24, weight=ft.FontWeight.BOLD, color=self.colors["error"]),
                ft.Container(height=15),
                ft.Text(error_msg, size=14, color=self.colors["text_secondary"]),
            ], 
            alignment=ft.MainAxisAlignment.CENTER, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
            ),
            alignment=ft.alignment.center,
            bgcolor=self.colors["surface"],
            expand=True
        )
        self.page.add(error_view)
