import flet as ft
from ..styles.styles import AppStyles

class ButtonPanel():
    def __init__(self, arr_btns={}):
        self.arr_btns = arr_btns
        self._build_button_panel()


    def _build_button_panel(self):
        self.button_panel_comp = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.ElevatedButton(
                    key,
                    icon=value.get("icon"),
                    on_click=value.get("func"),
                    **AppStyles.elevated_button(),
                )for key, value in self.arr_btns.items()
            ]
        )