import flet as ft
from ..styles.styles import AppStyles
from RAM.dataRam import ram

class RamBlock:
    def __init__(self, on_execute=None):
        self.on_execute = on_execute
        self.address_hex_width = max(4, ram.ADDRESS_BITS // 4)
        self.min_address = ram.CODE_START
        self.max_address = min(ram.MAX_ADDRESS, ram.UI_MAX_ADDRESS)
        self.visible_start = self.min_address
        self.visible_end = min(self.max_address, ram.DATA_START - 1)
        self.highlight_address = None
        self._create_components()
        self._build_ram_block()
        self.refresh()

    def _create_components(self):
        self.ram_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Dirección (HEX)", style=AppStyles.list_text())),
                ft.DataColumn(ft.Text("Palabra (HEX)", style=AppStyles.list_text())),
            ],
            rows=[],
            column_spacing=24,
        )

        self.table_scroll = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[self.ram_table],
        )

        self.address_range_text = ft.Text("Rango visible: 0000 - 001F", style=AppStyles.file_text())

        self.range_start_field = ft.TextField(
            label="Inicio (HEX)",
            value=f"{self.visible_start:0{self.address_hex_width}X}",
            capitalization=ft.TextCapitalization.CHARACTERS,
            width=190,
            on_submit=self._on_range_fields_submit,
        )

        self.range_end_field = ft.TextField(
            label="Fin (HEX)",
            value=f"{self.visible_end:0{self.address_hex_width}X}",
            capitalization=ft.TextCapitalization.CHARACTERS,
            width=190,
            on_submit=self._on_range_fields_submit,
        )

        self.apply_range_btn = ft.ElevatedButton(
            "Aplicar rango",
            icon=ft.Icons.CHECK,
            on_click=self._on_range_fields_submit,
            **AppStyles.elevated_button(),
        )

    def _build_ram_block(self):
        self.ram_block_comp=ft.Container(
            **AppStyles.container(),
            content=ft.Column(
                controls=[
                    ft.Text("Memoria RAM", style=AppStyles.title()),
                    self.address_range_text,
                    ft.Row(
                        controls=[
                            self.range_start_field,
                            self.range_end_field,
                            self.apply_range_btn,
                        ],
                    ),
                    ft.Container(
                        **AppStyles.list_view(),
                        height=400,
                        padding=10,
                        content=self.table_scroll
                    ),
                    ft.Text("Edite una celda o use el bloque de modificación para escribir en RAM.", style=AppStyles.file_text())
                ]
            )
        ) 

    def refresh(self):
        if self.visible_end < self.visible_start:
            self.visible_end = self.visible_start

        self.visible_start = max(self.min_address, min(self.visible_start, self.max_address))
        self.visible_end = max(self.min_address, min(self.visible_end, self.max_address))

        self.address_range_text.value = (
            f"Rango visible: {self.visible_start:0{self.address_hex_width}X} - "
            f"{self.visible_end:0{self.address_hex_width}X}"
        )
        self.range_start_field.value = f"{self.visible_start:0{self.address_hex_width}X}"
        self.range_end_field.value = f"{self.visible_end:0{self.address_hex_width}X}"
        self.ram_table.rows = [
            self._build_row(address, ft.Colors.GREEN_400 if address == self.highlight_address else None)
            for address in range(self.visible_start, self.visible_end + 1)
        ]

    def _on_range_fields_submit(self, event: ft.ControlEvent):
        start_raw = (self.range_start_field.value or "0").strip()
        end_raw = (self.range_end_field.value or "0").strip()

        try:
            start_address = int(start_raw, 16)
            end_address = int(end_raw, 16)
        except ValueError:
            self.range_start_field.error_text = "HEX inválido"
            self.range_end_field.error_text = "HEX inválido"
            self.range_start_field.update()
            self.range_end_field.update()
            return

        self.range_start_field.error_text = None
        self.range_end_field.error_text = None

        self.visible_start = min(start_address, end_address)
        self.visible_end = max(start_address, end_address)
        self.refresh()
        if event.page:
            event.page.update()

    def write_direct(self, address_hex: str, value_hex: str):
        try:
            address = int((address_hex or "0").strip(), 16)
        except ValueError:
            return False, "Dirección HEX inválida"

        cleaned_value = (value_hex or "").strip().upper()
        if cleaned_value == "":
            cleaned_value = "0"

        if any(c not in "0123456789ABCDEF" for c in cleaned_value):
            return False, "La palabra debe contener solo dígitos HEX"

        if len(cleaned_value) > ram.WORD_SIZE_HEX:
            return False, f"Máximo {ram.WORD_SIZE_HEX} dígitos HEX"

        normalized_value = cleaned_value.zfill(ram.WORD_SIZE_HEX)

        try:
            ram.write(address, normalized_value)
        except Exception as exc:
            return False, str(exc)

        return True, f"[{address:0{self.address_hex_width}X}] = {normalized_value}"

    def _build_row(self, address: int, highlight_color: str = None):
        current_word = ram.read(address)
        text_color_value = highlight_color if highlight_color else None
        
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(f"{address:0{self.address_hex_width}X}", style=AppStyles.list_text())),
                ft.DataCell(
                    ft.TextField(
                        value=current_word,
                        dense=True,
                        capitalization=ft.TextCapitalization.CHARACTERS,
                        on_submit=lambda e, addr=address: self._on_cell_submit(e, addr),
                        on_blur=lambda e, addr=address: self._on_cell_submit(e, addr),
                        text_style=ft.TextStyle(color=text_color_value) if text_color_value else None,
                    )
                ),
            ]
        )

    def _on_cell_submit(self, event: ft.ControlEvent, address: int):
        value = event.control.value if event and event.control else ""
        success, message = self.write_direct(f"{address:X}", value)
        if not success:
            event.control.error_text = message
            event.control.update()
            return

        event.control.error_text = None
        event.control.value = ram.read(address)
        event.control.update()