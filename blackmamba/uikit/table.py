#!python3

from enum import Enum


class UITableViewCellStyle(str, Enum):
    default = 'default'
    subtitle = 'subtitle'
    value1 = 'value1'
    value2 = 'value2'
