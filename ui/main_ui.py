import flet as ft
from .layout.first_column import FirstColumn
from .layout.second_column import SecondColumn
from .layout.col3 import col3

class ComputerUI:
    def __init__(self, page: ft.Page):
        self.page = page
        self._setup_page()
        self._create_components()
        self._build_ui()

    def _setup_page(self):
        self.page.title = "Computer"
        self.page.bgcolor = "#090B0D"
        self.page.window.height = 800
        self.page.window.width = 1200
        self.page.theme_mode = ft.ThemeMode.DARK

    def _create_components(self):
        self.second_col = SecondColumn(self.page)
        self.first_col = FirstColumn(self.page, self.second_col.relocatable_code)

    def _build_ui(self):
        self.page.add(
            ft.Row(
                expand=True,
                controls=[
                    self.first_col.first_column,
                    self.second_col.second_column,
                    col3()
                ]
            )
        )

        self.page.update()

def main(page: ft.Page):
    ui = ComputerUI(page)

if __name__ == "__main__":
    ft.run(main)