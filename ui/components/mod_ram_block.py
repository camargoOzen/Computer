import flet as ft
from ..styles.styles import AppStyles

class ModRamBlock:
    def __init__(self):
        self._create_components()
        self._build_mod_ram_block()

    def _create_components(self):
        self.address_field = ft.TextField(
            label="Dirección",
            hint_text="Dirección en HEX",
            capitalization="CHARACTERS",
            width=200
        )

        self.word_content = ft.TextField(
            label="Palabra",
            hint_text="Palabra en HEX",
            max_length=16,
            counter_style=ft.TextStyle(size=0),
            capitalization="CHARACTERS",
            expand=True
        )

        self.send_btn = ft.ElevatedButton(
            "Modificar",
            **AppStyles.elevated_button()
        )
    
    def _build_mod_ram_block(self):
        self.mod_ram_block_comp=ft.Container(
            content=ft.Row(
                controls=[
                    self.address_field,
                    self.word_content,
                    self.send_btn
                ]
            )
        )

    def _mod_ram():
        pass