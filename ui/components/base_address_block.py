import flet as ft
from ..styles.styles import AppStyles

class BaseAddressBlock:
    def __init__(self, ):
        self._create_components()
        self._build_base_address_block()

    def _create_components(self):
        self.base_address = ft.TextField(
            hint_text="Dirección base en HEX",
            capitalization="CHARACTERS",

        )

    def _build_base_address_block(self):
        self.base_address_block=ft.Container(
            content=ft.Row(
                controls=[
                    self.base_address,
                ],
                expand=True
            )
        )