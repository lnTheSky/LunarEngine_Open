__all__ = []


def __dir__():
    return []


_USB_HID_CLASS_CTRL_bmRequestType = 0x21
_USB_HID_CLASS_CTRL_wValue_REPORT_TYPE_INPUT = 0x01 << 8
_USB_HID_CLASS_CTRL_wValue_REPORT_TYPE_OUTPUT = 0x02 << 8
_USB_HID_CLASS_CTRL_wValue_REPORT_TYPE_FEATURE = 0x03 << 8

_USB_CLASS_bmRequestType_GET_DESCRIPTOR = 0x81
_USB_CLASS_bRequest_GET_DESCRIPTOR = 6
_USB_CLASS_wValue_GET_HID_REPORT_DESCRIPTOR = 0x22 << 8

_USB_HID_CLASS_REPORT_DESCRIPTOR_TYPE = 0x22

_USAGE_WHEEL = 0x38
_USAGE_X = 0x30
_USAGE_Y = 0x31
_PAGE_BUTTON = 0x9


def get_mouse_descriptor(device):
    report_descriptor = None
    interface_num = 0

    cfg = device.get_active_configuration()

    for intf in cfg:
        desc_bytes = intf.extra_descriptors
        n_descriptors = desc_bytes[5]
        for d in range(n_descriptors):
            desc_type = desc_bytes[6 + (d * 3)]
            desc_length = desc_bytes[7 + (d * 3)] | (desc_bytes[8 + (d * 3)])
            if desc_type == _USB_HID_CLASS_REPORT_DESCRIPTOR_TYPE:
                report_descriptor = device.ctrl_transfer(_USB_CLASS_bmRequestType_GET_DESCRIPTOR,
                                                         _USB_CLASS_bRequest_GET_DESCRIPTOR,
                                                         _USB_CLASS_wValue_GET_HID_REPORT_DESCRIPTOR,
                                                         intf.bInterfaceNumber, desc_length)
                break

        if report_descriptor[3] == 2:
            interface_num = intf.bInterfaceNumber
            break

    return report_descriptor, interface_num


def get_device_interfaces(device):
    try:
        # intf_cnt = 0
        # cfg = device.get_active_configuration()
        # for i in cfg:
        #     intf_cnt += 1
        # return intf_cnt
        return device.bNumInterfaces
    except Exception as e:
        print(f'[Hid] [get_devices_interfaces] [F]: Unexpected error ({e})')
        return 0


def parse_hid_report(data, mouse):
    buttons = []
    x, y = 0, 0
    wheel = 0

    output = mouse.parse_input_report(data)

    for item in output:
        if item.usage == _USAGE_X and item.page != _PAGE_BUTTON:
            x = output[item].value
        elif item.usage == _USAGE_Y and item.page != _PAGE_BUTTON:
            y = output[item].value
        elif item.usage == _USAGE_WHEEL and item.page != _PAGE_BUTTON:
            wheel = output[item].value
        elif item.page == _PAGE_BUTTON:
            buttons.append(output[item].value)

    return x, y, buttons, wheel


def buttons2num(buttons: list[bool]):
    return int("".join([str(int(i)) for i in buttons[::-1]]), 2)


def num2buttons(num: int):
    buttons = list(map(lambda x: bool(int(x)), bin(num)[:1:-1]))
    return buttons + [False] * ((8 - len(buttons)) % 8)
