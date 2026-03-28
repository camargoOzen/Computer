import flet as ft
from ..styles.styles import AppStyles

class CodeBlock():
    def __init__(self, title="", lines=20):
        self.title = title
        self.lines = lines
        self._create_components()
        self._build_code_block()

    def _create_components(self):
        self.title_text = ft.Text(self.title, style=AppStyles.title())

        self.code_editor = ft.TextField(
            **AppStyles.code_editor(),
            multiline=True,
            min_lines=self.lines,
            max_lines=self.lines,
            width=1500
        )

    def _build_code_block(self):
        self.code_block_comp = ft.Container(
            **AppStyles.container(),
            content=ft.Column([
                    self.title_text,
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=self.code_editor
                            )
                        ],
                        scroll=ft.ScrollMode.AUTO,
                        
                    )
                ]
            )
        )