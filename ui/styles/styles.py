import flet as ft 

class AppStyles:
    PRIMARY = "#222A59"
    SECONDARY = "#5666BF"
    TERTIARY = "#5670BF"
    UTIL = "#F2CD13"
    BG = "#020E26"
    # PRIMARY = "#385773"
    # SECONDARY = "#5A90BF"
    # TERTIARY = "#5F94D9"
    # UTIL = "#F2B366"
    # BG = "#090B0D"
    # PRIMARY = "#5E66F2"
    # SECONDARY = "#4B4FA6"
    # TERTIARY = "#6B7FF2"
    # UTIL = "#99A6F2"
    # BG = "#B3BDF2" 
    CODE_TEXT_COLOR = "white"
    TITLE_TEXT_COLOR = "#E3E3E3"
    BUTTON_TEXT_COLOR = "#E3E3E3"

    @staticmethod
    def title():
        return ft.TextStyle(size=24, weight=ft.FontWeight.BOLD)
    
    @staticmethod
    def list_text():
        return ft.TextStyle(size=18,color=AppStyles.CODE_TEXT_COLOR, font_family="serif")
    
    @staticmethod
    def file_text():
        return ft.TextStyle(size=13, font_family="serif")
    
    @staticmethod
    def container():
        return {
            "bgcolor": AppStyles.BG,
            "padding": 10,
            "border_radius": 10
        }
    @staticmethod
    def code_block():
        return{
            "bgcolor": AppStyles.BG,
            "padding": 10,
        }
    
    @staticmethod
    def code_editor():
        return {
            "bgcolor": AppStyles.PRIMARY,
            "border_color": AppStyles.PRIMARY,
            "focused_border_color": AppStyles.PRIMARY,
            "cursor_color": AppStyles.UTIL,
            "selection_color": ft.Colors.PINK,
            "text_style": ft.TextStyle(size=16, color=AppStyles.CODE_TEXT_COLOR, font_family="Courier New")
        }
    
    @staticmethod
    def list_view():
        return {
            "bgcolor": AppStyles.PRIMARY,
            "border_radius": 10,
        }
    
    @staticmethod
    def elevated_button():
        return {
            "bgcolor": AppStyles.TERTIARY,
            "color": AppStyles.BUTTON_TEXT_COLOR,
            "style": ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
        }
    
