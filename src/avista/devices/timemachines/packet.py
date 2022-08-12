from construct import BitsInteger, Byte, BitStruct, BytesInteger, CString, Enum, PaddedString, Struct, Flag, Int8ub, Int16ub, Int32ub, Padding

import enum


FirmwareVersion = Struct(
    'major' / Int8ub,
    'minor' / Int8ub
)

DisplayedTime = Struct(
    'hour' / Int8ub,
    'minute' / Int8ub,
    'second' / Int8ub
)


class DisplayMode(enum.IntEnum):
    clock = 0
    count_up = 1
    count_down = 2,
    interval_up = 3
    interval_down = 4


Display = BitStruct(
    'mode' / Enum(BitsInteger(3), DisplayMode),
    Padding(2),
    'days' / Flag,
    'running' / Flag,
    'show_tenths' / Flag
)

CountdownAlarm = BitStruct(
    'duration' / BitsInteger(7),
    'checked' / Flag
)

QueryResponse = Struct(
    'device_type' / Byte,
    'ip_address' / Int32ub,
    'mac_address' / BytesInteger(6),
    'firmware_version' / FirmwareVersion,
    'sync_count' / Int16ub,
    'displayed_time' / DisplayedTime,
    'tenths_of_second' / Int8ub,
    'display' / Display,
    'countdown_alarm' / CountdownAlarm,
    'days_displayed' / Int8ub,
    Padding(1),  # It's not this but their wording is confusing
    'wireless_signal_strength' / Int8ub,
    'name' / PaddedString(16, 'utf-8')
)
