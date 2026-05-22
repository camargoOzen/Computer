import flet as ft
from ..styles.styles import AppStyles
from CPU.storeOperationTracker import store_tracker
from RAM.dataRam import ram
import struct

class StoreResultsBlock:
    def __init__(self):
        self._create_components()
        self._build_store_results_block()
        self.refresh()

    def _create_components(self):
        self.store_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("RAM", style=AppStyles.list_text())),
                ft.DataColumn(ft.Text("Valor (HEX)", style=AppStyles.list_text())),
                ft.DataColumn(ft.Text("Entero (DEC)", style=AppStyles.list_text())),
                ft.DataColumn(ft.Text("Flotante", style=AppStyles.list_text())),
            ],
            rows=[],
            column_spacing=16,
            heading_row_height=40,
            divider_thickness=1,
            show_checkbox_column=False,
        )

        self.table_scroll = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[self.store_table],
            expand=True,
        )

    def _build_store_results_block(self):
        self.store_results_block_comp = ft.Container(
            **AppStyles.container(),
            content=ft.Column(
                controls=[
                    ft.Text("Resultados de STORE", style=AppStyles.title()),
                    ft.Container(
                        **AppStyles.list_view(),
                        height=200,
                        padding=10,
                        content=self.table_scroll
                    ),
                    ft.Text("Muestra el valor actual de las direcciones de RAM modificadas.", style=AppStyles.file_text())
                ]
            )
        )

    def _format_float(self, value_hex: str):
        """Format float value for display"""
        try:
            val_float = struct.unpack('!d', bytes.fromhex(value_hex))[0]
            if abs(val_float) < 1e-10 and val_float != 0:
                return f"{val_float:.2e}"
            else:
                return f"{val_float:.6g}"
        except:
            return "N/A"

    def refresh(self):
        """Update the table with current values of modified addresses"""
        modified_addresses = store_tracker.get_modified_addresses()
        
        # Ordenar direcciones por valor
        sorted_addresses = sorted(modified_addresses, key=lambda x: int(x, 16))
        
        self.store_table.rows = []
        
        for address in sorted_addresses:
            try:
                addr_int = int(address, 16)
                value_hex = ram.read(addr_int)
                value_int = int(value_hex, 16)
                value_float = self._format_float(value_hex)
                
                address_display = f"[{address}]"
                
                self.store_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(address_display, style=AppStyles.list_text())),
                            ft.DataCell(ft.Text(value_hex, style=AppStyles.list_text())),
                            ft.DataCell(ft.Text(str(value_int), style=AppStyles.list_text())),
                            ft.DataCell(ft.Text(value_float, style=AppStyles.list_text())),
                        ]
                    )
                )
            except Exception as e:
                print(f"Error refreshing store results: {e}")

    def clear(self):
        """Clear all modified addresses"""
        store_tracker.clear()
        self.refresh()
