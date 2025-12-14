__all__ = []


def __dir__():
    return []



from flet import (
    NavigationRail,
    NavigationRailDestination,
    NavigationRailLabelType,
    Text,
    Image,
    ImageFit,
    icons,
)
from locales import TextLocales


def nav_rail(on_change, locale):
    textLocaled = TextLocales(locale)
    return NavigationRail(
        selected_index=0,
        on_change=on_change,
        label_type=NavigationRailLabelType.ALL,
        min_width=140,
        extended=False,
        min_extended_width=260,
        group_alignment=0,
        leading=Image(src=f'logo.png', fit=ImageFit.SCALE_DOWN, width=110, height=110),
        destinations=[
            NavigationRailDestination(
                icon=icons.VPN_KEY_OFF_ROUNDED,
                padding=3,
                label_content=Text(textLocaled('spoofer_tab'), size=18),
            ),
            NavigationRailDestination(
                icon=icons.HOUSE,
                padding=3,
                label_content=Text(textLocaled('main_tab'), size=18),
            ),
            NavigationRailDestination(
                label_content=Text(textLocaled('neural_tab'), size=18),
                icon=icons.DISPLAY_SETTINGS_ROUNDED,
                padding=3
            ),
            NavigationRailDestination(
                label_content=Text(textLocaled('mouse_tab'), size=18),
                icon=icons.MOUSE_OUTLINED,
                padding=3
            ),
            NavigationRailDestination(
                label_content=Text(textLocaled('aimbot_tab'), size=18),
                icon=icons.ACCESSIBILITY_NEW_ROUNDED,
                padding=3
            ),
            NavigationRailDestination(
                label_content=Text(textLocaled('triggerbot_tab'), size=18),
                icon=icons.ADS_CLICK_ROUNDED,
                padding=3
            ),
            NavigationRailDestination(
                label_content=Text(textLocaled('bindings_tab'), size=18),
                icon=icons.KEYBOARD_ALT_OUTLINED,
                padding=3
            ),
        ],
    )
