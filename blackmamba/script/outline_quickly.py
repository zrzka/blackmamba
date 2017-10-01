#!python3
"""
Script name ``outline_quickly.py``.

Shows source code outline. You can filter functions, ... by name. Use arrows key to
change selection and then hit ``Enter`` to scroll to the symbol.
"""

import editor
import ast
import os
from enum import Enum
from blackmamba.uikit.picker import PickerView, PickerItem, PickerDataSource
from ui import Image
import blackmamba.ide.source as source


class OutlineNodeItem(PickerItem):
    class Style(Enum):
        cls = 'class'
        fn = 'function'

    def __init__(self, style, name, line, column, level, breadcrumb):
        super().__init__('{}{}'.format(level * '    ', name),
                         '{} (line {})'.format(breadcrumb, line))
        self.style = style
        self.name = name
        self.line = line
        self.column = column
        self.level = level
        self.breadcrumb = breadcrumb
        self.image = Image(style.value)


class OutlineDataSource(PickerDataSource):
    def __init__(self, text, filename):
        super().__init__()

        r = ast.parse(text)
        self.items = OutlineDataSource._generate_nodes(r, breadcrumb=filename)

    @staticmethod
    def _generate_nodes(parent, level=0, breadcrumb=''):
        nodes = []

        for child in parent.body:
            if isinstance(child, ast.ClassDef):
                style = OutlineNodeItem.Style.cls
            elif isinstance(child, ast.FunctionDef):
                style = OutlineNodeItem.Style.fn
            else:
                style = None

            if style:
                node = OutlineNodeItem(style, child.name, child.lineno, child.col_offset, level, breadcrumb)
                nodes.append(node)
                if breadcrumb:
                    bc = '{} • {}'.format(breadcrumb, child.name)
                else:
                    bc = child.name
                child_nodes = OutlineDataSource._generate_nodes(child, level + 1, bc)
                if child_nodes:
                    nodes.extend(child_nodes)

        return nodes


def main():
    filename = editor.get_path()
    if not filename:
        return

    if not filename.endswith('.py'):
        return

    text = editor.get_text()
    if not text:
        return

    def scroll_to_node(node, shift_enter):
        source.scroll_to_line(node.line)

    v = PickerView()
    v.name = 'Outline'
    v.datasource = OutlineDataSource(text, os.path.basename(filename))
    v.shift_enter_enabled = False
    v.help_label.text = (
        '⇅ - select • Enter - scroll to location'
        '\n'
        'Esc - close • Cmd . - close with Apple smart keyboard'
    )
    v.textfield.placeholder = 'Start typing to filter nodes...'
    v.did_select_item_action = scroll_to_node
    v.present('sheet')
    v.wait_modal()


if __name__ == '__main__':
    main()
