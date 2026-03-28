import flet as ft
from ..styles.styles import AppStyles
from RAM.dataRam import ram

class RamBlock:
    def __init__(self):
        self._create_components()
        self._build_ram_block()

    def _create_components(self):
        self.ram_list = ft.ListView(
            expand=1,
            spacing=5,
        )

    def _build_ram_block(self):
        self.ram_block_comp=ft.Container(
            **AppStyles.container(),
            content=ft.Column(
                controls=[
                    ft.Text("Memoria RAM", style=AppStyles.title()),
                    ft.Container(
                        **AppStyles.list_view(),
                        height=400,
                        content=self.ram_list            
                    )
                ]
            )
        ) 