__all__ = []


def __dir__():
    return []


import flet as ft
from flet import Page, BottomAppBar, Text, colors, TextAlign
from interval_timer import IntervalTimer
from multiprocessing import Process, Value, Array
from hashlib import pbkdf2_hmac
from Crypto.PublicKey import RSA
from Crypto.Signature import pss
from Crypto.Hash import SHA256
from pickle import loads
from locales import TextLocales
import struct
import math
import time

import naim_configurator
# import license_client


APP_VERSION = '1.5.2'

exit_value = Value('i', 15)
data_err = Array('c', 100)
lic_type = Value('i', 254)

# libs = []


def loading_target(exit_value, data_err_value, lic_type_value):
    def loading(page: Page):
        page.window.center()
        page.window.width = 400
        page.window.height = 470
        page.window.title_bar_hidden = True
        page.window.frameless = True
        page.window.resizable = False

        page.padding = 0
        page.theme_mode = ft.ThemeMode.DARK
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.vertical_alignment = ft.MainAxisAlignment.CENTER

        if page.client_storage.contains_key('locale'):
            textLocaled = TextLocales(page.client_storage.get('locale'))
        else:
            textLocaled = TextLocales()

        loading_text = ft.Text(textLocaled('loading_modules_loader_text'), size=24, text_align=ft.TextAlign.CENTER)
        progress_ring = ft.ProgressRing(width=200, height=200, stroke_width=20, color=ft.colors.ORANGE)

        page.add(
            ft.Column(
                [
                    progress_ring,
                    loading_text
                ],
                spacing=50,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True
            )
        )

        page.bottom_appbar = BottomAppBar(
            content=Text(textLocaled.getBottomAppBarText(str(APP_VERSION), short=True), size=22, color=colors.ORANGE_ACCENT, expand=1,
                         text_align=TextAlign.CENTER),
            padding=0,
            height=30
        )

        page.update()

        # tp = TranslateFletPage(page=page, into_language=GoogleTranslateLanguage.english, use_internet=True)

        # page.update()
        # tp.update()

        # ===================================================
        import license_client

        # try:
        #     with open(license_client.__spec__.origin, 'rb') as file:
        #         lc_bytes = file.read()
        # except:
        #     loading_text.value = 'Integrity check failed'
        #     loading_text.update()
        #     progress_ring.color = ft.colors.RED
        #     animate_ring(progress_ring, 0.8)
        #     exit_value.value = 1
        #     time.sleep(2)
        #     page.window_close()
        #     return 1

        # try:
        #     lc_sign_len = struct.unpack('=Q', lc_bytes[-8:])[0]
        #     lc_sign = lc_bytes[-lc_sign_len - 8:-8]
        #     lc_extra_len = struct.unpack('=Q', lc_bytes[-lc_sign_len - 16:-lc_sign_len - 8])[0]
        #     pub_key = loads(lc_bytes[-lc_sign_len - 16 - lc_extra_len:-lc_sign_len - 16])
        # except Exception as e:
        #     loading_text.value = 'Integrity check failed'
        #     loading_text.update()
        #     progress_ring.color = ft.colors.RED
        #     animate_ring(progress_ring, 0.8)
        #     exit_value.value = 1
        #     time.sleep(2)
        #     page.window_close()
        #     return 1

        # verifier = pss.new(RSA.import_key(pub_key))
        # h = SHA256.new(lc_bytes[:-8 - lc_sign_len])

        # try:
        #     verifier.verify(h, lc_sign)
        # except (ValueError, TypeError):
        #     loading_text.value = 'Integrity check failed'
        #     loading_text.update()
        #     progress_ring.color = ft.colors.RED
        #     animate_ring(progress_ring, 0.8)
        #     exit_value.value = 1
        #     time.sleep(2)
        #     page.window_close()
        #     return 1

        # for lib in [naim_configurator.__spec__.origin, __file__[:-2] + 'cp311-win_amd64.pyd']:
        #     if lib is None:
        #         continue
        #     try:
        #         with open(lib, 'rb') as file:
        #             lib_bytes = file.read()
        #     except Exception as e:
        #         loading_text.value = 'Integrity check failed'
        #         loading_text.update()
        #         progress_ring.color = ft.colors.RED
        #         animate_ring(progress_ring, 0.8)
        #         exit_value.value = 1
        #         time.sleep(2)
        #         page.window_close()
        #         return 1
        #     try:
        #         lib_sign_len = struct.unpack('=Q', lib_bytes[-8:])[0]
        #         lib_sign = lib_bytes[-lib_sign_len - 8:-8]
        #         lib_extra_len = struct.unpack('=Q', lib_bytes[-lib_sign_len - 16:-lib_sign_len - 8])[0]
        #         lib_extra = loads(lib_bytes[-lib_sign_len - 16 - lib_extra_len:-lib_sign_len - 16])
        #     except Exception as e:
        #         loading_text.value = 'Integrity check failed'
        #         loading_text.update()
        #         progress_ring.color = ft.colors.RED
        #         animate_ring(progress_ring, 0.8)
        #         exit_value.value = 1
        #         time.sleep(2)
        #         page.window_close()
        #         return 1
        #     lib_junked_hash, lib_offs, lib_salt, lib_iters, lib_hash_len = lib_extra
        #     lib_hash = b''

        #     for i in range(len(lib_offs) // 2):
        #         lib_hash += lib_junked_hash[lib_offs[i * 2]:lib_offs[i * 2 + 1]]

        #     if not lib_hash == pbkdf2_hmac("sha256", pub_key, lib_salt, lib_iters, lib_hash_len):
        #         loading_text.value = 'Integrity check failed'
        #         loading_text.update()
        #         progress_ring.color = ft.colors.RED
        #         animate_ring(progress_ring, 0.8)
        #         exit_value.value = 1
        #         time.sleep(2)
        #         page.window_close()
        #         return 1

        #     verifier = pss.new(RSA.import_key(pub_key))
        #     h = SHA256.new(lib_bytes[:-8 - lib_sign_len])

        #     try:
        #         verifier.verify(h, lib_sign)
        #     except (ValueError, TypeError):
        #         loading_text.value = 'Integrity check failed'
        #         loading_text.update()
        #         progress_ring.color = ft.colors.RED
        #         animate_ring(progress_ring, 0.8)
        #         exit_value.value = 1
        #         time.sleep(2)
        #         page.window_close()
        #         return 1
        # ===================================================

        from license_client import open_license, is_online, generate_uid_file

        # from datetime import datetime
        from babel.dates import format_datetime

        RPI = license_client.encrypt(b'LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JSVNRZ0lCQURBTkJna3Foa2lHOXcwQkFRRUZB\nQVNDRWl3d2doSW9BZ0VBQW9JRUFRRHZrc1BMY3JsRVE2dEgKQXlIZWI3L2QwSGxIWjR6Ukw0Rnl5\nU0t5aThrWGxHaUc0VmF2V1NURjdmSTZzcnNnRHR2S0NNcUZ0TlhJWDUyZgpXUFZXTEEycWovZzk5\nckZQMWRNT1dYTElRVHJ0TVhCV0NHQ3UwMklPTGZWUEZrYUFHcml5UjhIZTA5S2paOFNjClpYS091\nTHMvc2dhWlY3ei9wV0F4OEVBMnBZV0VpY0lhZE13SWtEaUltMC9SYkJrVWJTblZENE14VkZncnVy\nV0MKcGZHNFhkd1lxZ2ZDU1g5NVg4V3hNeXlIcTZkZG9FaFBvcUlJbUhQeThjQ2dzQXg4SUFoQUxE\nakdzUElCNHRwTwowQTRRcE1qSXNVZjlSRjZDK205MXdldDNJOENYZzV0SUdqS0R4amE2TmxBVkVk\nWFNkSjUxT2wvbTRKUmlXbVkxCkdTK2I3TzJnc0RzRThVUDRJREoyQ25tQmZFM1AzWFJvWWpudElH\nWGtFOHNqSVp4TzJZNDNXZWxyTGtic1puUGwKRVdMcWRmZk04SGNEUFZQQlgyNzZTRkFYMjlWcnFv\nemt0ckttVE9BUHQ5WDlBajczVERIUld6MXMyb001RjdIcAo1MmF1MXhyRnpoZGVCYlpKK2UySEh4\nRkNJNHdqVGVKT2QvYWsxYW1OMEVKQTlDRWF6bDdlbHJndENhbnJJTi9EClRhRTdIYlZiZmg1Sksv\nRWlvS1hHa1F5c3JjQ1BUSnorUVAxU3NrRkYzUTlETTh2WkZxSHQ4VHdGdFZZQ2hibHMKRFgxOW5H\nMEcrUE1qckF4NlpzV1ZjOEQ4NWJhVDI0eFBWeTBtQVprQWMxVmRrZm8wRFFvZzI5aFdmclkwR2pF\ndApyWSsvQi9VbzJkanN0b0VDa3VGRUVKU1Fubk5iNVgxVldndSs5K0FyZzFBVUxLWllNRE15RDNk\na1ZjamtNZHJMCmVsQWtSYzhCclNFa3RlTjlvemx0MGIxY2ZxZE1ZTGJYQ2tMb0xKM29OWWZXdE5t\nV2tOM0tKUzZaUm8rd2VUUnIKeEJ3NUVUbEhXWldFdjlVc3hPaXUzdTlPMkNPTWxjbkcvRG1CREhR\nZUxDZlhZZmNmemlrSlBDM2YvaVYvNWh0RwppU0NkaHg5WnJQK2lyazZTMXNvd0NkNHRielloU1pL\ndDhPNFpHKzZJM2s0dklSU1VBb25BcS9DUHlWS1h5Sm9ZCnFHalZRZFJWekhWRzNTQnZzblI5aG54\nQStoUmgvMjhySU1GVmNPUy9FdHhPQ2VrZGJ1T2RUWmRLdmh6WVdydWUKb3grOWxTeW1tcnArRjJt\nTEJySlBkdVZEK3d0TWdKVVo1bEVHeFU0YTEzQUNiT0xtQ3QzT1ZQZ0xORnlJeXZDUQpIVnlKN0ZV\nOHFwKzVUNXdvU0hBTVQ4bzBUZENDWVJwQVFHV3dpOWNQL2cyVkw0Z3FCaS94WmJqSVNhdkN0L0xZ\nCjN4MzhjdWZLVUNKbHpzYk5rOUdKeUVaYlg0NHVhcUViUjlKdDQ5cVBSTDI2TkVnU25DQ2I0eVJH\nRVArQ2JLZzIKdHo4SXV3N0lPQnFJdVFjN0lyNURaWDVUVytkdnVTQTBMQjFaYVhZc0V2YlVETXVF\nK29lL2NicjIxMnVGenprRgpZMi9mK2pFOG51RFZBU1VqcDgwM0o1UE5oMVo4RTA0WTVWNUl6cW5l\nb2I3c1pJNExaM0dnelBFR1AxTXpvMk9nCjNiSVI5S0dZVE91K0dCeTZXaVY2anJZQmZoM2R4WkRr\nbFo1b3A0MG50eU9uYkUxSXc1RVhmSGFENGkwZ2dNL1AKVWpldG9ZS2xBZ01CQUFFQ2dnUUFmaVU5\nUzBiaEhueXpGdlVqUkVoN01vU3ZGMVlDNDdLcjZwRFY0RVdTWVFRWAo5YzE1STJOQTVhZGd3RitV\nQUZGU2taTUhjRmZEcVhvUE9QUlNXa2xmK010TjN2S2ljbk1ZYXBuV3duTDJZQ2FFCkRBamxQNmky\nSE5rK0xhS0JCTHNOUFhKak5yMDZVQ2czY2xKSWU3WHhncHh1dFJkcHdRS0hJRVJzeTFsa2NHRkkK\nL3owNG9kbXVxdDk4cTd6TGgrSGpBUGptRDNkbDVjQ3VDbGp1YWpHaHpxclk0d2hvUXJTWEY3TG1Z\nNW1TeXMyMgp4WmZRMGMzVVg3dkR2ZGgwK25hellYYm5mbGQxVm1Eb3FrOEsyT0NyaUdFd2tyOEpO\nTlpCRWpSRms3b1RrclFOCmMyMjM0NExmRmpXNi9SMGpCV202ZGVlQ3o4SzQzd0RTaUdyMmtwZXls\nOFd6amVxcjYxNm9zMWJZbThHa0J5dUkKTzk1Y3Vlc3hPMkxndDJMZk52VisyTTVUQmNpY042WEtx\nSGI3S3BGckpWSUltSUFXTmQvV1E1c0g4VWdqbkVsMQpYb2lFa09ReHBwVVo2OXJlNU1BT0N6cUxv\nV0Y5YnZaM0M3NTRadCtFalZyekd1TFBGU3l3VVZHZWVNRFc3VS81Ck5YQWRRclh1VFdtM09SUlN5\naGFZQllRKy9oZjBqSVlHeklOM3ZmVHFwWDVHM0NoekU5U2E5Vzh5eVVuRDlyQlUKaWR3V2h4Q3RK\nZWc4UFJwczM2WDNKWjY4Q0JWdmNHeVJNYi80cjhkSjhUM3NhSUFUSWZBellYcE54OXY4d3VYNwpm\nMXRidm9OZzJNZmh6eDhxSzNZaU95TUhTcVAxdElHR0c1TWorV1pyUkZOUTBYTlhnczlzSmJiRlEx\nRHJWUnNBCmtqL3RObFVKVGk3VUNRaGZwTzZ5d2EwOURUenNnUUs1RDQzV2x0dmRpWkxWeHlmbDJ4\nNW9wQTVETnlta0VyaHEKeFN3VHdCbGx1RFEwN1lFUUdKWDRXaHlVT1Zqd3pOOXpFaTc4V1pWY3Ar\nUUV6Y0hPcHp4a3ExSHY5Tlk2MWdKRQpTOHdlVEJKcDdrU2hER1NybU5WSVJSdUtMcGVxUHRpSUlC\neDdQaHhCYnVnQXdvR0l3SkpUTUdTVFVuWVRCT3JaCmt5Wi9od2pPa1JYdVBrZU9xTE5JZ0NnUXBy\nUTluWE5IYlV0dnA4ZkNNbEF1aWl4RU8rQ3BPaC8yV3hTQy9zSTYKdUZ0MVhtRTBueGFyMHVRdUQ2\nUDFSRjRoNjVBa3lQa1FpeGVCNEFSSytwckRuYmhQdm5qNmZJNzZqeWR6bUtKNQo2YlFVVUhrOVFz\ndTB6eU1sNHdiSWRqM0ozMUpyS0VIQXhKdXI3dTZ2TjYyMnlyTytjNk5QbjJiTEhvNzBwUVBGCnBG\najJKd1Ywdy85NTd2c2JRb1RycFpQRTcvZSsyYUVYd05neVFkYlZuUFJMQURSUS9mNEI3Q3haQ2xh\ndU5XTWkKRGJzcit0NEFaSzZpbDl6TDNJY1AxS1Y1aGp0N2VCK2pqZ3RyMGFwekZGa2FvdDYyMktp\nSGI2M3l5TkhPWHpwNgp6ZDVWaWR2SEh0bDZYbzl0Nys5LzVoa1E4Tzc1Qy85VGZQOXVFcW9BVFhv\nYlJUUWx0S1VUUkNqR1dGU3N0citoCkJhb2pSTkVVdU11UjZPNU5wTlJmaHFDdGlPNHc4bEtWK000\nSFlZMDJEdjRYaklCb3VmZThnc2ZDTkw0S0VBcGEKMDR6dEkwdVNTRVgwT0dYZ1g4UTFNQmcwQ0VE\nbVRoS0Vmb0FWKy9Sb0FRS0NBZ0VBK0Z6Y05yZ2JiVnFzRzRDZwordHFlTWZSTXBQUXQrUWxYUzZm\ncVpBdG5ORnZocUV0ckUwMFF2eExsRGYwNDNpV1FvYTZONzFyb2dXYWlHU0tPCmlOUU5zUGFmN2VM\nNUNlUjVMUUwxQUlmekFwTTF6QWJDa1V1enA5RzdrWmFJM2tmcVV1SXBPUUpLTkZjQlF2dUIKclln\nalFMWVorbXZjMmVyeVRSSkY5Z3M5L0pkRjlxTUxrNmF5Vnl5emlXcUVZOWRXWFUzNWFJRE1lZk5D\nSGhBVAovZTdVakt5SlNRaE5aSExLVXBKYUZCSHJ3RWxHWVVYaTgvMWUraDJDL3N3RjFXS0wwS3k0\nUjF6K0gvRGYyMC95Cmh2YlI2UUpKNDFoSWFuRHFaZ3VxUGN1SjVFcEZ1TXQyci9aYzNTYjdTM2lX\nWnB6MFRzTGptaWhwRFJXaHBKWjUKVGFDMWFMbEhaUUhnVUkrZjZjU2g4NjQ4c3Y5aG9jcm12QnhK\naDVLRmRUV2FzRjdjYW5ZUGJ5SFBtK3pLMmdzWApqQmF0RUZjMW1aOFNSNnNOSURyOVpITWtKcEdF\nMXdLcStZcU9VTUpzcXZ6OWRSOXJ5SHVFRzJibmhMMExlSmg3CkVsWkNiZzF0MjFpTk1pVDIwYnd6\nakl5V0g4Z0hFdURBZW5nMGpJNHcwVzl5UFlpQkRwSitxMlZiZFhQOFZuZ1UKdVlxb1dNdFNnOHZC\nMnM3bkJLSkRrNE1SQTVCWmVRYStTdWdBNnVKNnVxOE40VHF1a2ExeGViY1RBS2dOYW4vcQozK2Ri\nQ0xvWDFXMWNRZmhlSVQrLzFzTDBma0xmSGhqc20yRlNsbjFOU0hpNUI4UkdaQ0w5MUE0VkQxOUZr\ncnRHCkM3aVNrTENzWnFVb2RJN1poVnA2dE1wN2s0RUNnZ0lCQVBid3RwTEc3Ukdiejh6T2NpeTJX\nWHBIcElFY3VmbDUKT3luSXkvZVRiNDljV1NSU1dkSW4wUGxJa0haNTJyb0QybGJCbFhRaUE4T1hF\nMUgzWUhjV05VMkcxZFN1OXZKawpLdjlxTjlidXJmQjBrbzVXa0FCY3lWcHg5d25BTjJvMkFLUm1I\nS3Jwd2tzcStRdlg0eE94VytnS09hMjV1M0pvCkp6MFhsNjcxZGZvY29aMVo4bmh2dVpnT1dSOWli\nNUs3NmtJUGhQV1RCcDl6SC9uMjFFRllPRWJTeWRWVFppMDQKTDVkdTVzTEZlaVhIWFhLZUhJVEJs\nRlo2YWpnR3NWL2g0eENTZXo5WnBHUStRU3FreFpCNVJWQjdBQmhwWVFMbQo3M293NWZrUXRoREo5\nekNVWEZDYUpkV1hnMW92eThWTUVId0U4a29idHhxUDdpSllva1NabXBLU0pLRmoreWRtCjlNWThY\nQmxtbWdQU0VLYmRKbTBJc0ZZSzhHS3FMQVpEVTNlT1lOYS9NajlIOXZLK0JCWVdmZ1d0bVdyRjVE\na0cKWGhxOWt3RnNDbXRCelF1c1F5aWNuWldZQ2twV2hZWmd6Q3Fxdzd0ZjBOYVdiKzk1SmY5em9I\nQTArd0xBRTNqeAoxcHVtMDJOMFN4NXQzY1Y3a1hMY1J1UFBzZEs3NythNlVNWEFlSkhwUGxXKy80\nQkg5SWtKSmNNaWxhNnVjL0hKClpEQUZ6bzltNlJqWWNEQzBxQlJiNnJoY3QzUHpnMnU3K2JQZEs3\nZlVCZFhVVTJIa1l6S2MvR0lOeVhhUkRoVEMKU3I4eG8wVldnUFQ3SVFSZi85Lzl0K1QzZDVONzQ3\nQjZ2SDJEOWhjVy82YThFVlFwYVVqWjFySVd4VmxBU1o5TApTaWRuVGxwcFNiRWxBb0lDQUZlKzV3\nWm1FVHFYV0VyM0xPaXpxRVJaM1dKQjZxUWJpcjN0K3orUlQ4c04wekhVClEyWTBTZ0JYdXBrd3A1\nREVrTTZ1anZMTG1XMXVSMEsrRk1GK3ViK1Z3bmNYUTRrZE1UcVgydHR2TElueVhJVlMKdGhjRE9k\ndkdtNUFhTVF6bk40QkU2dTk3UWFBd1JQL1hQNytCWTRNUFV5cElSV1N3UHg2L24vd0hpTVRlNVJi\nNApEN1VBcGUxcW01dW5DRk1GMXp0cnV2d1MxU3NZcUhsYWtOV2NOWGZsMVRMNlBlMkpLTFgzZ3Qr\nb1hUUTRMeWRhCnU0NGNMQndOcFNSRURLT1JCM2lZTFJyNVhjY0hJTytvMVRTZHF4ZTVlVVZiQVdx\ncHJnYVRoSGdFbXhrT3JJZFgKU3Yxcit1OGZRSlV2YTJPaGZDYi9iODRkRE5CVW5pRTZFRzArcEJq\nMXJLV2cvaEU0VFBVWVJXZUVYV21ZRkhSRwo3VEgwaEgzalpFYyt3d0lnNFpxelQweWlFMmt4UlpH\nM2JZQk8ycUgxVGJpU25MQzVYQS9SQjRrZnJOdjdlWVZGCktnYXp6d2YxU05NNFFvdklxQm5TbVov\nY3dWc0NOelZLR2VFbW5KMnBIUERyM2lhakxKaDQ5M1ZtamZ0NGZoZEwKVkhWd1ZwQjZCQUZhY0hB\nUTlCZWo1aUREMUlZd2ppdzJqSXZvMHdWY0FERVVJYzhlWGp3aTMrRVQ0MFR4RU10VAplSk9hV0Fp\na0wxd1pVTHdNTVhUQ1pGN3VNVWFBR1ExUldEZjIweERJUG5kbkJidEE5bkNreHpBbS9KNUhIZkRT\nCk9YWEQ4cHU4ZFR0dmUxK2xGb0YyWTFzeUJuckIzQ0MxRFZCQ3kzVlhGZkhGMC84cUlPdWVSYy90\nNGE4QkFvSUMKQVFDTmxhYVlzWVhydXJLQ2N6dnpkdm9HcWwwZnlpQzNjVk1DdWlaNFpRaHA0a0Vh\nR2oxMXlXNS8vNk1VeXZrbAovbCtKcnFUS1dWWmZKcGZsUHprSURxdXhMOFlhazlielU0dHp0cXNk\naU93aUdqU05lQVJJc09xaCtRWHppVW84Cms0bjZ1TEZuTFhCQk9QcGlWLzNTcExaVmJNZDFYRENs\nZ0NJL1hPK1RXUm16dGdiVCtXYVV0enBxZkkrTTl4dVIKdmp5cWM4dUFJalNCNTdoRjBjZ1JUMHUx\nRDlhNWdYL3NIWExzR0tJbXVxTTJWZ0MyWHdGcS9MTFlnb2UwWitINwpYOENaRitPaWh2dENubzh1\nckJxNm8wMml2Mk5tbThVTHJPMVIyZ2VCcnBzMU5SZU51d0xURkE3dFVGbjNzNy9aCjk2cmI4Tm9h\nczVsZ21YV29LN21lSzVQOHhkNUt5dENOM3ZJcFZ5SlhUZ1N3ZkJrZ0UxeWMxNGFEVHZKVkg4enUK\nS2x3SkNKRnRqMkozOWdNWld1bHM0S2lSQ09BVjRERGlvVXdEZVA1NHFrR3ZEYU5MTmhHcmoyQ3JE\nT21aaGRJNQpJZmJ0MzhzcCs5MzVxM2V5am52QzQ4RHhsTzcydkxwdGRmdmVjdUJ3L1pTMGRibmFL\nT2RVUEFoSlJpUm05MnF0Cmw5WUlERHNWTGU2WHExTkRjZjQ3TkF0NnZyR2ozbEtNSnpSU2RJSGlw\ndGF2Y0NtalEzRzdlcGd4N0xjaXZGUjEKeU9sNnZ5ejUwWThtOHY1NytqOEdIZ3gzREFDZkFyeFlH\ncTVRd1YwanZGMWtHVGp0RVQzY1o5U3dhMU1jTk1Sdgp3MitmWjdJSnV4NEpzM3NjRGtKWGlzOFdm\nUWZhRElvcDB6bEpMbW8yWEhmc0lRS0NBZ0JHVDJ6MnpLcFdZZmR2CmFOYVlYaGJVM1draVJyUWpt\nc2Rmd0JyZ0VhMDdCRThNNU5kK2Y1dnVCcDNCTEFaZS9OZUpKUE9PZ1IwQjNlM24KVkZZWnRwSHJi\nMTBSVmRBbjBweDhwWlB0OEM1M29xQjlOTWV4dGs3cHFhRUJON1JyU1g4aFBOS0Zjd1Zzc1c4MQpk\nVFFvd3B1N1ZFV2w2RmhWdURTaWluTHdXblliQ1RhQkxRNVduQjQ3Y0FPZ1l6Nzd5Q1hzcWpGS083\nL3l4SkV6Cm5oTEVLUmZyUFVDYWQyOC9lWGg3aHRRb1NUd28rOUdJdThjdFFwcGhtMTZVYVc0eURY\ncDk4dnBIWi9zc1NjSkYKaFlBQTRQTUhNbzltRms2cUFvOG5JcjBKRHdqUGxXVkwyN3B6MjRoOVdk\nSk5HNzNsYlh2RUlNVVIxajY3UVFVSQp6SXFYaGtTQWQzcDFmM2IrUytJVWNFOXUxaytIOGVJeFRD\ndVNFQjhnQktzKyt1WitFNm8xNHJyRDNRNkM0YllFCkZZYTJPc2ZqZ2dENkw0N3ZjRGk5RkhJVFhy\nQ2Nsd0RuR0Q4MTBtYzY3bjEydTFML2hMdFdMVDJsd3paQmdWc0YKYXpMZzE1Qi96WVlWR0JLM3Zr\nd2ZQL1FXT3crRnBKUnJoVThsZ2x6ZFZEdEhQUGZTUFNId0k1Vmg5ZlNza0h0bQo4SHYxbC9DdExo\neGVWS3lPVXJVTmlFRmoyRDU1UnhkYkl0VWg4d1ptWVZUZExEZXJoQW5UcEEyWEpwOVRQeHlhCisw\ndURmRFlndk9EMDFOMEo1NUVSRndoNm5xekpVemlBVi80UnZmQkN2V2h3QTFocnkzOEJMUDVhZElO\nUVpqUjgKNko0Yk5TSGo5NHpibEsvRnBiYzhObUdGM3B2NHV3PT0KLS0tLS1FTkQgUFJJVkFURSBL\nRVktLS0tLQo=\n')
        BPU = license_client.encrypt(b'LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJRUlqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0JB\nOEFNSUlFQ2dLQ0JBRUF3LzBQRnB6Ri9GTUcvQ1g0ZkRESQp4bkNtTW8yMVVKVjdUc2hUSzM3WVF5\nYzlKejBmMmQ5OEpZbHJ2czVVZWtRTURTRkxWMG9veFpWRDMrU1BYZm9ECmN6ZWNaL3BpaVUyNUpt\naE1pc0I5SXJkbFJpbUhpekN1ajhjOWVZNUx2Y0RNMG5WUFBBUG45bitVbkpHTkpyZkEKSGVVWXlm\nYUYwYmhqOW1FN0JNZTVaRVhYT0dqRmtlWDM2ejhpd3VKVWdxQkE0QmxKZW1OZS9icWF0SHA1K1B5\nZQpjODdHS09Qb3JqK2RZaUU4RURaUUw2WUNENlE5ZTF0bndTcVJWZGhXbmdhd05Ua01oYVUvejQw\nV0cxaGNCaElGCitUSy9oU0tWSFRsckN2alAvRmFVaHc1NVN0ZXpSd004dU13QVBZRzRBN0haQklV\nLzl4N2l0a2d1SjB6ZWh5RUQKTXByalREN1cxNDVvWVBMWExQcmFBeGZPVExWa1l3ME0xN2crZ3lS\nMkFybXZHQ0NzcCt6bTkxM1MyZHgwN0VzYwpIeXFvRHA1ZFUxM1RBb2pxWjZ4QjNHWXFFYWQ1SFdG\nYXdJUWs0WitZenloUWZ0RmgzYjdJSURza1ZkRDBXLzhaCmcwd0FkdG1SMXRKMHhkVFNERFhZaG41\nVys0d3oyTFV0L1JkV2NxbGRpUFZIRXhabk90T3o5ZzltSHphNUJLTDMKU3R0VXZSUEZaQUhmYm9N\nUjhsVmJ4b25qMzFGRWhMS2VsUFpoMnNOZVA3dmxoUUtKdjlSdXdUbG9PcHhtb1lSVgpFMWVwNWpO\ncW1tbXJJNkRERTVSUmRIUmZ4R1ppbHNNTzZqVGtHclQ3aUtyM0VpTlpVcGJrNHZkNFhXc084NC9q\nCk5abFExQlF4OElBQm9nV2hYd05yTXBUYi9PYnBoYXhKVWdJNlo4dXhvMXozczhSeUsxVTN0elZm\nMTVkQWxSNUoKN0VTWE5PNkhKcCszRlFUc3EvZXFPcktORE81SVU0ZUc1SDErTHNpbEh0RlRiaEpi\nSjY5YllyOXRNb1lrSGtBWgpGRDIxTDBhMzNpdlM0bEVjUnhqVmhsbEJaZWtTMnNEVkxyNEJUUkJH\nL1ZxTUZoTmNPa1NpSEh2bDhaZGVJU1YvClpMUXpqM1prSVE3ejBZSWl4NTRwUDg0UllJQUlQMzhJ\nRUJKZzRWYWFRRUgzVjVCamcxdndDR01HdnJCTmd4NEoKUm5oUFhkNit0amlzZUtnc09vdHAzNVl3\nTkU3dTRreG5qZjd2Z2hkYlZ3Wk51NGVWQ2psdVZZVXlDWHJnNlVSdQpycjlMRnBoNHNZYTJ5MHlx\nUzE2Yk5FV2FaNjA2azgyNk9kbE1NRnpxYjluY3AvUEJLVEFBRWc3YmQ2TzJLUXB0ClJYcHZGRnNL\nUGdYMGY3b3pPUnh4WWtlTWNXWDhoeHRjM2xWWW1mS2pTZlFuaWZYUllINThObjV0MktJQ3oyYmIK\nK05jeW51SmVlb0d1akhMemd4MjZJVFJXb21OdzBsbUFoR09BcWdLUFBnTUIyYW5uL1J1RVgzZHVh\nWDNjQzIreQpHOXlQa3JRT2xMTW94OVpuRTJXZk1RaThlcmdYSmQzdi92RkxRKzlEVDNidk1yd3hT\nMnBkRmdXMTh3clhEa0ZHCm5SVVZvTFo5QnB0dnRPcFpCbldNT0p3SXVsakROZGxQRXErcjFQMklq\nU05tSmxPUm1TQkpsWkZ4ZGpDNERXYjEKclUxcTdhTW9KYzdlY2Y5cDZ3Q0dzY1RHeVlWNldOc2Fn\nd0xpaGtaNlhodVpFeE9lazJtZndLWG1kcTJqdzhIcgpsUUlEQVFBQgotLS0tLUVORCBQVUJMSUMg\nS0VZLS0tLS0K\n')

        loading_text.value = textLocaled('check_inet_loader_text')
        # tp.update()
        loading_text.update()

        if not is_online():
            loading_text.value = textLocaled('no_inet_loader_text')
            loading_text.update()
            progress_ring.color = ft.colors.YELLOW
            animate_ring(progress_ring, 0.8)
            exit_value.value = 1
            time.sleep(3.7)
            page.window_close()
            return 1

        try:
            generate_uid_file(license_client.decrypt(BPU), bytes(APP_VERSION, encoding='utf-8'))
        except license_client.UIDError:
            loading_text.value = textLocaled('no_uid_loader_text')
            loading_text.update()
            progress_ring.color = ft.colors.RED
            animate_ring(progress_ring, 0.8)
            exit_value.value = 1
            time.sleep(3.7)
            page.window_close()
            return 1

        loading_text.value = textLocaled('check_license_loader_text')
        # tp.update()
        loading_text.update()

        code_err, data_err, lic_type, date_now = open_license(license_client.decrypt(RPI), bytes(APP_VERSION, encoding='utf-8'), license_client.__spec__.origin)

        # from datetime import datetime
        # code_err, data_err, lic_type, date_now = 'J29dJ3ue87CV2987IUESNP1Phd83E3h', datetime.fromtimestamp(int(time.time())+49*60*60), 3, datetime.fromtimestamp(time.time())

        if code_err == 'J29dJ3ue87CV2987IUESNP1Phd83E3h':
            loading_text.value = textLocaled('activated_loader_text')
            loading_text.update()
            progress_ring.color = ft.colors.CYAN
            animate_ring(progress_ring, 0.8)
            hours_remain = round((data_err.timestamp() - time.time()) / 3600)
            if hours_remain < 48:
                dlg = ft.AlertDialog(
                    title=Text(f'{textLocaled("hours_remain_loader_text")}: {hours_remain}', color=ft.colors.RED)
                )
                page.open(dlg)
                time.sleep(2)
            time.sleep(0.5)
            data_err_value.value = bytes(format_datetime(data_err, locale=textLocaled.locale[:2]), encoding='utf')
            lic_type_value.value = lic_type
            exit_value.value = 0
        elif code_err == 0:
            loading_text.value = textLocaled('not_activated_loader_text')
            loading_text.update()
            progress_ring.color = ft.colors.RED_ACCENT
            exit_value.value = 1
            animate_ring(progress_ring, 0.8)
            time.sleep(3.7)
        elif code_err == -1:
            ################## DEPRECATED
            loading_text.value = f'Версии активированного клиента {APP_VERSION} и текущего {data_err} не соответствуют!'
            loading_text.update()
            progress_ring.color = ft.colors.YELLOW
            exit_value.value = 1
            animate_ring(progress_ring, 0.8)
            time.sleep(3.7)
        elif code_err == -2:
            loading_text.value = textLocaled('no_inet_loader_text')
            loading_text.update()
            progress_ring.color = ft.colors.RED
            exit_value.value = 1
            animate_ring(progress_ring, 0.8)
            time.sleep(3.7)
        elif code_err == -3:
            loading_text.value = textLocaled('no_check_duration_loader_text')
            loading_text.update()
            progress_ring.color = ft.colors.RED
            exit_value.value = 1
            animate_ring(progress_ring, 0.8)
            time.sleep(3.7)
        elif code_err == -4:
            loading_text.value = textLocaled('subscription_ended_loader_text')
            loading_text.update()
            progress_ring.color = ft.colors.YELLOW
            exit_value.value = 1
            animate_ring(progress_ring, 0.8)
            time.sleep(3.7)
        elif code_err == -5:
            loading_text.value = textLocaled('license_corrupted_loader_text')
            loading_text.update()
            progress_ring.color = ft.colors.RED
            exit_value.value = 1
            animate_ring(progress_ring, 0.8)
            time.sleep(3.7)
        page.window_close()
        return 1
    ft.app(target=loading)


def animate_ring(control, time, steps=100):
    step_time = time / steps
    x = -6

    for _ in IntervalTimer(step_time, stop=steps):
        control.value = 1 / (1 + math.e ** -x)
        control.update()
        x += 12 / steps
    control.value = 1
    control.update()


def main(page: Page):
    global data_err, lic_type

    page.window.center()
    page.window.title_bar_hidden = True
    page.window.min_width = 350
    page.window.min_height = 350

    page.fonts = {
        'Multiround': 'MultiroundPro.otf'
    }

    page.title = 'Microsoft Edge'
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.update()

    app = naim_configurator.NeuroFocusApp(page, data_err.value.decode(), APP_VERSION, lic_type.value)


def app_main():
    global data_err, exit_value, lic_type

    loading_app = Process(target=loading_target, args=(exit_value, data_err, lic_type))
    loading_app.start()
    loading_app.join()
    loading_app.kill()
    if exit_value.value == 0:
        ft.app(main)


if __name__ == '__main__':
    app_main()
