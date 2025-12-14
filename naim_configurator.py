__all__ = []


def __dir__():
    return []


from flet import (
    VerticalDivider,
    ColorScheme,
    Theme,
    ThemeMode,
    AnimatedSwitcher,
    AnimatedSwitcherTransition,
    AnimationCurve,
    AppBar,
    FloatingActionButton,
    IconButton,
    icons,
    WindowDragArea,
    ButtonStyle,
    MaterialState,
    RoundedRectangleBorder,
    Page,
    BottomAppBar,
    Container,
    Row,
    colors,
    Text,
    TextAlign,
    MainAxisAlignment,
    Divider,
    AlertDialog,
    Dropdown,
    dropdown,
    TextButton
)
import flet as ft
# from flet_translator import TranslateFletPage, GoogleTranslateLanguage
# from naim_appbar import appbar
from naim_navrail import nav_rail
from naim_settings_container import SettingsContent
from locales import TextLocales


class NeuroFocusApp:
    def __init__(self, page: Page, date: str, app_version, license_type: int):
        self.page = page
        self.date = date
        self.lic_type = license_type
        self.app_version = app_version

        if self.page.client_storage.contains_key('locale'):
            self.textLocaled = TextLocales(self.page.client_storage.get('locale'))
        else:
            self.textLocaled = TextLocales()

        self.settings_content = SettingsContent(self.date, self.page, self.lic_type)

        self.language_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(self.textLocaled('change_lang_title')),
            content=Dropdown(
                label=self.textLocaled('lang_label'),
                options=[
                    dropdown.Option(
                        key='ru-RU',
                        text='Русский'
                    ),
                    dropdown.Option(
                        key='en-US',
                        text='English'
                    )
                ],
                border_radius=18,
                value=self.textLocaled.locale
            ),
            actions=[
                TextButton(self.textLocaled('okay'), on_click=self.change_language),
                TextButton(self.textLocaled('cancel'), on_click=lambda e: self.page.close(self.language_dlg))
            ],
            on_dismiss=lambda e: self.page.close(self.language_dlg),
            actions_alignment=MainAxisAlignment.END
        )

        self.appbar = AppBar(
            actions=[
                Container(
                    Row(
                        [
                            # FloatingActionButton(content=Text('Старт', size=18, text_align=TextAlign.CENTER,
                            #                                   font_family='Multiround'), width=90, bgcolor='#2aae4f'),
                            # FloatingActionButton(content=Text('Стоп', size=18, text_align=TextAlign.CENTER,
                            #                                   font_family='Multiround'), width=90, bgcolor='#ba2c4c'),
                            IconButton(icon=icons.MINIMIZE_ROUNDED, on_click=self.minimize),
                            IconButton(icon=icons.CROP_DIN_ROUNDED, data=0, icon_size=18, on_click=self.maximize,
                                       selected=False, selected_icon=icons.FILTER_NONE_ROUNDED),
                            IconButton(icon=icons.CLOSE_ROUNDED, data=0,
                                       style=ButtonStyle(
                                           bgcolor={
                                               MaterialState.HOVERED: colors.RED
                                           },
                                           shape={
                                               MaterialState.HOVERED: RoundedRectangleBorder(radius=5)
                                           }
                                       ),
                                       on_click=self.exit)
                        ]
                    ),
                    expand=1,
                    margin=10,
                )
            ],
            title=WindowDragArea(Row(
                spacing=0,
                controls=[
                    Text('LunarAim', size=30, text_align=TextAlign.CENTER, font_family='Multiround')
                ],
                alignment=MainAxisAlignment.SPACE_AROUND
            ), expand=True),
            center_title=True,
            leading=Row(
                [
                    Container(),
                    IconButton(icon=icons.DARK_MODE_OUTLINED, data=0, on_click=self.theme_change),
                    IconButton(icon=icons.MENU_OPEN_ROUNDED, data=0, on_click=self.extend_navrail),
                    IconButton(icon=icons.VOLUME_OFF_ROUNDED, data=0,
                               selected=self.settings_content.settings.bind_sounds,
                               selected_icon=icons.VOLUME_UP_ROUNDED,
                               on_click=self.bind_sounds),
                    IconButton(icon=icons.PUSH_PIN_OUTLINED, data=0,
                               selected=False,
                               selected_icon=icons.PUSH_PIN_ROUNDED,
                               on_click=self.pin_lunaraim),
                    IconButton(
                        icon=icons.LANGUAGE_ROUNDED,
                        on_click=self.change_language_btn
                    )
                ],
                expand=1,
                spacing=10,
            ),
            leading_width=245,
            bgcolor=colors.BLACK26,
        )
        self.navigation_rail = nav_rail(self.on_selected, self.textLocaled.locale)

        self.page.appbar = self.appbar
        self.page.bottom_appbar = BottomAppBar(
            content=Text(self.textLocaled.getBottomAppBarText(app_version), size=22, color=colors.ORANGE_ACCENT, expand=1,
                         text_align=TextAlign.CENTER),
            padding=0,
            height=30
        )

        self.page.window.on_event = self.on_window_event

        self.page.add(Divider(height=3, thickness=3, color=colors.DEEP_ORANGE))

        self.settings_container = self.settings_content.get_container('spoofer_content')

        self.settings_switcher = AnimatedSwitcher(
            self.settings_container,
            transition=AnimatedSwitcherTransition.FADE,
            duration=500,
            reverse_duration=500,
            switch_in_curve=AnimationCurve.EASE_IN_OUT_CUBIC,
            switch_out_curve=AnimationCurve.EASE_IN_OUT_CUBIC
        )

        self.settings_switcher_container = Container(
            expand=1,
            content=self.settings_switcher,
            margin=0,
            padding=0
        )

        self.main_row = Row(
            [
                Container(
                    padding=0,
                    margin=0,
                    bgcolor=colors.GREY,
                    theme=Theme(color_scheme=ColorScheme(primary=colors.DEEP_ORANGE, on_secondary=colors.DEEP_ORANGE,
                                                         secondary_container='#9C715A')),
                    content=self.navigation_rail
                ),

                VerticalDivider(width=1),

                self.settings_switcher_container
            ],
            expand=True,
            spacing=5,
        )

        self.page.add(self.main_row)

        self.page.on_route_change = self.on_route_change

        self.page.go('/')
        self.navigation_rail.selected_index = 1

        # tp = TranslateFletPage(page=page, into_language=GoogleTranslateLanguage.english, use_internet=True)
        self.page.update()
        # tp.update()
    
    def change_language_btn(self, e):
        self.page.open(self.language_dlg)
    
    def change_language(self, e):
        if self.settings_content.core_state_listener_ran:
            return 0
        self.page.client_storage.set('locale', self.language_dlg.content.value)
        self.textLocaled.locale = self.language_dlg.content.value
        del(self.settings_content)
        self.settings_content = SettingsContent(self.date, self.page, self.lic_type)

        
        match self.page.route:
            case '/':
                self.settings_switcher.content = self.settings_content.get_container('main_content')
            case '/neural':
                self.settings_switcher.content = self.settings_content.get_container('neural_content')
            case '/aim':
                self.settings_switcher.content = self.settings_content.get_container('aim_content')
            case '/trigger':
                self.settings_switcher.content = self.settings_content.get_container('trigger_content')
            case '/mouse':
                self.settings_switcher.content = self.settings_content.get_container('mouse_content')
            case '/bindings':
                self.settings_switcher.content = self.settings_content.get_container('bindings_content')
                self.settings_content.bindings_content_update()
            case '/spoofer':
                self.settings_switcher.content = self.settings_content.get_container('spoofer_content')
        
        self.page.bottom_appbar.content.value = self.textLocaled.getBottomAppBarText(self.app_version)
        self.navigation_rail.destinations[0].label_content.value = self.textLocaled('spoofer_tab')
        self.navigation_rail.destinations[1].label_content.value = self.textLocaled('main_tab')
        self.navigation_rail.destinations[2].label_content.value = self.textLocaled('neural_tab')
        self.navigation_rail.destinations[3].label_content.value = self.textLocaled('mouse_tab')
        self.navigation_rail.destinations[4].label_content.value = self.textLocaled('aimbot_tab')
        self.navigation_rail.destinations[5].label_content.value = self.textLocaled('triggerbot_tab')
        self.navigation_rail.destinations[6].label_content.value = self.textLocaled('bindings_tab')

        self.page.close(self.language_dlg)
        self.page.update()
        self.language_dlg.title = ft.Text(self.textLocaled('change_lang_title'))
        self.language_dlg.content.label = self.textLocaled('lang_label')
        self.language_dlg.actions[0].text = self.textLocaled('okay')
        self.language_dlg.actions[1].text = self.textLocaled('cancel')


    def pin_lunaraim(self, e):
        e.control.selected = not e.control.selected
        self.page.window_always_on_top = e.control.selected
        # print(f'[App] [I]: Always on top {e.control.selected}')
        e.control.update()
        self.page.update()

    def bind_sounds(self, e):
        e.control.selected = not e.control.selected
        self.settings_content.settings.bind_sounds = e.control.selected
        e.control.update()

    def minimize(self, e):
        self.page.window_minimized = True
        self.page.update()

    def maximize(self, e):
        self.page.window_maximized = not self.page.window_maximized
        self.page.update()

    def theme_change(self, e):
        if self.page.theme_mode.value == 'dark':
            self.page.theme_mode = ThemeMode.LIGHT
            self.settings_switcher.content.bgcolor = colors.BLACK12
            self.settings_content.bgcolor_theme = colors.BLACK12
            self.appbar.bgcolor = colors.BLACK12
        else:
            self.page.theme_mode = ThemeMode.DARK
            # self.settings_switcher_container.bgcolor = None
            self.settings_switcher.content.bgcolor = colors.BLACK26
            self.settings_content.bgcolor_theme = colors.BLACK26
            self.appbar.bgcolor = colors.BLACK26
        self.page.update()

    def extend_navrail(self, e):
        self.navigation_rail.extended = not self.navigation_rail.extended
        self.navigation_rail.update()

    def on_selected(self, e):

        match self.navigation_rail.selected_index:
            case 0:
                self.page.go('/spoofer')
            case 1:
                self.page.go('/')
            case 2:
                self.page.go('/neural')
            case 3:
                self.page.go('/mouse')
            case 4:
                self.page.go('/aim')
            case 5:
                self.page.go('/trigger')
            case 6:
                self.page.go('/bindings')

    def on_route_change(self, e):

        match self.page.route:
            case '/':
                self.settings_switcher.content = self.settings_content.get_container('main_content')
            case '/neural':
                self.settings_switcher.content = self.settings_content.get_container('neural_content')
            case '/aim':
                self.settings_switcher.content = self.settings_content.get_container('aim_content')
            case '/trigger':
                self.settings_switcher.content = self.settings_content.get_container('trigger_content')
            case '/mouse':
                self.settings_switcher.content = self.settings_content.get_container('mouse_content')
            case '/bindings':
                self.settings_switcher.content = self.settings_content.get_container('bindings_content')
                self.settings_content.bindings_content_update()
            case '/spoofer':
                self.settings_switcher.content = self.settings_content.get_container('spoofer_content')

        # self.settings_switcher.update()
        self.page.update()

    def on_window_event(self, e):
        self.appbar.actions[0].content.controls[1].selected = self.page.window_maximized
        self.appbar.update()

    def exit(self, e):
        if self.settings_content.stop_core(e) == 0 and self.settings_content.core_state_listener_ran:
            return 0
        self.page.window.close()
