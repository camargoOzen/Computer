import flet as ft
from ..styles.styles import AppStyles

class ModRamBlock:
    def __init__(self, on_modify=None):
        self.on_modify = on_modify
        self._create_components()
        self._build_mod_ram_block()

    def _create_components(self):
        self.address_field = ft.TextField(
            label="Dirección",
            hint_text="Dirección HEX (hasta 16 dígitos)",
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
            on_click=self.on_modify,
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
